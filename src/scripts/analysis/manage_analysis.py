#!/usr/bin/env python3
"""CLI for running numerical analysis workflows."""

from typing import Annotated

import typer
from rich.console import Console

from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="Resonance Fitting Subcommands.", add_completion=False)


@app.command("scattering")
def fit_scattering(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
    parameter: Annotated[
        str, typer.Option("--parameter", "-p", help="S-parameter name (e.g. S21, S11)")
    ] = "S21",
    f_min: Annotated[
        float | None, typer.Option("--f-min", help="Minimum frequency for fitting range in GHz")
    ] = None,
    f_max: Annotated[
        float | None, typer.Option("--f-max", help="Maximum frequency for fitting range in GHz")
    ] = None,
    bias_index: Annotated[
        int, typer.Option("--bias-index", "-b", help="L_jun bias slice index to fit")
    ] = 0,
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
            dataset_identifier=dataset_identifier,
            parameter=parameter,
            f_min=f_min,
            f_max=f_max,
            bias_index=bias_index,
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

        # Visualization
        console.print("\n[yellow]Generating interactive Plotly visualization...[/yellow]")
        import numpy as np
        import plotly.graph_objects as go

        data_payload = result["data"]
        f_ghz = data_payload["f"] / 1e9
        s21_raw = data_payload["s21_raw"]
        s21_fit = data_payload["s21_model"]

        fig = go.Figure()

        # Magnitude vs Frequency
        # Assuming linear S-parameters are passed, convert to dB for viewing
        mag_raw_db = 20 * np.log10(np.abs(s21_raw))
        mag_fit_db = 20 * np.log10(np.abs(s21_fit))

        fig.add_trace(
            go.Scatter(
                x=f_ghz,
                y=mag_raw_db,
                mode="markers",
                marker=dict(size=5, color="rgba(0,0,255,0.5)"),
                name="Data Mag (dB)",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=f_ghz,
                y=mag_fit_db,
                mode="lines",
                line=dict(color="red", width=2),
                name="Fit Mag (dB)",
            )
        )

        fig.update_layout(
            title=f"Resonance Fit (Scattering): {dataset_identifier} ({parameter})",
            height=600,
            width=800,
            template="plotly_white",
            xaxis_title="Frequency (GHz)",
            yaxis_title="Magnitude (dB)",
        )

        fig.show()

    except Exception as e:
        console.print(f"[red]Error during fitting:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("admittance")
def fit_admittance(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
) -> None:
    """Perform RLC resonance fit on a dataset's Y-parameters."""
    console.print(
        f"[yellow]Admittance fitting for {dataset_identifier} is not yet implemented.[/yellow]"
    )
    raise typer.Exit(code=1)


@app.command("compare")
def compare_fits(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
) -> None:
    """Compare S-parameter and Y-parameter fits for the same dataset."""
    console.print(f"[yellow]Comparison for {dataset_identifier} is not yet implemented.[/yellow]")
    raise typer.Exit(code=1)


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
