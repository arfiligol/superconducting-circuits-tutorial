"""
Circuit Visualizer using Schemdraw.

This module provides functionality to convert a CircuitDefinition
into an SVG string using the Schemdraw library.
"""

import re

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

    # Vertical branches are denser; split name/value on opposite sides.
    if is_shunt:
        stacked_label = name_label if not value_label else f"{name_label}\n{value_label}"
        if name_lower.startswith("c"):
            # For vertical capacitors, `loc='top'` maps to the visual left side.
            return element.label(stacked_label, loc="top", ofst=0.35, halign="right", fontsize=11)
        # For other vertical elements, `loc='bottom'` maps to the visual right side.
        return element.label(stacked_label, loc="bottom", ofst=0.35, halign="left", fontsize=11)

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
    x_pos = 0.0
    dx = 3.0
    gap = 2.0

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

    for comp_name, node1_raw, node2_raw, value_ref in circuit.topology:
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

        is_gnd1 = node1_str.lower() in ["0", "gnd"]
        is_gnd2 = node2_str.lower() in ["0", "gnd"]

        y1 = 0.0 if is_gnd1 else 3.0
        y2 = 0.0 if is_gnd2 else 3.0
        is_shunt = y1 != y2

        if is_shunt:
            signal_node = node1_str if not is_gnd1 else node2_str

            if tip_node_top is not None and tip_node_top != signal_node:
                x_pos += gap

            x = x_pos
            if isinstance(element, elm.Dot):
                d.add(element.at((x, 1.5)))
            else:
                d.add(
                    _label_element(
                        element.at((x, 0.0)).to((x, 3.0)),
                        comp_name,
                        name_label,
                        value_label,
                        is_shunt=True,
                    )
                )

            wire_ground(x)

            should_label_nodes = not name_lower.startswith("p")

            if should_label_nodes and node1_str not in labeled_nodes:
                loc1 = "top" if y1 > y2 else "bottom"
                d.add(elm.Label().at((x, y1)).label(node1_str, loc=loc1, color="gray", fontsize=8))
                labeled_nodes.add(node1_str)
            if should_label_nodes and node2_str not in labeled_nodes:
                loc2 = "bottom" if y1 > y2 else "top"
                d.add(elm.Label().at((x, y2)).label(node2_str, loc=loc2, color="gray", fontsize=8))
                labeled_nodes.add(node2_str)

            wire_node(signal_node, x, 3.0)
            tip_node_top = signal_node
            x_pos = x + gap
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

        if tip_node_top is not None and tip_node_top != node1_str:
            x_pos += gap

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

        if node1_str not in labeled_nodes:
            loc1 = "left" if x1 < x2 else "right"
            d.add(elm.Label().at((x1, 3.0)).label(node1_str, loc=loc1, color="gray", fontsize=8))
            labeled_nodes.add(node1_str)
        if node2_str not in labeled_nodes:
            loc2 = "right" if x1 < x2 else "left"
            d.add(elm.Label().at((x2, 3.0)).label(node2_str, loc=loc2, color="gray", fontsize=8))
            labeled_nodes.add(node2_str)

        wire_node(node1_str, x1, 3.0)
        wire_node(node2_str, x2, 3.0)

        tip_node_top = node2_str
        x_pos = x2

    svg_bytes = d.get_imagedata("svg")
    return _add_svg_padding(svg_bytes.decode("utf-8"))
