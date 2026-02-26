"""Tests for the circuit visualizer application."""

import pytest

from core.simulation.application.circuit_visualizer import generate_circuit_svg
from core.simulation.domain.circuit import CircuitDefinition, ComponentValue


def test_generate_circuit_svg_basic():
    """Test that a basic circuit can be converted to an SVG string."""
    circuit = CircuitDefinition(
        name="Test Circuit",
        components=[
            ComponentValue(name="L1", value=10.0, unit="nH"),
            ComponentValue(name="C1", value=1.0, unit="pF"),
        ],
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
    assert svg_str.startswith("<?xml")
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
        components=[],
        topology=[("K1", "1", "2", "K1"), ("Unknown", "2", "3", "Unknown")],
    )

    svg_str = generate_circuit_svg(circuit)

    assert isinstance(svg_str, str)
    assert "<svg" in svg_str
    assert "K1" in svg_str
    assert "Unknown" in svg_str
