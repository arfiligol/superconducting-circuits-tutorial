"""Tests for the circuit visualizer application."""

import re

from core.simulation.application.circuit_visualizer import (
    _add_svg_padding,
    _boxes_overlap,
    _build_backbone_positions,
    _build_shunt_branch_offsets,
    _build_signal_node_padding,
    _classify_layout_mode,
    _estimate_component_slot_width,
    _parallel_branch_y,
    _resolve_shunt_label_layout,
    _shunt_branch_offset,
    _shunt_label_plan,
    generate_circuit_svg,
)
from core.simulation.application.layout_plan import build_layout_plan
from core.simulation.domain.circuit import CircuitDefinition, parse_circuit_definition_source


def _circuit(*, name: str, parameters: dict, topology: list[tuple]):
    components: list[dict[str, object]] = []
    seen_component_refs: set[str] = set()
    normalized_topology: list[tuple[str, str, str, str | int]] = []

    for element_name, node1, node2, value_ref in topology:
        element_name_text = str(element_name)
        if element_name_text.lower().startswith("p"):
            normalized_topology.append((element_name_text, str(node1), str(node2), int(value_ref)))
            continue

        component_ref = str(value_ref)
        if component_ref not in seen_component_refs:
            parameter = parameters[component_ref]
            components.append(
                {
                    "name": component_ref,
                    "default": float(parameter["default"]),
                    "unit": str(parameter["unit"]),
                }
            )
            seen_component_refs.add(component_ref)
        normalized_topology.append((element_name_text, str(node1), str(node2), component_ref))

    return parse_circuit_definition_source(
        {
            "name": name,
            "components": components,
            "topology": normalized_topology,
        }
    )


_legacy_circuit = _circuit


def test_generate_circuit_svg_basic():
    """Test that a basic circuit can be converted to an SVG string."""
    circuit = _circuit(
        name="Test Circuit",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1": {"default": 10.0, "unit": "nH"},
            "C1": {"default": 1.0, "unit": "pF"},
            "Lj1": {"default": 0.3, "unit": "nH"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
            ("L1", "1", "2", "L1"),
            ("C1", "2", "0", "C1"),
            ("Lj1", "2", "3", "Lj1"),
        ],
    )

    svg_str = generate_circuit_svg(circuit)

    # Verify it returns a string
    assert isinstance(svg_str, str)

    # Verify it looks like an SVG
    assert svg_str.lstrip().startswith(("<?xml", "<svg"))
    assert "<svg" in svg_str
    assert "</svg>" in svg_str

    # Check that component labels might be in the SVG (schemdraw SVG output includes text tags)
    assert "P1" in svg_str
    assert "R50" in svg_str
    assert "L1" in svg_str
    assert "C1" in svg_str
    assert "Lj1" in svg_str


def test_build_layout_plan_exposes_explicit_backbone_contract():
    """Layout planning should materialize an explicit contract before rendering."""
    circuit = _circuit(
        name="Planned Circuit",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1": {"default": 10.0, "unit": "nH"},
            "C1": {"default": 1.0, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R1", "1", "0", "R50"),
            ("L1", "1", "2", "L1"),
            ("C1", "2", "0", "C1"),
        ],
    )

    plan = build_layout_plan(circuit)

    assert plan.circuit_ir.circuit_name == "Planned Circuit"
    assert plan.layout_mode == "generic"
    assert plan.use_backbone_layout is True
    assert plan.backbone_positions is not None
    assert plan.backbone_positions["1"] < plan.backbone_positions["2"]


