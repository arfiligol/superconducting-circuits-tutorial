"""
Circuit Visualizer using Schemdraw.

This module provides functionality to convert a CircuitDefinition
into an SVG string using the Schemdraw library.
"""

import re
from collections import defaultdict

import schemdraw
import schemdraw.elements as elm

from core.simulation.domain.circuit import CircuitDefinition

_SVG_VIEWBOX_PATTERN = re.compile(
    r'height="([0-9.eE+-]+)pt"\s+width="([0-9.eE+-]+)pt"\s+'
    r'viewBox="([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)"'
)


def _add_svg_padding(svg_text: str, pad_pt: float = 12.0) -> str:
    """Expand SVG viewBox/size to prevent edge clipping of strokes and labels."""
    match = _SVG_VIEWBOX_PATTERN.search(svg_text)
    if match is None:
        return svg_text

    height = float(match.group(1))
    width = float(match.group(2))
    x0 = float(match.group(3))
    y0 = float(match.group(4))
    view_w = float(match.group(5))
    view_h = float(match.group(6))

    replacement = (
        f'height="{height + 2 * pad_pt}pt" '
        f'width="{width + 2 * pad_pt}pt" '
        f'viewBox="{x0 - pad_pt} {y0 - pad_pt} {view_w + 2 * pad_pt} {view_h + 2 * pad_pt}"'
    )
    return _SVG_VIEWBOX_PATTERN.sub(replacement, svg_text, count=1)


def _component_label_parts(
    circuit: CircuitDefinition, component_name: str, value_ref: str | int
) -> tuple[str, str | None]:
    """Build display-friendly label parts: component id + optional value/unit."""
    if component_name.lower().startswith("p"):
        return component_name, None
    if not isinstance(value_ref, str):
        return component_name, None

    parameter = circuit.parameters.get(value_ref)
    if parameter is None:
        return component_name, None

    value_str = f"{parameter.default:g}"
    return component_name, f"{value_str} {parameter.unit}"


def _is_ground(node_str: str) -> bool:
    """Return True when a topology node represents the ground reference."""
    return node_str.lower() in ["0", "gnd"]


def _classify_layout_mode(circuit: CircuitDefinition) -> str:
    """Return a coarse layout profile for domain-specific spacing heuristics."""
    series_inductive = 0
    shunt_capacitive = 0
    shunt_josephson = 0
    port_count = 0

    for comp_name, node1_raw, node2_raw, _ in circuit.topology:
        name_lower = comp_name.lower()
        node1_str = str(node1_raw)
        node2_str = str(node2_raw)
        is_shunt = _is_ground(node1_str) ^ _is_ground(node2_str)

        if name_lower.startswith("p"):
            port_count += 1
        if not is_shunt:
            if name_lower.startswith("l") or name_lower.startswith("lj"):
                series_inductive += 1
            continue

        if name_lower.startswith("c"):
            shunt_capacitive += 1
        if name_lower.startswith("lj"):
            shunt_josephson += 1

    if series_inductive >= 3 and shunt_capacitive >= 2:
        return "jtwpa_like"
    if port_count >= 1 and shunt_capacitive >= 1 and shunt_josephson >= 1:
        return "jpa_like"
    return "generic"


def _build_shunt_cluster_metadata(circuit: CircuitDefinition) -> dict[int, tuple[str, int, int]]:
    """Map topology index to (signal_node, cluster_index, cluster_total) for shunt branches."""
    shunt_indices_by_node: dict[str, list[int]] = defaultdict(list)

    for index, (_, node1_raw, node2_raw, _) in enumerate(circuit.topology):
        node1_str = str(node1_raw)
        node2_str = str(node2_raw)
        is_gnd1 = _is_ground(node1_str)
        is_gnd2 = _is_ground(node2_str)
        if is_gnd1 == is_gnd2:
            continue

        signal_node = node2_str if is_gnd1 else node1_str
        shunt_indices_by_node[signal_node].append(index)

    metadata: dict[int, tuple[str, int, int]] = {}
    for signal_node, indices in shunt_indices_by_node.items():
        total = len(indices)
        for cluster_index, topo_index in enumerate(indices):
            metadata[topo_index] = (signal_node, cluster_index, total)
    return metadata


