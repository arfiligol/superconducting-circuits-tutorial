#!/usr/bin/env python3
"""CLI for resonance frequency extraction (non-fitting methods)."""

from typing import Annotated

import typer
from rich.console import Console

from core.analysis.application.services.resonance_extract_service import (
    ResonanceExtractService,
)
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="Resonance Extraction Subcommands.", add_completion=False)


@app.command("admittance")
def extract_admittance(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
    bias_index: Annotated[
        int | None,
        typer.Option(
            "--bias-index", "-b", help="L_jun bias slice index (default: extract ALL slices)"
        ),
    ] = None,
) -> None:
    """
    Extract resonance frequencies from a Database Dataset using Im(Y)=0 zero-crossing.

    This is a direct extraction method (no curve fitting). It finds the frequencies
    where the imaginary part of the admittance crosses zero, which correspond to
    the natural resonances of the circuit.

    If the data contains multiple bias points (L_jun), all slices are extracted by default.
    Use --bias-index to select a specific slice.
    """
    from rich.table import Table

    service = ResonanceExtractService()
    try:
        console.print(
            "[cyan]Extracting resonance modes[/cyan] from dataset: "
            f"[bold]{dataset_identifier}[/bold]"
        )

        result = service.extract_admittance(
            dataset_identifier=dataset_identifier, bias_index=bias_index
        )
        result_df = result["results"]

        console.print("[green]Extraction completed successfully![/green]\n")

        # Pretty print results
        table = Table(title="Im(Y)=0 Zero-Crossing Resonances")
        for col in result_df.columns:
            table.add_column(col, justify="right")

        for _, row in result_df.iterrows():
            table.add_row(*[f"{v:.6f}" if isinstance(v, float) else str(v) for v in row])

        console.print(table)
        console.print(
            f"\n[dim]Total: {len(result_df)} bias point(s), "
            f"up to {len(result_df.columns) - 1} mode(s) each.[/dim]"
        )

        console.print("[cyan]These have been saved as Derived Parameters to the database.[/cyan]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error during extraction:[/red] {e}")
        raise typer.Exit(code=1) from e


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
