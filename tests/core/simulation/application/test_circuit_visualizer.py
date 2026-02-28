"""Tests for the circuit visualizer application."""

import re

from core.simulation.application.circuit_visualizer import (
    _add_svg_padding,
    _build_backbone_positions,
    _classify_layout_mode,
    _shunt_branch_offset,
    _shunt_label_plan,
    generate_circuit_svg,
)
from core.simulation.domain.circuit import CircuitDefinition


def test_generate_circuit_svg_basic():
    """Test that a basic circuit can be converted to an SVG string."""
    circuit = CircuitDefinition(
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


def test_generate_circuit_svg_unknown_component():
    """Test graceful handling of unknown components like K (Mutual Inductance) or random strings."""
    circuit = CircuitDefinition(
        name="Test Circuit 2",
        parameters={},
        topology=[("K1", "1", "2", "K1"), ("Unknown", "2", "3", "Unknown")],
    )

    svg_str = generate_circuit_svg(circuit)

    assert isinstance(svg_str, str)
    assert "<svg" in svg_str
    assert "K1" in svg_str
    assert "Unknown" in svg_str


def test_generate_circuit_svg_includes_component_value_and_unit_labels():
    """Value and unit should be shown alongside component id in the SVG output."""
    circuit = CircuitDefinition(
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
    small = CircuitDefinition(
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
    large = CircuitDefinition(
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
    circuit = CircuitDefinition(
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
    circuit = CircuitDefinition(
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


def test_shunt_label_plan_spreads_dense_cluster_labels_outward():
    """Dense shunt clusters should push labels to opposite sides."""
    left_side = _shunt_label_plan("Lj1", cluster_index=0, cluster_total=2, layout_mode="jpa_like")
    right_side = _shunt_label_plan("C2", cluster_index=1, cluster_total=2, layout_mode="jpa_like")

    assert left_side[0] == "left"
    assert left_side[1] < 0.0
    assert right_side[0] == "right"
    assert right_side[1] > 0.0


def test_generate_circuit_svg_does_not_duplicate_port_label_in_shunt_clusters():
    """Port labels should appear once even when the port participates in a dense shunt node."""
    circuit = CircuitDefinition(
        name="Port Labels",
        parameters={"R50": {"default": 50.0, "unit": "Ohm"}},
        topology=[
            ("P1", "1", "0", 1),
            ("R50", "1", "0", "R50"),
        ],
    )

    svg_str = generate_circuit_svg(circuit)

    assert len(re.findall(r">P1</tspan>", svg_str)) == 1


def test_shunt_branch_offset_spreads_dense_clusters_around_anchor():
    """Multiple shunts on the same node should not stack on the same x anchor."""
    left_offset = _shunt_branch_offset(
        "Lj1", cluster_index=0, cluster_total=2, layout_mode="jpa_like"
    )
    right_offset = _shunt_branch_offset(
        "C2", cluster_index=1, cluster_total=2, layout_mode="jpa_like"
    )

    assert left_offset < 0.0
    assert right_offset > 0.0
    assert abs(left_offset - right_offset) > 1.0