def _build_backbone_positions(
    circuit: CircuitDefinition, dx: float, origin_x: float = 1.8
) -> dict[str, float] | None:
    """Return fixed x positions for simple chain-like signal backbones."""
    adjacency: dict[str, list[str]] = defaultdict(list)
    signal_nodes: set[str] = set()
    port_signal_nodes: list[str] = []

    for comp_name, node1_raw, node2_raw, _ in circuit.topology:
        node1_str = str(node1_raw)
        node2_str = str(node2_raw)
        is_gnd1 = _is_ground(node1_str)
        is_gnd2 = _is_ground(node2_str)

        if is_gnd1 != is_gnd2 and comp_name.lower().startswith("p"):
            port_signal_nodes.append(node2_str if is_gnd1 else node1_str)

        if is_gnd1 or is_gnd2:
            signal_nodes.add(node2_str if is_gnd1 else node1_str)
            continue

        signal_nodes.update([node1_str, node2_str])
        adjacency[node1_str].append(node2_str)
        adjacency[node2_str].append(node1_str)

    if not signal_nodes:
        return None

    if any(len(neighbors) > 2 for neighbors in adjacency.values()):
        return None

    if adjacency:
        endpoints = sorted(node for node, neighbors in adjacency.items() if len(neighbors) <= 1)
        start_node = next(
            (node for node in port_signal_nodes if node in adjacency and len(adjacency[node]) <= 1),
            None,
        )
        if start_node is None:
            start_node = endpoints[0] if endpoints else sorted(adjacency)[0]

        order: list[str] = []
        visited: set[str] = set()
        previous: str | None = None
        current = start_node

        while current not in visited:
            order.append(current)
            visited.add(current)
            next_candidates = [
                node
                for node in adjacency[current]
                if node != previous and node not in visited
            ]
            if not next_candidates:
                break
            previous, current = current, next_candidates[0]

        if len(visited) != len(adjacency):
            return None
    else:
        order = sorted(signal_nodes)

    missing_signal_nodes = [node for node in sorted(signal_nodes) if node not in order]
    order.extend(missing_signal_nodes)

    return {node: origin_x + index * dx for index, node in enumerate(order)}


def _shunt_branch_offset(
    comp_name: str, cluster_index: int, cluster_total: int, layout_mode: str
) -> float:
    """Return x offset from the signal-node anchor for a shunt branch."""
    if cluster_total <= 1:
        return 0.0

    centered_index = cluster_index - ((cluster_total - 1) / 2.0)
    step = 1.35 if layout_mode == "jtwpa_like" else 1.2
    offset = centered_index * step

    if comp_name.lower().startswith("p") and offset >= -0.25:
        offset -= 0.55
    return offset


def _shunt_label_plan(
    comp_name: str, cluster_index: int, cluster_total: int, layout_mode: str
) -> tuple[str, float, float, float]:
    """Return side, x offset, name y, value y for vertical-branch labels."""
    if cluster_total <= 1:
        if comp_name.lower().startswith("c"):
            return ("left", -0.78, 1.95, 1.05)
        return ("right", 0.82, 1.95, 1.05)

    split_at = (cluster_total + 1) // 2
    side = "left" if cluster_index < split_at else "right"
    edge_rank = cluster_index if side == "left" else (cluster_total - 1 - cluster_index)

    base_offset = 1.05 + (0.12 if layout_mode == "jtwpa_like" else 0.0)
    x_offset = base_offset + 0.36 * edge_rank
    if side == "left":
        x_offset *= -1.0

    return (side, x_offset, 1.82, 1.12)


def _ensure_node_label(
    drawing: schemdraw.Drawing,
    labeled_nodes: set[str],
    node_str: str,
    x: float,
    y: float,
    loc: str,
) -> None:
    """Render each node label at most once."""
    if node_str in labeled_nodes:
        return
    drawing.add(elm.Label().at((x, y)).label(node_str, loc=loc, color="gray", fontsize=8))
    labeled_nodes.add(node_str)


def _add_shunt_labels(
    drawing: schemdraw.Drawing,
    x: float,
    comp_name: str,
    name_label: str,
    value_label: str | None,
    cluster_index: int,
    cluster_total: int,
    layout_mode: str,
) -> None:
    """Place shunt labels with cluster-aware offsets to reduce overlap."""
    side, x_offset, name_y, value_y = _shunt_label_plan(
        comp_name=comp_name,
        cluster_index=cluster_index,
        cluster_total=cluster_total,
        layout_mode=layout_mode,
    )
    halign = "right" if side == "left" else "left"

    drawing.add(
        elm.Label()
        .at((x + x_offset, name_y))
        .label(name_label, loc="center", fontsize=11, halign=halign)
    )
    if value_label:
        drawing.add(
            elm.Label()
            .at((x + x_offset, value_y))
            .label(value_label, loc="center", fontsize=10, halign=halign)
        )


