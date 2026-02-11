#!/usr/bin/env python3
"""
CLI script for running circuit simulations.

Usage:
    uv run sc-simulate-lc --help
    uv run sc-simulate-lc --inductance 10 --capacitance 1 --start 0.1 --stop 10
"""

from typing import Annotated

import typer

app = typer.Typer(add_completion=False)


@app.command()
def main(
    inductance: Annotated[
        float,
        typer.Option("--inductance", "-L", help="Inductance in nH (default: 10)"),
    ] = 10.0,
    capacitance: Annotated[
        float,
        typer.Option("--capacitance", "-C", help="Capacitance in pF (default: 1)"),
    ] = 1.0,
    start: Annotated[
        float,
        typer.Option(help="Start frequency in GHz (default: 0.1)"),
    ] = 0.1,
    stop: Annotated[
        float,
        typer.Option(help="Stop frequency in GHz (default: 10)"),
    ] = 10.0,
    points: Annotated[
        int,
        typer.Option("--points", "-n", help="Number of frequency points (default: 1000)"),
    ] = 1000,
    output: Annotated[
        str | None,
        typer.Option("--output", "-o", help="Output JSON file path (optional)"),
    ] = None,
) -> None:
    """Simulate an LC resonator and compute S11."""

    print(f"Simulating LC resonator: L={inductance} nH, C={capacitance} pF")
    print(f"Frequency range: {start} - {stop} GHz ({points} points)")

    # Import here to allow --help without Julia startup
    from core.simulation.domain.circuit import FrequencyRange
    from core.simulation.infrastructure.julia_adapter import JuliaSimulator

    freq_range = FrequencyRange(
        start_ghz=start,
        stop_ghz=stop,
        points=points,
    )

    simulator = JuliaSimulator()
    result = simulator.run_lc_simulation(
        inductance_nh=inductance,
        capacitance_pf=capacitance,
        freq_range=freq_range,
    )

    # Calculate resonance frequency
    import math

    f0_ghz = 1 / (2 * math.pi * math.sqrt(inductance * 1e-9 * capacitance * 1e-12)) / 1e9
    print(f"\nExpected resonance: {f0_ghz:.3f} GHz")
    print(f"Simulation complete: {len(result.frequencies_ghz)} points")

    # Find minimum S11 (resonance dip)
    s11_mag = result.s11_magnitude
    min_idx = s11_mag.index(min(s11_mag))
    print(f"Resonance found at: {result.frequencies_ghz[min_idx]:.3f} GHz")

    if output:
        import json

        with open(output, "w") as f:
            json.dump(
                {
                    "frequencies_ghz": result.frequencies_ghz,
                    "s11_real": result.s11_real,
                    "s11_imag": result.s11_imag,
                    "s11_magnitude": s11_mag,
                    "config": {
                        "inductance_nh": inductance,
                        "capacitance_pf": capacitance,
                    },
                },
                f,
                indent=2,
            )
        print(f"Results saved to: {output}")


if __name__ == "__main__":
    app()
