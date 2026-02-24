#!/usr/bin/env python3
"""CLI for running numerical analysis workflows."""

from typing import Annotated

import typer
from rich.console import Console

from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.logging import setup_logging

console = Console()
app = typer.Typer(help="S-Parameter Resonance Fitting Subcommands.", add_completion=False)


@app.command("scattering")
def fit_scattering(
    dataset_identifier: Annotated[str, typer.Argument(help="Dataset ID or Name")],
    parameter: Annotated[
        str, typer.Option("--parameter", "-p", help="S-parameter name (e.g. S21, S11)")
    ] = "S21",
    model: Annotated[
        str, typer.Option("--model", "-m", help="Fit model (notch, transmission, vf)")
    ] = "notch",
    resonators: Annotated[
        int, typer.Option("--resonators", "-r", help="Number of physical resonators for VF model")
    ] = 1,
    f_min: Annotated[
        float | None, typer.Option("--f-min", help="Minimum frequency for fitting range in GHz")
    ] = None,
    f_max: Annotated[
        float | None, typer.Option("--f-max", help="Maximum frequency for fitting range in GHz")
    ] = None,
    bias_index: Annotated[
        int | None,
        typer.Option("--bias-index", "-b", help="L_jun bias slice index (default: fit ALL slices)"),
    ] = None,
) -> None:
    """
    Perform a complex resonance fit (Notch model) on a dataset's S-parameters.

    The dataset must contain matching data records for the specified parameter
    in representations that allow for building the complex signal (e.g. Re/Im or Mag/Phase).

    If the data contains multiple bias points (L_jun), all slices are fitted by default.
    Use --bias-index to select a specific slice.
    """
    service = ResonanceFitService()
    try:
        console.print(
            f"[cyan]Initiating resonance fit[/cyan] on dataset: [bold]{dataset_identifier}[/bold]"
        )
        console.print(f"Targeting Parameter: [bold]{parameter}[/bold]")

        result = service.perform_fit(
            dataset_identifier=dataset_identifier,
            parameter=parameter,
            model=model,
            resonators=resonators,
            f_min=f_min,
            f_max=f_max,
            bias_index=bias_index,
        )

        # Normalize to a list of slices for uniform handling
        if "slices" in result:
            slices = result["slices"]
            console.print(f"[green]Fit completed for {len(slices)} bias slices![/green]\n")
        else:
            slices = [result]
            console.print("[green]Fit completed successfully![/green]\n")

        for sr in slices:
            # Print bias header if L_jun info is available
            bi = sr.get("bias_index", 0)
            l_jun = sr.get("l_jun")
            if l_jun is not None:
                console.print(
                    f"[bold cyan]━━━ Bias Index {bi} │ L_jun = {l_jun:.4f} nH ━━━[/bold cyan]"
                )
            elif len(slices) > 1:
                console.print(f"[bold cyan]━━━ Bias Index {bi} ━━━[/bold cyan]")

            console.print("[bold]Extracted Parameters:[/bold]")

            if model in ["notch", "transmission"]:
                console.print(f"  Resonance Frequency (fr): {sr['fr'] / 1e9:.6f} GHz")
                console.print(f"  Loaded Q (Ql)         : {sr['Ql']:.2f}")
                if "Qi" in sr:
                    console.print(f"  Internal Q (Qi)       : {sr['Qi']:.2f}")
                if "Qc_mag" in sr:
                    console.print(f"  Coupling Q (Qc)       : {sr['Qc_mag']:.2f}")
                if "tau" in sr:
                    console.print(f"  Elec. Delay (tau)     : {sr['tau'] * 1e9:.4f} ns")
            elif model == "vf":
                console.print("  [green]Physical Resonances:[/green]")
                if not sr["resonances"]:
                    console.print("    None found")
                for idx, res in enumerate(sr["resonances"]):
                    console.print(
                        f"    Resonator {idx}: fr = {res['fr'] / 1e9:.6f} GHz, Ql = {res['Ql']:.2f}"
                    )

                artifacts = sr.get("artifacts", [])
                if artifacts:
                    console.print("  [yellow]Mathematical/Artifact Poles (Filtered):[/yellow]")
                    for idx, res in enumerate(artifacts):
                        console.print(
                            f"    Pole {idx}: fr = {res['fr'] / 1e9:.6f} GHz, Ql = {res['Ql']:.2f}"
                        )

            console.print(f"  Model Cost            : {sr['cost']:.4e}\n")

        console.print("[cyan]These have been saved as Derived Parameters to the database.[/cyan]")

        # Visualization — plot the last (or only) slice
        plot_slice = slices[-1]
        console.print("\n[yellow]Generating interactive Plotly visualization...[/yellow]")
        import numpy as np
        import plotly.graph_objects as go

        data_payload = plot_slice["data"]
        f_ghz = data_payload["f"] / 1e9
        s21_raw = data_payload["s21_raw"]
        s21_fit = data_payload["s21_model"]

        fig = go.Figure()

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

        # Add vertical markers for extracted resonance frequencies
        if model in ["notch", "transmission"]:
            fr_ghz = plot_slice["fr"] / 1e9
            fig.add_vline(
                x=fr_ghz,
                line_dash="dash",
                line_color="green",
                annotation_text=f"fr: {fr_ghz:.4f} GHz",
            )
        elif model == "vf":
            for res in plot_slice["resonances"]:
                fr_ghz = res["fr"] / 1e9
                fig.add_vline(x=fr_ghz, line_dash="dash", line_color="green")

        # Build title with bias info
        bi = plot_slice.get("bias_index", 0)
        l_jun = plot_slice.get("l_jun")
        title_suffix = ""
        if l_jun is not None:
            title_suffix = f" [b{bi}, L_jun={l_jun:.4f} nH]"
        elif len(slices) > 1:
            title_suffix = f" [b{bi}]"

        fig.update_layout(
            title=f"Resonance Fit ({model}): {dataset_identifier} ({parameter}){title_suffix}",
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


def main() -> None:
    setup_logging(level="WARNING")
    app()


if __name__ == "__main__":
    main()
