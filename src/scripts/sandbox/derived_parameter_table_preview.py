"""Sandbox: preview cross-dataset DerivedParameter table with Plotly."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated

import plotly.graph_objects as go
import typer

from core.shared.persistence import get_unit_of_work
from core.shared.persistence.database import DATABASE_PATH

app = typer.Typer(add_completion=False, help="Preview DerivedParameter table with Plotly.")


def _default_output_path() -> Path:
    reports_dir = DATABASE_PATH.parent / "processed" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return reports_dir / f"derived_parameter_table_preview_{stamp}.html"


def _to_float_text(value: float) -> str:
    return f"{value:.6g}"


def _load_rows(dataset_filters: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    missing_filters: list[str] = []

    with get_unit_of_work() as uow:
        dataset_map = {
            int(dataset.id): dataset.name
            for dataset in uow.datasets.list_all()
            if dataset.id is not None
        }

        selected_ids: set[int] | None = None
        if dataset_filters:
            selected_ids = set()
            for token in dataset_filters:
                if token.isdigit():
                    selected_ids.add(int(token))
                    continue
                dataset = uow.datasets.get_by_name(token)
                if dataset and dataset.id is not None:
                    selected_ids.add(int(dataset.id))
                else:
                    missing_filters.append(token)

        params = uow.derived_params.list_all()

    rows: list[dict[str, str]] = []
    for param in params:
        dataset_id = int(param.dataset_id)
        if selected_ids is not None and dataset_id not in selected_ids:
            continue
        rows.append(
            {
                "dataset_name": dataset_map.get(dataset_id, f"<missing:{dataset_id}>"),
                "dataset_id": str(dataset_id),
                "parameter": param.name,
                "value": _to_float_text(param.value),
                "unit": param.unit or "-",
                "device_type": str(param.device_type.value),
                "method": param.method or "-",
                "created_at": param.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    rows.sort(
        key=lambda row: (
            row["dataset_name"].casefold(),
            row["parameter"].casefold(),
            row["created_at"],
        )
    )
    return rows, missing_filters


def _mock_rows() -> list[dict[str, str]]:
    """Fallback rows so table style can still be previewed when DB is empty."""
    return [
        {
            "dataset_name": "HFSS_Qubit_A",
            "dataset_id": "101",
            "parameter": "L_s",
            "value": "2.15",
            "unit": "nH",
            "device_type": "qubit",
            "method": "model_fit",
            "created_at": "2026-02-10 09:30:00",
        },
        {
            "dataset_name": "HFSS_Qubit_A",
            "dataset_id": "101",
            "parameter": "C_eff",
            "value": "84.2",
            "unit": "fF",
            "device_type": "qubit",
            "method": "model_fit",
            "created_at": "2026-02-10 09:30:01",
        },
        {
            "dataset_name": "HFSS_Qubit_B",
            "dataset_id": "102",
            "parameter": "f_resonance",
            "value": "5.31",
            "unit": "GHz",
            "device_type": "qubit",
            "method": "admittance_peak",
            "created_at": "2026-02-10 09:35:00",
        },
    ]


def _build_table_figure(rows: list[dict[str, str]], title: str) -> go.Figure:
    column_keys = [
        "dataset_name",
        "dataset_id",
        "parameter",
        "value",
        "unit",
        "device_type",
        "method",
        "created_at",
    ]
    column_headers = [
        "Dataset",
        "Dataset ID",
        "Parameter",
        "Value",
        "Unit",
        "Device Type",
        "Method",
        "Created At (UTC)",
    ]
    column_values = [[row[key] for row in rows] for key in column_keys]

    fig = go.Figure(
        data=[
            go.Table(
                header={
                    "values": column_headers,
                    "align": "left",
                    "fill_color": "#2f3e46",
                    "font": {"color": "white", "size": 13},
                    "height": 30,
                },
                cells={
                    "values": column_values,
                    "align": "left",
                    "fill_color": [["#f8f9fa", "#ffffff"] * ((len(rows) + 1) // 2)],
                    "font": {"size": 12, "color": "#1f2933"},
                    "height": 28,
                },
                columnwidth=[240, 90, 130, 90, 70, 100, 130, 180],
            )
        ]
    )
    fig.update_layout(
        title={"text": title, "x": 0.01},
        template="plotly_white",
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
        height=max(300, 90 + 30 * len(rows)),
    )
    return fig


@app.command()
def main(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output HTML file path. Defaults to data/processed/reports/...",
        ),
    ] = None,
    png_output: Annotated[
        Path | None,
        typer.Option(
            "--png-output",
            help="Optional PNG output path (requires kaleido).",
        ),
    ] = None,
    dataset: Annotated[
        list[str] | None,
        typer.Option(
            "--dataset",
            "-d",
            help="Dataset filter by ID or name. Repeat option to include multiple datasets.",
        ),
    ] = None,
    mock_on_empty: Annotated[
        bool,
        typer.Option(
            "--mock-on-empty/--no-mock-on-empty",
            help="Render mock rows when no DerivedParameter exists in DB.",
        ),
    ] = True,
    show: Annotated[
        bool,
        typer.Option(
            "--show/--no-show",
            help="Open interactive Plotly preview in browser (fig.show()).",
        ),
    ] = True,
    save_html: Annotated[
        bool,
        typer.Option(
            "--save-html/--no-save-html",
            help="Save HTML output file.",
        ),
    ] = False,
) -> None:
    """Render a cross-dataset table for DerivedParameter values."""
    rows, missing_filters = _load_rows(dataset or [])

    if missing_filters:
        typer.echo(f"Warning: unknown dataset filters ignored: {', '.join(missing_filters)}")

    used_mock = False
    if not rows and mock_on_empty:
        rows = _mock_rows()
        used_mock = True

    if not rows:
        typer.echo("No DerivedParameter rows found. Nothing to render.")
        raise typer.Exit(code=1)

    title_suffix = " (mock data)" if used_mock else ""
    fig = _build_table_figure(rows, f"Derived Parameter Table Preview{title_suffix}")

    if show:
        fig.show()

    if save_html:
        output_path = output or _default_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path), include_plotlyjs="cdn")
        typer.echo(f"HTML written: {output_path.resolve()}")

    if png_output:
        png_output.parent.mkdir(parents=True, exist_ok=True)
        try:
            fig.write_image(str(png_output), width=1800, scale=2)
            typer.echo(f"PNG written: {png_output.resolve()}")
        except Exception as exc:  # pragma: no cover - dependency dependent
            typer.echo(f"PNG export skipped (kaleido missing or failed): {exc}")


if __name__ == "__main__":
    app()