def _label_element(
    element,
    comp_name: str,
    name_label: str,
    value_label: str | None,
    is_shunt: bool,
):
    """Attach label with type-aware defaults to avoid overlaps."""
    name_lower = comp_name.lower()
    if isinstance(element, elm.Dot):
        return element.label(name_label, loc="top", fontsize=11)

    # Port sources need extra room from nearby shunt elements.
    if name_lower.startswith("p"):
        return element.label(name_label, loc="right", ofst=0.45, halign="left", fontsize=11)

    # Dense shunt branches are handled by cluster-aware absolute labels.
    if is_shunt:
        return element

    # Series path labels sit above/below the line for readability.
    element.label(name_label, loc="top", ofst=0.32, fontsize=11)
    if value_label:
        element.label(value_label, loc="bottom", ofst=0.28, fontsize=10)
    return element


def generate_circuit_svg(circuit: CircuitDefinition) -> str:
    """
    Generate an SVG string representation of a CircuitDefinition.

    This uses a simple layout heuristic to draw the components.

    Args:
        circuit: The circuit definition to visualize.

    Returns:
        A string containing the raw SVG data.
    """
    # SVG backend scales with drawing extents naturally and avoids matplotlib figure accumulation.
    d = schemdraw.Drawing(canvas="svg", show=False)
    layout_mode = _classify_layout_mode(circuit)

    x_pos = 0.0
    if layout_mode == "jtwpa_like":
        dx = 3.4
        gap = 2.3
    elif layout_mode == "jpa_like":
        dx = 3.2
        gap = 2.2
    else:
        dx = 3.0
        gap = 2.0

    shunt_cluster_metadata = _build_shunt_cluster_metadata(circuit)
    backbone_positions = _build_backbone_positions(circuit, dx=dx)
    use_backbone_layout = backbone_positions is not None

    node_latest_x: dict[str, float] = {}
    node_bridge_y: dict[str, float] = {}
    tip_node_top = None
    next_bridge_y = 4.5
    labeled_nodes: set[str] = set()

    def wire_node(node_str: str, target_x: float, target_y: float) -> None:
        nonlocal next_bridge_y
        if node_str in node_latest_x:
            prev_x = node_latest_x[node_str]
            dist = abs(target_x - prev_x)
            if dist > 2.0:
                # Reuse one bridge lane per node to keep the same net visually coherent.
                bridge_y = node_bridge_y.get(node_str)
                if bridge_y is None:
                    bridge_y = next_bridge_y
                    node_bridge_y[node_str] = bridge_y
                    next_bridge_y += 0.6

                d.add(elm.Line().at((prev_x, target_y)).to((prev_x, bridge_y)))
                d.add(elm.Line().at((prev_x, bridge_y)).to((target_x, bridge_y)))
                d.add(elm.Line().at((target_x, bridge_y)).to((target_x, target_y)))
            elif dist > 0.1:
                d.add(elm.Line().at((prev_x, target_y)).to((target_x, target_y)))

        node_latest_x[node_str] = max(node_latest_x.get(node_str, 0.0), target_x)

    last_ground_x: float | None = None
    ground_drawn = False

    def wire_ground(target_x: float) -> None:
        nonlocal last_ground_x, ground_drawn
        if not ground_drawn:
            d.add(elm.Ground().at((target_x, 0.0)))
            ground_drawn = True

        if last_ground_x is not None:
            dist = abs(target_x - last_ground_x)
            if dist > 0.1:
                d.add(elm.Line().at((last_ground_x, 0.0)).to((target_x, 0.0)))
        last_ground_x = target_x

    for topo_index, (comp_name, node1_raw, node2_raw, value_ref) in enumerate(circuit.topology):
        name_lower = comp_name.lower()
        node1_str = str(node1_raw)
        node2_str = str(node2_raw)
        name_label, value_label = _component_label_parts(circuit, comp_name, value_ref)

        if name_lower.startswith("p"):
            element = elm.SourceSin()
        elif name_lower.startswith("c"):
            element = elm.Capacitor()
        elif name_lower.startswith("l") and not name_lower.startswith("lj"):
            element = elm.Inductor()
        elif name_lower.startswith("r"):
            element = elm.Resistor()
        elif name_lower.startswith("lj"):
            element = elm.Josephson()
        elif name_lower.startswith("k"):
            element = elm.Dot(open=True).label(f"K({comp_name})")
        else:
            element = elm.Dot(open=True).label(f"? {comp_name}")

        is_gnd1 = _is_ground(node1_str)
        is_gnd2 = _is_ground(node2_str)

        y1 = 0.0 if is_gnd1 else 3.0
        y2 = 0.0 if is_gnd2 else 3.0
        is_shunt = y1 != y2

        if is_shunt:
            signal_node, cluster_index, cluster_total = shunt_cluster_metadata.get(
                topo_index, (node1_str if not is_gnd1 else node2_str, 0, 1)
            )

            if use_backbone_layout:
                node_anchor_x = backbone_positions[signal_node]
                branch_x = node_anchor_x + _shunt_branch_offset(
                    comp_name=comp_name,
                    cluster_index=cluster_index,
                    cluster_total=cluster_total,
                    layout_mode=layout_mode,
                )
            else:
                node_anchor_x = x_pos
                branch_x = x_pos

            if not use_backbone_layout and tip_node_top is not None and tip_node_top != signal_node:
                x_pos += gap

            x = branch_x
            if isinstance(element, elm.Dot):
                d.add(element.at((x, 1.5)))
            else:
                d.add(
                    _label_element(
                        element.at((x, 0.0)).to((x, 3.0)),
                        comp_name,
                        name_label,
                        value_label,
                        True,
                    )
                )
                if not name_lower.startswith("p"):
                    _add_shunt_labels(
                        drawing=d,
                        x=x,
                        comp_name=comp_name,
                        name_label=name_label,
                        value_label=value_label,
                        cluster_index=cluster_index,
                        cluster_total=cluster_total,
                        layout_mode=layout_mode,
                    )

            if use_backbone_layout and abs(branch_x - node_anchor_x) > 0.1:
                d.add(elm.Line().at((node_anchor_x, 3.0)).to((branch_x, 3.0)))

            wire_ground(x)

            should_label_nodes = not name_lower.startswith("p")

            if should_label_nodes:
                loc1 = "top" if y1 > y2 else "bottom"
                loc2 = "bottom" if y1 > y2 else "top"
                label_x1 = node_anchor_x if not is_gnd1 else x
                label_x2 = node_anchor_x if not is_gnd2 else x
                _ensure_node_label(d, labeled_nodes, node1_str, label_x1, y1, loc1)
                _ensure_node_label(d, labeled_nodes, node2_str, label_x2, y2, loc2)

            if use_backbone_layout:
                node_latest_x[signal_node] = node_anchor_x
            else:
                wire_node(signal_node, x, 3.0)
            tip_node_top = signal_node
            if not use_backbone_layout:
                dense_cluster_pitch = gap
                if cluster_total > 1:
                    dense_cluster_pitch += 0.7 + 0.25 * min(cluster_total - 1, 3)
                x_pos = x + dense_cluster_pitch
            continue

        if is_gnd1 and is_gnd2:
            if tip_node_top is not None:
                x_pos += gap
            x1 = x_pos
            x2 = x_pos + dx
            wire_ground(x1)
            wire_ground(x2)
            x_pos = x2
            continue

        if not use_backbone_layout and tip_node_top is not None and tip_node_top != node1_str:
            x_pos += gap

        if use_backbone_layout:
            x1 = backbone_positions.get(node1_str)
            x2 = backbone_positions.get(node2_str)
            if x1 is None or x2 is None:
                x1 = x_pos
                x2 = x_pos + dx
        else:
            x1 = x_pos
            x2 = x_pos + dx

        if isinstance(element, elm.Dot):
            d.add(element.at(((x1 + x2) / 2, 3.0)))
        else:
            d.add(
                _label_element(
                    element.at((x1, 3.0)).to((x2, 3.0)),
                    comp_name,
                    name_label,
                    value_label,
                    is_shunt=False,
                )
            )

        loc1 = "left" if x1 < x2 else "right"
        loc2 = "right" if x1 < x2 else "left"
        _ensure_node_label(d, labeled_nodes, node1_str, x1, 3.0, loc1)
        _ensure_node_label(d, labeled_nodes, node2_str, x2, 3.0, loc2)

        if use_backbone_layout:
            node_latest_x[node1_str] = x1
            node_latest_x[node2_str] = x2
        else:
            wire_node(node1_str, x1, 3.0)
            wire_node(node2_str, x2, 3.0)

        tip_node_top = node2_str
        if not use_backbone_layout:
            x_pos = x2

    svg_bytes = d.get_imagedata("svg")
    return _add_svg_padding(svg_bytes.decode("utf-8"))
