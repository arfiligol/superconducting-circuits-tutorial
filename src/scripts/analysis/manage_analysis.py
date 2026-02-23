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
    f_min: Annotated[
        float | None, typer.Option("--f-min", help="Minimum frequency for fitting range in GHz")
    ] = None,
    f_max: Annotated[
        float | None, typer.Option("--f-max", help="Maximum frequency for fitting range in GHz")
    ] = None,
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
        from plotly.subplots import make_subplots

        data_payload = result["data"]
        f_ghz = data_payload["f"] / 1e9
        s21_raw = data_payload["s21_raw"]
        s21_fit = data_payload["s21_model"]

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Complex Plane (Re vs Im)", f"Magnitude ({parameter}) vs Frequency"),
        )

        # Subplot 1: Complex Plane
        fig.add_trace(
            go.Scatter(
                x=np.real(s21_raw),
                y=np.imag(s21_raw),
                mode="markers",
                marker=dict(
                    size=6,
                    color=f_ghz,
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Freq (GHz)", x=0.45),
                ),
                name=f"Data ({parameter})",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=np.real(s21_fit),
                y=np.imag(s21_fit),
                mode="lines",
                line=dict(color="red", width=2),
                name="Fit Model",
            ),
            row=1,
            col=1,
        )

        # Subplot 2: Magnitude vs Frequency
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
            ),
            row=1,
            col=2,
        )

        fig.add_trace(
            go.Scatter(
                x=f_ghz,
                y=mag_fit_db,
                mode="lines",
                line=dict(color="red", width=2),
                name="Fit Mag (dB)",
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title=f"Resonance Fit: {dataset_identifier}",
            height=600,
            width=1200,
            template="plotly_white",
        )
        fig.update_xaxes(title_text="Re", row=1, col=1)
        # Force complex plane to be 1:1 aspect ratio
        fig.update_yaxes(title_text="Im", scaleanchor="x", scaleratio=1, row=1, col=1)

        fig.update_xaxes(title_text="Frequency (GHz)", row=1, col=2)
        fig.update_yaxes(title_text="Magnitude (dB)", row=1, col=2)

        fig.show()

    except Exception as e:
        console.print(f"[red]Error during fitting:[/red] {e}")
        raise typer.Exit(code=1)


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
