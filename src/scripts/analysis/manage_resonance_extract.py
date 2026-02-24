#!/usr/bin/env python3
"""CLI for resonance frequency extraction (non-fitting methods)."""

from typing import Annotated

import typer
from rich.console import Console

from core.analysis.application.analysis.extraction.admittance import (
    extract_mode_from_admittance,
)
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="Resonance Extraction Subcommands.", add_completion=False)


@app.command("admittance")
def extract_admittance(
    csv_path: Annotated[str, typer.Argument(help="Path to HFSS Admittance CSV file")],
) -> None:
    """
    Extract resonance frequencies from an Admittance CSV using Im(Y)=0 zero-crossing.

    This is a direct extraction method (no curve fitting). It finds the frequencies
    where the imaginary part of the admittance crosses zero, which correspond to
    the natural resonances of the circuit.
    """
    from rich.table import Table

    try:
        console.print(f"[cyan]Extracting resonance modes[/cyan] from: [bold]{csv_path}[/bold]")

        result_df = extract_mode_from_admittance(csv_path)

        if result_df is None or result_df.empty:
            console.print("[red]No resonance modes found.[/red]")
            raise typer.Exit(code=1)

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

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error during extraction:[/red] {e}")
        raise typer.Exit(code=1)


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
