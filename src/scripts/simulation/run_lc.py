#!/usr/bin/env python3
"""
CLI script for running circuit simulations.

Usage:
    uv run sc-simulate-lc --help
    uv run sc-simulate-lc --inductance 10 --capacitance 1 --start 0.1 --stop 10
"""

import argparse
from typing import NamedTuple


class Args(NamedTuple):
    inductance: float
    capacitance: float
    start: float
    stop: float
    points: int
    output: str | None


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="Simulate an LC resonator and compute S11.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--inductance",
        "-L",
        type=float,
        default=10.0,
        help="Inductance in nH (default: 10)",
    )
    parser.add_argument(
        "--capacitance",
        "-C",
        type=float,
        default=1.0,
        help="Capacitance in pF (default: 1)",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=0.1,
        help="Start frequency in GHz (default: 0.1)",
    )
    parser.add_argument(
        "--stop",
        type=float,
        default=10.0,
        help="Stop frequency in GHz (default: 10)",
    )
    parser.add_argument(
        "--points",
        "-n",
        type=int,
        default=1000,
        help="Number of frequency points (default: 1000)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output JSON file path (optional)",
    )

    ns = parser.parse_args()
    return Args(
        inductance=ns.inductance,
        capacitance=ns.capacitance,
        start=ns.start,
        stop=ns.stop,
        points=ns.points,
        output=ns.output,
    )


def main() -> None:
    args = parse_args()

    print(f"Simulating LC resonator: L={args.inductance} nH, C={args.capacitance} pF")
    print(f"Frequency range: {args.start} - {args.stop} GHz ({args.points} points)")

    # Import here to allow --help without Julia startup
    from core.simulation.domain.circuit import FrequencyRange
    from core.simulation.infrastructure.julia_adapter import JuliaSimulator

    freq_range = FrequencyRange(
        start_ghz=args.start,
        stop_ghz=args.stop,
        points=args.points,
    )

    simulator = JuliaSimulator()
    result = simulator.run_lc_simulation(
        inductance_nh=args.inductance,
        capacitance_pf=args.capacitance,
        freq_range=freq_range,
    )

    # Calculate resonance frequency
    import math

    f0_ghz = 1 / (2 * math.pi * math.sqrt(args.inductance * 1e-9 * args.capacitance * 1e-12)) / 1e9
    print(f"\nExpected resonance: {f0_ghz:.3f} GHz")
    print(f"Simulation complete: {len(result.frequencies_ghz)} points")

    # Find minimum S11 (resonance dip)
    s11_mag = result.s11_magnitude
    min_idx = s11_mag.index(min(s11_mag))
    print(f"Resonance found at: {result.frequencies_ghz[min_idx]:.3f} GHz")

    if args.output:
        import json

        with open(args.output, "w") as f:
            json.dump(
                {
                    "frequencies_ghz": result.frequencies_ghz,
                    "s11_real": result.s11_real,
                    "s11_imag": result.s11_imag,
                    "s11_magnitude": s11_mag,
                    "config": {
                        "inductance_nh": args.inductance,
                        "capacitance_pf": args.capacitance,
                    },
                },
                f,
                indent=2,
            )
        print(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
