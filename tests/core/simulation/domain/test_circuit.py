"""Tests for simulation domain models."""

import pytest

from core.simulation.domain.circuit import (
    CircuitDefinition,
    SimulationResult,
    format_circuit_definition,
    migrate_legacy_circuit_definition,
)
from core.simulation.domain.compiler import compile_simulation_topology


def _legacy_circuit(*, name: str, parameters: dict, topology: list[tuple]) -> CircuitDefinition:
    return CircuitDefinition.model_validate(
        migrate_legacy_circuit_definition(
            {"name": name, "parameters": parameters, "topology": topology}
        )
    )


def test_circuit_definition_compiles_to_explicit_ir() -> None:
    circuit = _legacy_circuit(
        name="IR Compile",
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

    compiled_ir = circuit.to_ir()

    assert compiled_ir.circuit_name == "IR Compile"
    assert compiled_ir.layout_direction == "lr"
    assert compiled_ir.layout_profile == "generic"
    assert compiled_ir.available_port_indices == (1,)
    assert [element.name for element in compiled_ir.elements] == ["P1", "R1", "L1", "C1"]
    assert compile_simulation_topology(
        compiled_ir,
        is_ground_node=lambda node: circuit.is_ground_node(node),
    ) == [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R50"),
        ("L1", "1", "2", "L1"),
        ("C1", "2", "0", "C1"),
    ]


def test_format_circuit_definition_uses_canonical_json_style() -> None:
    circuit = _legacy_circuit(
        name="Formatted",
        parameters={
            "R50": {"default": 50.0, "unit": "Ohm"},
        },
        topology=[
            ("P1", "1", "0", 1),
            ("R1", "1", "0", "R50"),
        ],
    )

    formatted = format_circuit_definition(circuit)

    assert formatted.startswith("{\n")
    assert '"schema_version": "0.1"' in formatted
    assert '"name": "Formatted"' in formatted
    assert "'name': 'Formatted'" not in formatted


def test_simulation_result_derives_s11_views() -> None:
    result = SimulationResult(
        frequencies_ghz=[5.0, 5.1],
        s11_real=[1.0, 0.0],
        s11_imag=[0.0, 1.0],
        port_indices=[1, 2],
        mode_indices=[(0,), (1,)],
        s_parameter_real={"S11": [1.0, 0.0], "S21": [0.5, 0.25]},
        s_parameter_imag={"S11": [0.0, 1.0], "S21": [0.0, -0.25]},
        s_parameter_mode_real={
            "om=0|op=1|im=0|ip=1": [1.0, 0.0],
            "om=0|op=2|im=0|ip=1": [0.5, 0.25],
            "om=1|op=2|im=0|ip=1": [1.5, 1.25],
        },
        s_parameter_mode_imag={
            "om=0|op=1|im=0|ip=1": [0.0, 1.0],
            "om=0|op=2|im=0|ip=1": [0.0, -0.25],
            "om=1|op=2|im=0|ip=1": [0.0, 0.5],
        },
        z_parameter_mode_real={"om=0|op=2|im=0|ip=2": [150.0, 160.0]},
        z_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [0.0, 5.0]},
        y_parameter_mode_real={"om=0|op=2|im=0|ip=2": [0.006, 0.005]},
        y_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [0.0, -0.001]},
        qe_parameter_mode={"om=1|op=2|im=0|ip=1": [0.8, 0.9]},
        qe_ideal_parameter_mode={"om=1|op=2|im=0|ip=1": [0.95, 0.97]},
        cm_parameter_mode={"om=1|op=2": [1.0, 1.0]},
    )

    assert result.s11_complex == [complex(1.0, 0.0), complex(0.0, 1.0)]
    assert result.available_port_indices == [1, 2]
    assert result.available_mode_indices == [(0,), (1,)]
    assert result.available_s_parameter_labels == ["S11", "S21"]
    assert result.available_mode_s_parameter_labels == [
        "om=0|op=1|im=0|ip=1",
        "om=0|op=2|im=0|ip=1",
        "om=1|op=2|im=0|ip=1",
    ]
    assert result.get_s_parameter_complex(2, 1) == [complex(0.5, 0.0), complex(0.25, -0.25)]
    assert result.get_mode_s_parameter_complex((1,), 2, (0,), 1) == [
        complex(1.5, 0.0),
        complex(1.25, 0.5),
    ]
    assert result.s11_magnitude == [1.0, 1.0]
    assert result.return_gain_linear == [1.0, 1.0]
    assert result.s11_db == [0.0, 0.0]
    assert result.return_gain_db == [0.0, 0.0]
    assert result.s11_phase_deg == [0.0, 90.0]
    assert result.get_gain_linear(2, 1) == pytest.approx([0.25, 0.125])
    assert result.get_mode_gain_linear((1,), 2, (0,), 1) == pytest.approx([2.25, 1.8125])
    assert result.get_mode_z_parameter_complex((0,), 2, (0,), 2) == [
        complex(150.0, 0.0),
        complex(160.0, 5.0),
    ]
    assert result.get_mode_y_parameter_complex((0,), 2, (0,), 2) == [
        complex(0.006, 0.0),
        complex(0.005, -0.001),
    ]
    assert result.get_mode_qe((1,), 2, (0,), 1) == [0.8, 0.9]
    assert result.get_mode_qe_ideal((1,), 2, (0,), 1) == [0.95, 0.97]
    assert result.get_mode_cm((1,), 2) == [1.0, 1.0]


def test_simulation_result_converts_s11_to_impedance_and_admittance() -> None:
    result = SimulationResult(
        frequencies_ghz=[5.0],
        s11_real=[0.0],
        s11_imag=[0.0],
    )

    impedance = result.calculate_input_impedance_ohm(reference_impedance_ohm=50.0)
    admittance = result.calculate_input_admittance_s(reference_impedance_ohm=50.0)

    assert impedance == [complex(50.0, 0.0)]
    assert admittance == [complex(0.02, 0.0)]


def test_simulation_result_impedance_uses_selected_reflection_port() -> None:
    result = SimulationResult(
        frequencies_ghz=[5.0],
        s11_real=[0.0],
        s11_imag=[0.0],
        port_indices=[1, 2],
        s_parameter_real={"S11": [0.0], "S22": [0.5]},
        s_parameter_imag={"S11": [0.0], "S22": [0.0]},
        z_parameter_mode_real={"om=0|op=2|im=0|ip=2": [120.0]},
        z_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [1.0]},
    )

    impedance_port_2 = result.calculate_input_impedance_ohm(
        reference_impedance_ohm=50.0,
        port=2,
    )

    assert impedance_port_2 == [complex(120.0, 1.0)]
