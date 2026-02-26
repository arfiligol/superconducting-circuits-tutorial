"""Characterization page — unified analysis + results view."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

import pandas as pd
from nicegui import app, ui

from app.layout import app_shell
from app.services.analysis_registry import (
    ANALYSIS_REGISTRY,
    get_available_analyses,
    is_analysis_completed,
)
from core.analysis.application.services.resonance_extract_service import ResonanceExtractService
from core.analysis.application.services.resonance_fit_service import ResonanceFitService
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import DerivedParameter, ParameterDesignation

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
METHOD_LABELS: dict[str, str] = {
    "admittance_zero_crossing": "Admittance Zero-Crossing",
    "complex_notch_fit_S21": "Complex Notch Fit (S21)",
    "complex_notch_fit_S11": "Complex Notch Fit (S11)",
    "transmission_fit_S21": "Transmission Fit (S21)",
    "transmission_fit_S11": "Transmission Fit (S11)",
    "vector_fit_S21": "Vector Fit (S21)",
    "vector_fit_S11": "Vector Fit (S11)",
}

_BIAS_RE = re.compile(r"^(.+?)_b(\d+)$")
_IDX_RE = re.compile(r"^(.+?)_(\d+)$")
_MODE_ROW_RE = re.compile(r"^fr_ghz_(\d+)$")


# ---------------------------------------------------------------------------
# Data helpers (from former parameters.py)
# ---------------------------------------------------------------------------


def _group_by_method(params):
    groups: dict[str, list] = defaultdict(list)
    for p in params:
        groups[p.method or "unknown"].append(p)
    return dict(sorted(groups.items()))


def _build_bias_dataframe(params) -> pd.DataFrame | None:
    rows: dict[str, dict[int, float]] = defaultdict(dict)
    l_jun_values: dict[int, float] = {}
    l_jun_unit: str = "nH"

    for p in params:
        m = _BIAS_RE.match(p.name)
        if m:
            base, bias = m.group(1), int(m.group(2))
            if base == "L_jun":
                l_jun_values[bias] = p.value
                if p.unit:
                    l_jun_unit = p.unit
            else:
                rows[base][bias] = p.value

    if not rows:
        return None

    df = pd.DataFrame.from_dict(rows, orient="index")
    df = df.reindex(sorted(df.columns), axis=1)

    if l_jun_values:
        col_map = {
            b: f"{l_jun_values[b]:.4g} ({l_jun_unit})" for b in df.columns if b in l_jun_values
        }
        col_map.update({b: f"B{b}" for b in df.columns if b not in col_map})
    else:
        col_map = {b: f"B{b}" for b in df.columns}
    df = df.rename(columns=col_map)

    new_index = []
    for idx in df.index:
        m = _MODE_ROW_RE.match(idx)
        new_index.append(f"Mode {m.group(1)} (GHz)" if m else idx)
    df.index = new_index
    df.index.name = "Parameter"
    return df


def _build_resonator_table(params) -> pd.DataFrame | None:
    cells: dict[int, dict[str, float]] = defaultdict(dict)
    for p in params:
        if _BIAS_RE.match(p.name):
            continue
        m2 = _IDX_RE.match(p.name)
        if m2:
            base, idx = m2.group(1), int(m2.group(2))
            cells[idx][base] = p.value

    if not cells:
        return None

    df = pd.DataFrame.from_dict(cells, orient="index")
    df.index.name = "Resonator"
    df = df.sort_index()
    preferred = ["fr_ghz", "Qi", "Qc", "Ql"]
    cols_ordered = [c for c in preferred if c in df.columns]
    cols_ordered += [c for c in sorted(df.columns) if c not in cols_ordered]
    return df[cols_ordered]


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _render_aggrid_df(df: pd.DataFrame, suppress_auto_header: bool = False):
    display = df.copy()
    for col in display.columns:
        if display[col].dtype == float:
            display[col] = display[col].apply(lambda v: f"{v:.4g}" if pd.notna(v) else "—")
    display = display.reset_index()

    grid = ui.aggrid.from_pandas(display).classes("w-full")
    grid.props("domLayout='autoHeight'")
    if suppress_auto_header:
        col_defs = [{"headerName": str(c), "field": str(c)} for c in display.columns]
        grid.options["columnDefs"] = col_defs
        grid.update()


def _render_metric_cards(params):
    with ui.row().classes("w-full gap-4 flex-wrap"):
        for p in sorted(params, key=lambda x: x.name):
            with ui.column().classes("app-card p-4 min-w-[140px] flex-grow flex-shrink"):
                ui.label(p.name).classes("text-xs text-muted font-bold uppercase")
                val = f"{p.value:.4g}" if isinstance(p.value, float) else str(p.value)
                with ui.row().classes("items-baseline gap-1 mt-1"):
                    ui.label(val).classes("text-xl font-bold text-fg")
                    if p.unit:
                        ui.label(p.unit).classes("text-xs text-muted")


def _render_bias_plotly(df: pd.DataFrame):
    import plotly.graph_objects as go

    from core.shared.visualization import get_plotly_layout

    x_labels = list(df.columns)
    x_numeric = []
    has_valid_numeric_x = False
    for label in x_labels:
        try:
            val = float(str(label).split()[0])
            x_numeric.append(val)
        except (ValueError, IndexError):
            x_numeric.append(label)

    if all(isinstance(x, (int, float)) for x in x_numeric):
        x_data = x_numeric
        has_valid_numeric_x = True
    else:
        x_data = x_labels

    fig = go.Figure()
    for idx, row in df.iterrows():
        mode_label = str(idx).replace(" (GHz)", "")
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=row.values,
                mode="lines+markers",
                name=mode_label,
                hovertemplate=(
                    f"<b>{mode_label}</b><br>Bias: %{{x}}<br>Freq: %{{y:.4g}} GHz<extra></extra>"
                ),
            )
        )

    layout_args = dict(
        title="Mode Frequencies vs. Bias",
        xaxis_title="L_jun (nH)" if has_valid_numeric_x else "Bias Index",
        yaxis_title="Frequency (GHz)",
        margin=dict(l=60, r=150, t=60, b=60),
        height=400,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
    )

    is_dark = app.storage.user.get("dark_mode", True)
    theme_layout = get_plotly_layout(dark=is_dark)
    layout_args.update(theme_layout)

    fig.update_layout(**layout_args)
    if not has_valid_numeric_x:
        fig.update_xaxes(type="category")

    ui.plotly(fig).classes("w-full")


# ---------------------------------------------------------------------------
# Identify Mode UI
# ---------------------------------------------------------------------------


def _render_identify_mode(ds, method: str, params: list, bias_df):
    """Render the Identify Mode UI for tagging modes with physical meaning."""
    ui.separator().classes("my-4 bg-border")
    with ui.row().classes("w-full items-center justify-between"):
        ui.label("Identify Mode").classes("text-xs text-muted font-bold uppercase tracking-wider")

    with ui.row().classes("w-full items-end gap-4 mt-2 p-4 bg-bg rounded-xl border border-border"):

        def extract_base_param(name: str) -> str:
            m_bias = _BIAS_RE.match(name)
            if m_bias:
                return m_bias.group(1)
            m_idx = _IDX_RE.match(name)
            if m_idx:
                return m_idx.group(1)
            return name

        def format_base_param(base_name: str) -> str:
            m_mode = _MODE_ROW_RE.match(base_name)
            return f"Mode {m_mode.group(1)} (GHz)" if m_mode else base_name

        unique_bases = {extract_base_param(p.name) for p in params}
        param_options = {base: format_base_param(base) for base in sorted(unique_bases)}

        if not param_options:
            ui.label("No parameters to tag").classes("text-muted text-sm")
        else:
            source_select = ui.select(param_options, label="Source Parameter").classes("w-64")

            tag_options = [
                "f_q (Qubit frequency)",
                "f_r (Readout frequency)",
                "alpha (Anharmonicity)",
                "g (Coupling strength)",
            ]
            tag_select = ui.select(tag_options, label="Designated Metric", with_input=True).classes(
                "w-64"
            )

            def save_designation():
                if not source_select.value or not tag_select.value:
                    ui.notify("Please select both a parameter and a tag", type="warning")
                    return

                true_tag = tag_select.value.split(" (")[0].strip()

                try:
                    with get_unit_of_work() as uow:
                        existing = (
                            uow._session.query(ParameterDesignation)
                            .filter_by(
                                dataset_id=ds.id,
                                designated_name=true_tag,
                                source_analysis_type=method,
                                source_parameter_name=source_select.value,
                            )
                            .first()
                        )

                        if existing:
                            ui.notify(
                                f"Tag '{true_tag}' already exists for {source_select.value}",
                                type="info",
                            )
                            return

                        desig = ParameterDesignation(
                            dataset_id=ds.id,
                            designated_name=true_tag,
                            source_analysis_type=method,
                            source_parameter_name=source_select.value,
                        )
                        uow._session.add(desig)
                        uow.commit()
                        ui.notify(
                            f"Successfully designated {source_select.value} as '{true_tag}'",
                            type="positive",
                        )

                        source_select.value = None
                        tag_select.value = None
                except Exception as e:
                    ui.notify(f"Error saving designation: {e}", type="negative")

            ui.button("Tag Parameter", icon="sell", on_click=save_designation).props(
                "outline color=primary size=sm"
            ).classes("mb-1")


# ---------------------------------------------------------------------------
# Results body inside each card
# ---------------------------------------------------------------------------


def _render_results_body(ds, method_key: str, method_params: list):
    """Render results for one analysis method inside its card."""

    # Render config context if any
    extra_config = method_params[0].extra if method_params and method_params[0].extra else {}
    if extra_config:
        with ui.row().classes("w-full gap-2 mb-4 bg-bg p-3 rounded-lg border border-border"):
            ui.icon("tune", size="xs").classes("text-muted")
            for k, v in extra_config.items():
                if v is not None:
                    ui.label(f"{k}: {v}").classes(
                        "text-xs text-muted font-mono bg-surface px-2 py-0.5 rounded"
                    )

    bias_df = _build_bias_dataframe(method_params)
    if bias_df is not None and not bias_df.empty:
        with ui.row().classes("w-full items-center justify-between mt-2 mb-2"):
            ui.label("Bias-Sweep Results").classes(
                "text-xs text-muted font-bold uppercase tracking-wider"
            )
            toggle = ui.toggle(["Table", "Plot"], value="Table").props(
                "size=md no-caps outline color=primary"
            )

        with ui.column().classes("w-full"):

            @ui.refreshable
            def render_bias_view():
                if toggle.value == "Table":
                    _render_aggrid_df(bias_df, suppress_auto_header=True)
                else:
                    _render_bias_plotly(bias_df)

            toggle.on_value_change(lambda _: render_bias_view.refresh())
            render_bias_view()

    resonator_df = _build_resonator_table(method_params)
    if resonator_df is not None and not resonator_df.empty:
        ui.label("Per-Resonator Summary").classes(
            "text-xs text-muted font-bold uppercase tracking-wider mt-4 mb-1"
        )
        _render_aggrid_df(resonator_df)

    scalars = [p for p in method_params if not _BIAS_RE.match(p.name) and not _IDX_RE.match(p.name)]
    if scalars:
        ui.label("Summary Metrics").classes(
            "text-xs text-muted font-bold uppercase tracking-wider mt-4 mb-1"
        )
        _render_metric_cards(scalars)

    # Identify Mode UI
    _render_identify_mode(ds, method_key, method_params, bias_df)


# ---------------------------------------------------------------------------
# Unified Analysis Card
# ---------------------------------------------------------------------------


def _render_analysis_card(
    ds,
    analysis: dict[str, Any],
    is_available: bool,
    method_params: list,
    refresh_fn,
):
    """Render a single full-width analysis card with Run button + results."""
    completed = len(method_params) > 0

    with ui.card().classes("w-full bg-surface rounded-xl p-6"):
        # ── Header row: icon + title + status + Run button ──
        with ui.row().classes("w-full items-center justify-between mb-2"):
            with ui.row().classes("items-center gap-2"):
                ui.icon(analysis["icon"], size="sm").classes("text-primary")
                ui.label(analysis["label"]).classes("text-lg font-bold text-fg")
                if completed:
                    with ui.row().classes("items-center gap-1 ml-2"):
                        ui.icon("check_circle", size="xs").classes("text-positive")
                        ui.label(f"{len(method_params)} params").classes(
                            "text-xs text-positive font-bold"
                        )

            # Run button — always visible
            if is_available:

                async def do_run(a=analysis, d=ds):
                    try:
                        ui.notify(f"Starting {a['label']}...", type="info")
                        if a["id"] == "admittance_extraction":
                            ResonanceExtractService().extract_admittance(str(d.id))
                        elif a["id"] == "s21_resonance_fit":
                            # Extract user parameters and pass them
                            ResonanceFitService().perform_fit(
                                dataset_identifier=str(d.id),
                                parameter="S21",
                                model=params.get("model", "notch"),
                                resonators=int(params.get("resonators", 1) or 1),
                                f_min=params.get("f_min"),
                                f_max=params.get("f_max"),
                            )
                        elif a["id"] in ("squid_fitting", "y11_fit"):
                            ui.notify(f"{a['label']} – not yet implemented.", type="warning")
                            return
                        ui.notify(f"{a['label']} complete!", type="positive")
                        refresh_fn()
                    except Exception as e:
                        ui.notify(f"Failed: {e!s}", type="negative")

                run_label = "🔁 Re-run" if completed else "▶ Run"
                ui.button(run_label, on_click=do_run).props(
                    "unelevated color=primary size=md"
                ).classes("px-4 font-bold")
            else:
                ui.label("Missing required data").classes("text-xs text-danger font-semibold")

        # ── Description ──
        ui.label(analysis["description"]).classes("text-sm text-muted mb-2")

        # ── Config fields (for manual analyses) ──
        config_fields = analysis.get("config_fields", [])
        if config_fields and is_available:
            with ui.row().classes("w-full gap-4 mb-2"):
                for field in config_fields:
                    if field["type"] == "select":
                        ui.select(
                            options=field["options"],
                            value=field.get("default"),
                            label=field["label"],
                        ).props("dense outline").classes("w-40")
                    elif field["type"] == "number":
                        ui.number(label=field["label"], value=field.get("default")).props(
                            "dense outline"
                        ).classes("w-32")

        # ── Results body ──
        ui.separator().classes("my-2 bg-border")
        if completed:
            _render_results_body(ds, method_params[0].method, method_params)
        else:
            with ui.column().classes("w-full py-8 items-center justify-center"):
                ui.icon("hourglass_empty", size="md").classes("text-muted opacity-40 mb-2")
                ui.label("Not yet analyzed").classes("text-sm text-muted")


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------


@ui.page("/characterization")
def characterization_page():
    def content():
        ui.label("Characterization").classes("text-2xl font-bold text-fg mb-6")

        selected_dataset_ids = app.storage.user.get("selected_datasets", [])

        if not selected_dataset_ids:
            with ui.column().classes(
                "w-full p-12 items-center justify-center "
                "border-2 border-dashed border-border rounded-xl"
            ):
                ui.icon("science", size="xl").classes("text-muted mb-4 opacity-50")
                ui.label("No Datasets Selected").classes("text-xl text-fg font-bold")
                ui.label("Select active datasets from the header or the Raw Data page.").classes(
                    "text-sm text-muted mt-2"
                )
            return

        try:
            with get_unit_of_work() as uow:
                ds_options = {}
                for ds_id in selected_dataset_ids:
                    ds = uow.datasets.get(ds_id)
                    if ds:
                        ds_options[ds_id] = ds.name

                if not ds_options:
                    ui.label("Error: Active datasets not found.").classes("text-danger")
                    return

                current_ds_id = app.storage.user.get("analysis_current_dataset")
                if current_ds_id not in ds_options:
                    current_ds_id = list(ds_options.keys())[0]
                    app.storage.user["analysis_current_dataset"] = current_ds_id

                @ui.refreshable
                def render_dataset_view():
                    active_id = app.storage.user.get("analysis_current_dataset")
                    if not active_id or active_id not in ds_options:
                        return

                    ds = uow.datasets.get(active_id)
                    if not ds:
                        return

                    records = [
                        {
                            "data_type": r.data_type,
                            "parameter": r.parameter,
                            "representation": r.representation,
                        }
                        for r in uow.data_records.list_all()
                        if r.dataset_id == active_id
                    ]

                    available = get_available_analyses(records)
                    available_ids = {a["id"] for a in available}
                    ds_params = uow.derived_params.list_by_dataset(active_id)

                    # Group params by method
                    method_params = _group_by_method(ds_params)

                    with ui.column().classes("w-full gap-4"):
                        for analysis in ANALYSIS_REGISTRY:
                            if analysis["scope"] != "per_dataset":
                                continue

                            # Collect params belonging to this analysis's completed_methods
                            completed_methods = set(analysis.get("completed_methods", []))
                            card_params = []
                            for mk, mp in method_params.items():
                                if mk in completed_methods:
                                    card_params.extend(mp)

                            _render_analysis_card(
                                ds=ds,
                                analysis=analysis,
                                is_available=analysis["id"] in available_ids,
                                method_params=card_params,
                                refresh_fn=render_dataset_view.refresh,
                            )

                # --- Layout ---
                with ui.row().classes("w-full items-center gap-4 mb-4"):
                    ui.label("Dataset:").classes("text-sm font-bold text-fg")

                    def on_change(e):
                        app.storage.user["analysis_current_dataset"] = e.value
                        render_dataset_view.refresh()

                    ui.select(options=ds_options, value=current_ds_id, on_change=on_change).props(
                        "dense outline dark standout"
                    ).classes("w-64")

                render_dataset_view()

        except Exception as e:
            ui.label(f"Error loading characterization: {e}").classes("text-danger")

    app_shell(content)()
