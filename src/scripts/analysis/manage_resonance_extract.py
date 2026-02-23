#!/usr/bin/env python3
"""CLI for resonance frequency extraction (non-fitting methods)."""

from typing import Annotated

import typer
from core.analysis.application.services.database_query import DatabaseQueryService
from rich.console import Console
from rich.table import Table

from core.analysis.application.analysis.extraction.admittance import (
    extract_modes_from_dataframe,
)
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="Resonance Extraction Subcommands.", add_completion=False)


@app.command("admittance")
def extract_admittance(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
    bias_index: Annotated[
        int, typer.Option("--bias-index", "-b", help="L_jun bias slice index")
    ] = -1,
) -> None:
    """
    Extract resonance frequencies from Admittance data using Im(Y)=0 zero-crossing.

    This is a direct extraction method (no curve fitting). It finds the frequencies
    where the imaginary part of the admittance crosses zero, which correspond to
    the natural resonances of the circuit.
    """
    import numpy as np
    import pandas as pd

    db = DatabaseQueryService()
    try:
        console.print(
            f"[cyan]Initiating resonance extraction[/cyan] on dataset: [bold]{dataset_identifier}[/bold]"
        )

        # Look up the dataset
        dataset = db.find_dataset(dataset_identifier)
        if dataset is None:
            console.print(f"[red]Dataset '{dataset_identifier}' not found.[/red]")
            raise typer.Exit(code=1)

        # Find the Im(Y) data record(s)
        records = db.find_data_records(
            dataset_id=dataset.id,
            data_type="admittance",
        )

        if not records:
            console.print("[red]No admittance data records found for this dataset.[/red]")
            raise typer.Exit(code=1)

        # Build a DataFrame from the records (frequency + ImY columns, optionally with L_jun)
        dfs = []
        for rec in records:
            arr = np.array(rec.values)
            freq_arr = np.array(rec.x_values) if rec.x_values else None
            if freq_arr is None:
                console.print(f"[yellow]Skipping record {rec.id}: no frequency axis.[/yellow]")
                continue
            df_part = pd.DataFrame(
                {
                    "Freq [GHz]": freq_arr,
                    "im(Y) []": arr,
                }
            )
            if hasattr(rec, "bias_value") and rec.bias_value is not None:
                df_part["L_jun [nH]"] = rec.bias_value
            dfs.append(df_part)

        if not dfs:
            console.print("[red]No valid admittance data found.[/red]")
            raise typer.Exit(code=1)

        full_df = pd.concat(dfs, ignore_index=True)

        # Run extraction
        result_df = extract_modes_from_dataframe(full_df)

        if result_df is None or result_df.empty:
            console.print("[red]No resonance modes found.[/red]")
            raise typer.Exit(code=1)

        # If a specific bias index is requested
        if bias_index >= 0:
            if bias_index >= len(result_df):
                console.print(
                    f"[red]Bias index {bias_index} out of range (max: {len(result_df) - 1}).[/red]"
                )
                raise typer.Exit(code=1)
            result_df = result_df.iloc[[bias_index]]

        # Pretty print results
        console.print("[green]Extraction completed successfully![/green]\n")
        console.print("[bold]Extracted Resonance Modes:[/bold]")

        table = Table(title="Im(Y)=0 Zero-Crossing Resonances")
        for col in result_df.columns:
            table.add_column(col, justify="right")

        for _, row in result_df.iterrows():
            table.add_row(*[f"{v:.6f}" if isinstance(v, float) else str(v) for v in row])

        console.print(table)

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