def test_build_layout_plan_tracks_parallel_branch_groups():
    """Repeated non-ground node pairs should be recognized as one parallel branch group."""
    circuit = CircuitDefinition.model_validate(
        {
            "name": "Parallel Branch",
            "components": [
                {"name": "R_port", "default": 50.0, "unit": "Ohm"},
                {"name": "L_q", "default": 10.0, "unit": "nH"},
                {"name": "C_q", "default": 1.0, "unit": "pF"},
            ],
            "topology": [
                ("P1", "1", "0", 1),
                ("R1", "1", "0", "R_port"),
                ("Lq", "1", "2", "L_q"),
                ("Cq", "1", "2", "C_q"),
            ],
        }
    )

    plan = build_layout_plan(circuit)

    assert plan.parallel_cluster_metadata[2][1:] == (0, 2)
    assert plan.parallel_cluster_metadata[3][1:] == (1, 2)
    assert plan.parallel_edge_padding[frozenset(("1", "2"))] > 0.0
    assert plan.backbone_positions is not None
    assert (plan.backbone_positions["2"] - plan.backbone_positions["1"]) > plan.dx


def test_parallel_branch_y_assigns_distinct_lanes():
    """Parallel branch group members should be assigned separate y lanes."""
    upper = _parallel_branch_y(cluster_index=0, cluster_total=2)
    lower = _parallel_branch_y(cluster_index=1, cluster_total=2)

    assert upper != lower
    assert upper < 3.0
    assert lower > 3.0


def test_resolve_shunt_label_layout_can_prefer_outer_side():
    """Shunt labels near parallel groups should be steered to the requested outer side."""
    side, x_offset, *_ = _resolve_shunt_label_layout(
        x=4.0,
        component_kind="resistor",
        name_label="R1",
        value_label="50 Ohm",
        cluster_index=0,
        cluster_total=1,
        layout_mode="generic",
        occupied_boxes=[],
        preferred_side="left",
    )

    assert side == "left"
    assert x_offset < 0.0


def test_generate_circuit_svg_mutual_coupling_marker():
    """Mutual-coupling placeholders should still render into the preview SVG."""
    circuit = _circuit(
        name="Test Circuit 2",
        parameters={
            "L2": {"default": 1.0, "unit": "nH"},
            "L3": {"default": 1.0, "unit": "nH"},
            "K1": {"default": 0.999, "unit": "H"},
        },
        topology=[
            ("L2", "1", "2", "L2"),
            ("L3", "2", "3", "L3"),
            ("K1", "L2", "L3", "K1"),
        ],
    )

    svg_str = generate_circuit_svg(circuit)

    assert isinstance(svg_str, str)
    assert "<svg" in svg_str
    assert "K1" in svg_str


