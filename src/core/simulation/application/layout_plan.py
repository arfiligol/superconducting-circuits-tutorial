"""Explicit layout planning layer between CircuitIR and Schemdraw rendering."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import pairwise

from core.simulation.domain.circuit import CircuitDefinition
from core.simulation.domain.ir import CircuitElement, CircuitIR


@dataclass(frozen=True)
class LayoutPlan:
    """Stable preview layout contract derived from CircuitIR."""

    circuit_ir: CircuitIR
    layout_mode: str
    dx: float
    gap: float
    elements: tuple[CircuitElement, ...]
    shunt_cluster_metadata: dict[int, tuple[str, int, int]]
    shunt_branch_offsets: dict[int, float]
    signal_node_padding: dict[str, tuple[float, float]]
    backbone_positions: dict[str, float] | None

    @property
    def use_backbone_layout(self) -> bool:
        return self.backbone_positions is not None


def component_label_parts(
    circuit: CircuitDefinition,
    component_name: str,
    component_kind: str,
    value_ref: str | int,
) -> tuple[str, str | None]:
    """Build display-friendly label parts: component id + optional value/unit."""
    if component_kind == "port":
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
    return CircuitDefinition.is_ground_node(node_str)


def _classify_layout_mode(circuit_ir: CircuitIR) -> str:
    """Return a coarse layout profile for domain-specific spacing heuristics."""
    if circuit_ir.layout_profile == "jtwpa":
        return "jtwpa_like"
    if circuit_ir.layout_profile == "jpa":
        return "jpa_like"
    return "generic"


def _build_shunt_cluster_metadata(
    elements: tuple[CircuitElement, ...],
) -> dict[int, tuple[str, int, int]]:
    """Map topology index to (signal_node, cluster_index, cluster_total) for shunt branches."""
    shunt_indices_by_node: dict[str, list[int]] = defaultdict(list)

    for index, element in enumerate(elements):
        node1_str = element.node1
        node2_str = element.node2
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


def _estimate_component_slot_width(
    component_kind: str,
    name_label: str,
    value_label: str | None,
    layout_mode: str,
) -> float:
    """Estimate horizontal space a shunt branch should reserve around its anchor."""
    longest_label = max(len(name_label), len(value_label or ""))
    label_span = max(1.2, (0.16 * longest_label) + 0.9)
    symbol_span = 1.35

    if component_kind == "port":
        symbol_span = 1.8
    elif component_kind == "resistor":
        symbol_span = 1.5
    elif component_kind == "josephson_junction":
        symbol_span = 1.55
    elif component_kind == "capacitor":
        symbol_span = 1.35
    elif component_kind == "inductor":
        symbol_span = 1.45

    slot_width = max(symbol_span, label_span)
    if value_label:
        slot_width += 0.3
    if layout_mode == "jtwpa_like":
        slot_width += 0.2
    elif layout_mode == "jpa_like":
        slot_width += 0.1
    return slot_width


def _build_shunt_branch_offsets(
    circuit: CircuitDefinition,
    elements: tuple[CircuitElement, ...],
    layout_mode: str,
) -> dict[int, float]:
    """Reserve horizontal slots for each shunt branch to avoid label crowding."""
    shunt_indices_by_node: dict[str, list[int]] = defaultdict(list)

    for index, element in enumerate(elements):
        node1_str = element.node1
        node2_str = element.node2
        is_gnd1 = _is_ground(node1_str)
        is_gnd2 = _is_ground(node2_str)
        if is_gnd1 == is_gnd2:
            continue

        signal_node = node2_str if is_gnd1 else node1_str
        shunt_indices_by_node[signal_node].append(index)

    branch_offsets: dict[int, float] = {}
    inter_slot_gap = 0.4
    if layout_mode == "jpa_like":
        inter_slot_gap = 0.5
    elif layout_mode == "jtwpa_like":
        inter_slot_gap = 0.6

    for indices in shunt_indices_by_node.values():
        if len(indices) <= 1:
            branch_offsets[indices[0]] = 0.0
            continue

        slot_widths: list[float] = []
        for topo_index in indices:
            lowered = elements[topo_index]
            name_label, value_label = component_label_parts(
                circuit,
                lowered.name,
                lowered.kind,
                lowered.value_ref,
            )
            slot_widths.append(
                _estimate_component_slot_width(
                    component_kind=lowered.kind,
                    name_label=name_label,
                    value_label=value_label,
                    layout_mode=layout_mode,
                )
            )

        total_width = sum(slot_widths) + (inter_slot_gap * (len(indices) - 1))
        cursor = -total_width / 2.0
        for topo_index, slot_width in zip(indices, slot_widths, strict=False):
            cursor += slot_width / 2.0
            branch_offsets[topo_index] = cursor
            cursor += (slot_width / 2.0) + inter_slot_gap

    return branch_offsets


def _build_signal_node_padding(
    shunt_cluster_metadata: dict[int, tuple[str, int, int]],
    shunt_branch_offsets: dict[int, float],
) -> dict[str, tuple[float, float]]:
    """Estimate left/right horizontal padding needed around each signal node."""
    node_padding: dict[str, tuple[float, float]] = {}
    branch_margin = 0.4

    for topo_index, (signal_node, _, _) in shunt_cluster_metadata.items():
        offset = shunt_branch_offsets.get(topo_index, 0.0)
        left_pad, right_pad = node_padding.get(signal_node, (0.0, 0.0))

        if offset < 0.0:
            left_pad = max(left_pad, abs(offset) + branch_margin)
        elif offset > 0.0:
            right_pad = max(right_pad, offset + branch_margin)
        else:
            left_pad = max(left_pad, branch_margin)
            right_pad = max(right_pad, branch_margin)

        node_padding[signal_node] = (left_pad, right_pad)

    return node_padding


def _build_backbone_positions(
    elements: tuple[CircuitElement, ...],
    dx: float,
    origin_x: float = 1.8,
    node_padding: dict[str, tuple[float, float]] | None = None,
) -> dict[str, float] | None:
    """Return fixed x positions for simple chain-like signal backbones."""
    adjacency: dict[str, list[str]] = defaultdict(list)
    signal_nodes: set[str] = set()
    port_signal_nodes: list[str] = []

    for element in elements:
        node1_str = element.node1
        node2_str = element.node2
        is_gnd1 = _is_ground(node1_str)
        is_gnd2 = _is_ground(node2_str)

        if is_gnd1 != is_gnd2 and element.kind == "port":
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
                node for node in adjacency[current] if node != previous and node not in visited
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

    if not order:
        return None

    positions: dict[str, float] = {order[0]: origin_x}
    padding_by_node = node_padding or {}
    spacing_scale = 0.7

    for previous_node, current_node in pairwise(order):
        previous_right = padding_by_node.get(previous_node, (0.0, 0.0))[1]
        current_left = padding_by_node.get(current_node, (0.0, 0.0))[0]
        segment_dx = dx + (spacing_scale * (previous_right + current_left))
        positions[current_node] = positions[previous_node] + segment_dx

    return positions


def build_layout_plan(
    circuit: CircuitDefinition,
    circuit_ir: CircuitIR | None = None,
) -> LayoutPlan:
    """Compile stable preview layout metadata from CircuitIR."""
    compiled_ir = circuit_ir or circuit.to_ir()
    layout_mode = _classify_layout_mode(compiled_ir)

    if layout_mode == "jtwpa_like":
        dx = 3.4
        gap = 2.3
    elif layout_mode == "jpa_like":
        dx = 3.2
        gap = 2.2
    else:
        dx = 3.0
        gap = 2.0

    elements = compiled_ir.elements
    shunt_cluster_metadata = _build_shunt_cluster_metadata(elements)
    shunt_branch_offsets = _build_shunt_branch_offsets(circuit, elements, layout_mode)
    signal_node_padding = _build_signal_node_padding(
        shunt_cluster_metadata,
        shunt_branch_offsets,
    )
    backbone_positions = _build_backbone_positions(
        elements,
        dx=dx,
        node_padding=signal_node_padding,
    )

    return LayoutPlan(
        circuit_ir=compiled_ir,
        layout_mode=layout_mode,
        dx=dx,
        gap=gap,
        elements=elements,
        shunt_cluster_metadata=shunt_cluster_metadata,
        shunt_branch_offsets=shunt_branch_offsets,
        signal_node_padding=signal_node_padding,
        backbone_positions=backbone_positions,
    )
