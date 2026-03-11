from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
OUTPUT_DIRS = [
    ROOT / "docs" / "assets",
    ROOT / "docs" / "docs_zhtw" / "assets",
]

EXAMPLES = {
    "tutorial-series-lc.svg": {
        "schema_version": "0.1",
        "name": "SmokeStableSeriesLC",
        "parameters": {
            "R_port": {"default": 50.0, "unit": "Ohm"},
            "L_main": {"default": 10.0, "unit": "nH"},
            "C_main": {"default": 1.0, "unit": "pF"},
        },
        "ports": [
            {
                "id": "P1",
                "node": "n1",
                "ground": "0",
                "index": 1,
                "role": "signal",
                "side": "left",
            }
        ],
        "instances": [
            {
                "id": "R1",
                "kind": "resistor",
                "pins": ["n1", "0"],
                "value_ref": "R_port",
                "role": "termination",
            },
            {
                "id": "L1",
                "kind": "inductor",
                "pins": ["n1", "n2"],
                "value_ref": "L_main",
                "role": "signal",
            },
            {
                "id": "C1",
                "kind": "capacitor",
                "pins": ["n2", "0"],
                "value_ref": "C_main",
                "role": "shunt",
            },
        ],
        "layout": {"direction": "lr", "profile": "generic"},
    },
    "tutorial-parallel-branch.svg": {
        "schema_version": "0.1",
        "name": "FloatingQubitBranch",
        "parameters": {
            "R_port": {"default": 50.0, "unit": "Ohm"},
            "L_q": {"default": 10.0, "unit": "nH"},
            "C_q": {"default": 1.0, "unit": "pF"},
            "C_g": {"default": 0.1, "unit": "pF"},
        },
        "ports": [
            {
                "id": "P1",
                "node": "n_drive",
                "ground": "0",
                "index": 1,
                "role": "signal",
                "side": "left",
            }
        ],
        "instances": [
            {
                "id": "R1",
                "kind": "resistor",
                "pins": ["n_drive", "0"],
                "value_ref": "R_port",
                "role": "termination",
            },
            {
                "id": "Lq",
                "kind": "inductor",
                "pins": ["n_drive", "n_island"],
                "value_ref": "L_q",
                "role": "qubit_branch",
            },
            {
                "id": "Cq",
                "kind": "capacitor",
                "pins": ["n_drive", "n_island"],
                "value_ref": "C_q",
                "role": "qubit_branch",
            },
            {
                "id": "Cg",
                "kind": "capacitor",
                "pins": ["n_island", "0"],
                "value_ref": "C_g",
                "role": "shunt",
            },
        ],
        "layout": {"direction": "lr", "profile": "qubit_readout"},
    },
    "tutorial-two-port.svg": {
        "schema_version": "0.1",
        "name": "ReadoutAndPumpPorts",
        "parameters": {
            "R_sig": {"default": 50.0, "unit": "Ohm"},
            "R_pump": {"default": 50.0, "unit": "Ohm"},
            "L_core": {"default": 1.2, "unit": "nH"},
            "C_core": {"default": 0.25, "unit": "pF"},
        },
        "ports": [
            {
                "id": "P1",
                "node": "n_sig",
                "ground": "0",
                "index": 1,
                "role": "readout",
                "side": "left",
            },
            {
                "id": "P2",
                "node": "n_pump",
                "ground": "0",
                "index": 2,
                "role": "pump",
                "side": "top",
            },
        ],
        "instances": [
            {
                "id": "Rsig",
                "kind": "resistor",
                "pins": ["n_sig", "0"],
                "value_ref": "R_sig",
                "role": "termination",
            },
            {
                "id": "Rpump",
                "kind": "resistor",
                "pins": ["n_pump", "0"],
                "value_ref": "R_pump",
                "role": "termination",
            },
            {
                "id": "Lcore",
                "kind": "inductor",
                "pins": ["n_sig", "n_core"],
                "value_ref": "L_core",
                "role": "nonlinear_core",
            },
            {
                "id": "Ccore",
                "kind": "capacitor",
                "pins": ["n_core", "n_pump"],
                "value_ref": "C_core",
                "role": "coupler",
            },
        ],
        "layout": {"direction": "lr", "profile": "jpa"},
    },
}


def _bootstrap_import_path() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


def main() -> None:
    _bootstrap_import_path()

    from core.simulation.application.circuit_visualizer import generate_circuit_svg
    from core.simulation.domain.circuit import CircuitDefinition

    for output_dir in OUTPUT_DIRS:
        output_dir.mkdir(parents=True, exist_ok=True)

    for filename, payload in EXAMPLES.items():
        circuit = CircuitDefinition.model_validate(payload)
        svg = generate_circuit_svg(circuit)
        for output_dir in OUTPUT_DIRS:
            path = output_dir / filename
            path.write_text(svg, encoding="utf-8")
            print(f"wrote {path}")


if __name__ == "__main__":
    main()
