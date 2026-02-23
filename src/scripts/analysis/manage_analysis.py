#!/usr/bin/env python3
"""CLI for running numerical analysis workflows."""

from typing import Annotated

import typer
from rich.console import Console

from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="Run numerical analysis on datasets.", add_completion=False)


@app.command("resonance-fit")
def fit_resonance(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
    parameter: Annotated[
        str, typer.Option("--parameter", "-p", help="S-parameter name (e.g. S21, S11)")
    ] = "S21",
) -> None:
    """
    Perform a complex resonance fit (Notch model) on a dataset's S-parameters.

    The dataset must contain matching data records for the specified parameter
    in representations that allow for building the complex signal (e.g. Re/Im or Mag/Phase).
    """
    service = ResonanceFitService()
    try:
        console.print(
            f"[cyan]Initiating resonance fit[/cyan] on dataset: [bold]{dataset_identifier}[/bold]"
        )
        console.print(f"Targeting Parameter: [bold]{parameter}[/bold]")

        result = service.perform_notch_fit(
            dataset_identifier=dataset_identifier, parameter=parameter
        )

        console.print("[green]Fit completed successfully![/green]\n")
        console.print("[bold]Extracted Parameters:[/bold]")
        console.print(f"  Resonance Frequency (fr): {result['fr'] / 1e9:.6f} GHz")
        console.print(f"  Loaded Q (Ql)         : {result['Ql']:.2f}")
        console.print(f"  Internal Q (Qi)       : {result['Qi']:.2f}")
        console.print(f"  Coupling Q (Qc)       : {result['Qc_mag']:.2f}")
        console.print(f"  Elec. Delay (tau)     : {result['tau'] * 1e9:.4f} ns")
        console.print(f"  Model Cost            : {result['cost']:.4e}\n")
        console.print("[cyan]These have been saved as Derived Parameters to the database.[/cyan]")

    except Exception as e:
        console.print(f"[red]Error during fitting:[/red] {e}")
        raise typer.Exit(code=1)


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
