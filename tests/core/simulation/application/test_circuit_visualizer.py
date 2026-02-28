"""Tests for the circuit visualizer application."""

import re

from core.simulation.application.circuit_visualizer import generate_circuit_svg
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
    circuit = CircuitDefinition(
        name="Padding",
        parameters={"R50": {"default": 50.0, "unit": "Ohm"}},
        topology=[("P1", "1", "0", 1), ("R50", "1", "0", "R50")],
    )

    svg_str = generate_circuit_svg(circuit)
    viewbox_match = re.search(r'viewBox="([0-9.eE+-]+) ([0-9.eE+-]+)', svg_str)
    assert viewbox_match is not None

    # Padded output should start outside the original origin to preserve stroke/text margins.
    assert float(viewbox_match.group(1)) < 0.0