def test_generate_circuit_svg_includes_component_value_and_unit_labels():
    """Value and unit should be shown alongside component id in the SVG output."""
    circuit = _circuit(
        name="Labeled Circuit",
        parameters={
            "R_port": {"default": 50.0, "unit": "Ohm"},
            "L_main": {"default": 10.0, "unit": "nH"},
            "C_main": {"default": 1.2, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R_port"),
            ("L1", "1", "2", "L_main"),
            ("C1", "2", "0", "C_main"),
        ],
    )

    svg_str = generate_circuit_svg(circuit)

    assert "R50" in svg_str
    assert "50 Ohm" in svg_str
    assert "10 nH" in svg_str
    assert "1.2 pF" in svg_str
    assert "L1\\n" not in svg_str
    assert "C1\\n" not in svg_str


def test_generate_circuit_svg_scales_for_large_topology():
    """Longer topologies should produce wider SVG extents (avoid cramped rendering)."""
    small = _legacy_circuit(
        name="Small",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1": {"default": 8.0, "unit": "nH"},
            "C1": {"default": 0.8, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
            ("L1", "1", "2", "L1"),
            ("C1", "2", "0", "C1"),
        ],
    )
    large = _legacy_circuit(
        name="Large",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1": {"default": 8.0, "unit": "nH"},
            "C1": {"default": 0.8, "unit": "pF"},
            "L2": {"default": 9.0, "unit": "nH"},
            "C2": {"default": 0.7, "unit": "pF"},
            "L3": {"default": 10.0, "unit": "nH"},
            "C3": {"default": 0.6, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
            ("L1", "1", "2", "L1"),
            ("C1", "2", "0", "C1"),
            ("L2", "2", "3", "L2"),
            ("C2", "3", "0", "C2"),
            ("L3", "3", "4", "L3"),
            ("C3", "4", "0", "C3"),
        ],
    )

    small_svg = generate_circuit_svg(small)
    large_svg = generate_circuit_svg(large)
    small_width_match = re.search(r'width="([0-9.]+)pt"', small_svg)
    large_width_match = re.search(r'width="([0-9.]+)pt"', large_svg)

    assert small_width_match is not None
    assert large_width_match is not None
    assert float(large_width_match.group(1)) > float(small_width_match.group(1))


def test_generate_circuit_svg_adds_padding_to_viewbox():
    """SVG output should include extra viewbox room to avoid edge clipping."""
    raw_svg = '<svg height="100pt" width="200pt" viewBox="0 0 200 100"></svg>'

    padded_svg = _add_svg_padding(raw_svg, pad_pt=12.0)

    assert 'height="124.0pt"' in padded_svg
    assert 'width="224.0pt"' in padded_svg
    assert 'viewBox="-12.0 -12.0 224.0 124.0"' in padded_svg


def test_classify_layout_mode_detects_jtwpa_like_topology():
    """Repeated series inductors plus shunt capacitors should use the ladder profile."""
    circuit = _legacy_circuit(
        name="JTWPA-ish",
        parameters={
            "L1": {"default": 8.0, "unit": "pH"},
            "C1": {"default": 0.5, "unit": "fF"},
            "L2": {"default": 8.0, "unit": "pH"},
            "C2": {"default": 0.5, "unit": "fF"},
            "L3": {"default": 8.0, "unit": "pH"},
            "C3": {"default": 0.5, "unit": "fF"},
        },
        topology=[
            ("L1", "1", "2", "L1"),
            ("C1", "2", "0", "C1"),
            ("L2", "2", "3", "L2"),
            ("C2", "3", "0", "C2"),
            ("L3", "3", "4", "L3"),
            ("C3", "4", "0", "C3"),
        ],
    )

    assert _classify_layout_mode(circuit) == "jtwpa_like"


def test_build_backbone_positions_extracts_simple_chain_path():
    """Simple chain-like topologies should receive a stable left-to-right backbone."""
    circuit = _legacy_circuit(
        name="Chain",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1": {"default": 10.0, "unit": "nH"},
            "C1": {"default": 1.0, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
            ("L1", "1", "2", "L1"),
            ("C1", "2", "0", "C1"),
        ],
    )

    positions = _build_backbone_positions(circuit, dx=3.2)

    assert positions is not None
    assert positions["1"] < positions["2"]


def test_build_backbone_positions_expands_when_adjacent_nodes_have_shunt_padding():
    """Backbone spacing should grow when nearby shunt branches consume horizontal space."""
    circuit = _legacy_circuit(
        name="Padded Chain",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "L1p": {"default": 10.0, "unit": "nH"},
            "C1p": {"default": 1.0, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R1", "1", "0", "R50"),
            ("L1", "1", "2", "L1p"),
            ("C1", "2", "0", "C1p"),
        ],
    )

    shunt_metadata = {
        0: ("1", 0, 2),
        1: ("1", 1, 2),
        3: ("2", 0, 1),
    }
    shunt_offsets = _build_shunt_branch_offsets(circuit, "generic")
    node_padding = _build_signal_node_padding(shunt_metadata, shunt_offsets)

    positions = _build_backbone_positions(circuit, dx=3.0, node_padding=node_padding)

    assert positions is not None
    assert (positions["2"] - positions["1"]) > 3.5


def test_estimate_component_slot_width_grows_for_long_value_labels():
    """Longer value labels should reserve more horizontal space."""
    short_slot = _estimate_component_slot_width(
        component_kind="capacitor",
        name_label="C2",
        value_label="1 pF",
        layout_mode="jpa_like",
    )
    long_slot = _estimate_component_slot_width(
        component_kind="josephson_junction",
        name_label="Lj1",
        value_label="2.1963e-10 H",
        layout_mode="jpa_like",
    )

    assert long_slot > short_slot


def test_shunt_label_plan_spreads_dense_cluster_labels_outward():
    """Dense shunt clusters should push labels to opposite sides."""
    left_side = _shunt_label_plan(
        "josephson_junction", cluster_index=0, cluster_total=2, layout_mode="jpa_like"
    )
    right_side = _shunt_label_plan(
        "capacitor", cluster_index=1, cluster_total=2, layout_mode="jpa_like"
    )

    assert left_side[0] == "left"
    assert left_side[1] < 0.0
    assert right_side[0] == "right"
    assert right_side[1] > 0.0


def test_build_shunt_branch_offsets_reserves_more_space_for_dense_jpa_cluster():
    """Dense JPA-like shunt clusters should get wider branch separation."""
    circuit = _legacy_circuit(
        name="JPA Branch Spacing",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "C1": {"default": 0.1, "unit": "pF"},
            "Lj_core": {"default": 1e-9, "unit": "H"},
            "C_shunt": {"default": 1e-12, "unit": "F"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R1", "1", "0", "R50"),
            ("C1", "1", "2", "C1"),
            ("Lj1", "2", "0", "Lj_core"),
            ("C2", "2", "0", "C_shunt"),
        ],
    )

    offsets = _build_shunt_branch_offsets(circuit, "jpa_like")

    assert offsets[3] < 0.0
    assert offsets[4] > 0.0
    assert offsets[4] - offsets[3] > 2.0


def test_resolve_shunt_label_layout_avoids_previously_occupied_label_box():
    """Second shunt label group should choose a non-overlapping candidate layout."""
    occupied: list[tuple[float, float, float, float]] = []
    _, _, _, _, first_box = _resolve_shunt_label_layout(
        x=5.0,
        component_kind="josephson_junction",
        name_label="Lj1",
        value_label="2.1963e-10 H",
        cluster_index=0,
        cluster_total=2,
        layout_mode="jpa_like",
        occupied_boxes=occupied,
    )
    occupied.append(first_box)
    _, _, _, _, second_box = _resolve_shunt_label_layout(
        x=5.5,
        component_kind="capacitor",
        name_label="C2",
        value_label="4e-13 F",
        cluster_index=1,
        cluster_total=2,
        layout_mode="jpa_like",
        occupied_boxes=occupied,
    )

    assert not _boxes_overlap(first_box, second_box)


def test_generate_circuit_svg_does_not_duplicate_port_label_in_shunt_clusters():
    """Port labels should appear once even when the port participates in a dense shunt node."""
    circuit = _legacy_circuit(
        name="Port Labels",
        parameters={"R50": {"default": 50.0, "unit": "Ohm"}},
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
        ],
    )

    svg_str = generate_circuit_svg(circuit)

    assert len(re.findall(r">P1</tspan>", svg_str)) == 1


def test_generate_circuit_svg_places_ground_node_label_below_ground_line():
    """Ground node labels should not sit on top of the ground conductor."""
    circuit = _legacy_circuit(
        name="Ground Label",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
            "C1": {"default": 1.0, "unit": "pF"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
            ("C1", "1", "0", "C1"),
        ],
    )

    svg_str = generate_circuit_svg(circuit)
    zero_label_match = re.search(
        r'<text x="[^"]+" y="([0-9.eE+-]+)"[^>]*><tspan[^>]*>0</tspan>',
        svg_str,
    )

    assert zero_label_match is not None
    assert float(zero_label_match.group(1)) > 0.0


def test_shunt_branch_offset_spreads_dense_clusters_around_anchor():
    """Multiple shunts on the same node should not stack on the same x anchor."""
    left_offset = _shunt_branch_offset(
        "josephson_junction", cluster_index=0, cluster_total=2, layout_mode="jpa_like"
    )
    right_offset = _shunt_branch_offset(
        "capacitor", cluster_index=1, cluster_total=2, layout_mode="jpa_like"
    )

    assert left_offset < 0.0
    assert right_offset > 0.0
    assert abs(left_offset - right_offset) > 1.0
