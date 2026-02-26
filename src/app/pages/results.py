"""Results page for SC Tutorial App — Derived Parameters Dashboard."""

from __future__ import annotations

import re
from collections import defaultdict

import pandas as pd
from nicegui import app, ui

from app.layout import app_shell
from core.shared.persistence import get_unit_of_work
from core.shared.persistence.models import ParameterDesignation

# ---------------------------------------------------------------------------
# Human-readable labels for analysis methods
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

# Parameters that should be displayed as "hero" metric cards
HERO_PARAMS = {"fr_ghz", "Qi", "Qc", "Ql", "electrical_delay"}

# Regex to parse bias suffix  e.g.  fr_ghz_0_b3 → base="fr_ghz_0", bias=3
_BIAS_RE = re.compile(r"^(.+?)_b(\d+)$")
# Regex to parse resonator index  e.g.  Qc_2 → base="Qc", idx=2
_IDX_RE = re.compile(r"^(.+?)_(\d+)$")


# ── Helpers ──────────────────────────────────────────────────────────────────


def _group_by_method(params):
    """Group a list of DerivedParameter objects by their `method` field."""
    groups: dict[str, list] = defaultdict(list)
    for p in params:
        groups[p.method or "unknown"].append(p)
    return dict(sorted(groups.items()))


def _build_bias_dataframe(params) -> pd.DataFrame | None:
    """
    If parameters follow the ``{base}_b{N}`` pattern, pivot them into a
    DataFrame with rows=base and columns=bias index.
    L_jun parameters are extracted to build meaningful column headers.
    Row labels like ``fr_ghz_0`` are converted to ``Mode 0 (GHz)``.
    """
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
        # non-bias params are ignored here

    if not rows:
        return None

    df = pd.DataFrame.from_dict(rows, orient="index")
    # Sort columns numerically by bias index
    df = df.reindex(sorted(df.columns), axis=1)

    # --- Build column headers ---
    if l_jun_values:
        col_map = {
            b: f"{l_jun_values[b]:.4g} ({l_jun_unit})" for b in df.columns if b in l_jun_values
        }
        # Fallback for any bias columns without a matching L_jun
        col_map.update({b: f"B{b}" for b in df.columns if b not in col_map})
    else:
        col_map = {b: f"B{b}" for b in df.columns}
    df = df.rename(columns=col_map)

    # --- Rename row indices: fr_ghz_0 → Mode 0 (GHz) ---
    _MODE_ROW_RE = re.compile(r"^fr_ghz_(\d+)$")
    new_index = []
    for idx in df.index:
        m = _MODE_ROW_RE.match(idx)
        if m:
            new_index.append(f"Mode {m.group(1)} (GHz)")
        else:
            new_index.append(idx)
    df.index = new_index
    df.index.name = "Parameter"
    return df


def _build_resonator_table(params) -> pd.DataFrame | None:
    """
    If parameters follow ``{param}_{idx}`` pattern, pivot them into
    rows = resonator index, columns = parameter type.
    """
    cells: dict[int, dict[str, float]] = defaultdict(dict)
    scalars = []
    for p in params:
        m = _BIAS_RE.match(p.name)
        if m:
            # Skip bias-indexed params here; they get their own table
            continue
        m2 = _IDX_RE.match(p.name)
        if m2:
            base, idx = m2.group(1), int(m2.group(2))
            cells[idx][base] = p.value
        else:
            scalars.append(p)

    if not cells:
        return None

    df = pd.DataFrame.from_dict(cells, orient="index")
    df.index.name = "Resonator"
    df = df.sort_index()
    # Sort columns in a nice order
    preferred = ["fr_ghz", "Qi", "Qc", "Ql"]
    cols_ordered = [c for c in preferred if c in df.columns]
    cols_ordered += [c for c in sorted(df.columns) if c not in cols_ordered]
    return df[cols_ordered]


# ── Renderers ────────────────────────────────────────────────────────────────


def _render_metric_cards(params):
    """Render a small set of params as summary metric cards (hero style)."""
    with ui.row().classes("w-full gap-4 flex-wrap"):
        for p in sorted(params, key=lambda x: x.name):
            with ui.column().classes("app-card p-4 min-w-[140px] flex-grow flex-shrink"):
                ui.label(p.name).classes("text-xs text-muted font-bold uppercase")
                if isinstance(p.value, float):
                    val = f"{p.value:.4g}"
                else:
                    val = str(p.value)
                with ui.row().classes("items-baseline gap-1 mt-1"):
                    ui.label(val).classes("text-xl font-bold text-fg")
                    if p.unit:
                        ui.label(p.unit).classes("text-xs text-muted")


def _render_aggrid_df(df: pd.DataFrame, suppress_auto_header: bool = False):
    """Render a pandas DataFrame as a compact AG Grid."""
    display = df.copy()
    # Round floats for readability
    for col in display.columns:
        if display[col].dtype == float:
            display[col] = display[col].apply(lambda v: f"{v:.4g}" if pd.notna(v) else "—")
    display = display.reset_index()

    grid_options = {
        "domLayout": "autoHeight",
        "defaultColDef": {"sortable": True, "resizable": True},
    }
    if suppress_auto_header:
        # Prevent AG Grid from inserting spaces into column names
        grid_options["defaultColDef"]["headerValueGetter"] = None

    grid = ui.aggrid.from_pandas(display).classes("w-full")
    grid.props("domLayout='autoHeight'")
    # Override column defs to preserve exact header text
    if suppress_auto_header:
        col_defs = [{"headerName": str(c), "field": str(c)} for c in display.columns]
        grid.options["columnDefs"] = col_defs
        grid.update()


def _render_bias_plotly(df: pd.DataFrame):
    """Render the bias-sweep DataFrame as a Plotly scatter plot (lines+markers)."""
    import plotly.graph_objects as go

    from core.shared.visualization import get_plotly_layout

    x_labels = list(df.columns)
    # Try to extract purely numeric x-values for a proper linear scale if possible,
    # otherwise fallback to categorical x-axis using the raw strings.
    x_numeric = []
    has_valid_numeric_x = False
    for label in x_labels:
        try:
            # e.g., "18.5 (nH)" -> 18.5
            val = float(str(label).split()[0])
            x_numeric.append(val)
        except (ValueError, IndexError):
            x_numeric.append(label)

    # Check if all x values are numeric (meaning we successfully parsed all of them)
    if all(isinstance(x, (int, float)) for x in x_numeric):
        x_data = x_numeric
        has_valid_numeric_x = True
    else:
        x_data = x_labels

    fig = go.Figure()

    for idx, row in df.iterrows():
        # idx is typically "Mode X (GHz)"
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

    # Base layout
    layout_args = dict(
        xaxis_title="L_jun (nH)" if has_valid_numeric_x else "Bias Index",
        yaxis_title="Frequency (GHz)",
        margin=dict(l=60, r=20, t=20, b=60),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Apply App Theme synchronization
    is_dark = app.storage.user.get("dark_mode", True)
    theme_layout = get_plotly_layout(dark=is_dark)
    layout_args.update(theme_layout)

    fig.update_layout(**layout_args)

    if not has_valid_numeric_x:
        fig.update_xaxes(type="category")

    ui.plotly(fig).classes("w-full")


def _render_method_section(ds, method: str, params: list):
    """
    Render one expandable section for a single analysis method.

    Strategy:
      1. Try to pivot bias-indexed params into a matrix table.
      2. Try to pivot resonator-indexed params into a summary table.
      3. Remaining scalar params → metric cards.
    """
    label = METHOD_LABELS.get(method, method)
    count = len(params)

    with (
        ui.expansion(f"{label}  ({count} parameters)", icon="analytics")
        .classes("w-full bg-surface rounded-xl")
        .props("default-opened header-class='text-fg font-bold'")
    ):
        # --- Bias-indexed matrix with Table/Plot toggle ---
        bias_df = _build_bias_dataframe(params)
        if bias_df is not None and not bias_df.empty:
            with ui.row().classes("w-full items-center justify-between mt-2 mb-2"):
                ui.label("Bias-Sweep Results").classes(
                    "text-xs text-muted font-bold uppercase tracking-wider"
                )
                # Enlarged toggle button for better UX
                toggle = ui.toggle(["Table", "Plot"], value="Table").props(
                    "size=md no-caps outline color=primary"
                )

            with ui.column().classes("w-full") as bias_container:

                @ui.refreshable
                def render_bias_view():
                    if toggle.value == "Table":
                        _render_aggrid_df(bias_df, suppress_auto_header=True)
                    else:
                        _render_bias_plotly(bias_df)

                toggle.on_value_change(lambda _: render_bias_view.refresh())
                render_bias_view()

        # --- Resonator summary table ---
        resonator_df = _build_resonator_table(params)
        if resonator_df is not None and not resonator_df.empty:
            ui.label("Per-Resonator Summary").classes(
                "text-xs text-muted font-bold uppercase tracking-wider mt-4 mb-1"
            )
            _render_aggrid_df(resonator_df)

        # --- Scalar / hero cards ---
        scalars = [p for p in params if not _BIAS_RE.match(p.name) and not _IDX_RE.match(p.name)]
        if scalars:
            ui.label("Summary Metrics").classes(
                "text-xs text-muted font-bold uppercase tracking-wider mt-4 mb-1"
            )
            _render_metric_cards(scalars)

        # --- Parameter Designation UI ---
        ui.separator().classes("my-4 bg-border")
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Assign Semantic Tag").classes(
                "text-xs text-muted font-bold uppercase tracking-wider"
            )

        with ui.row().classes(
            "w-full items-end gap-4 mt-2 p-4 bg-bg rounded-xl border border-border"
        ):
            _MODE_ROW_RE = re.compile(r"^fr_ghz_(\d+)$")

            def format_param_name(name: str) -> str:
                m_bias = _BIAS_RE.match(name)
                if m_bias:
                    base, b_idx = m_bias.group(1), m_bias.group(2)
                    m_mode = _MODE_ROW_RE.match(base)
                    base_label = f"Mode {m_mode.group(1)} (GHz)" if m_mode else base
                    return f"{base_label} [b{b_idx}]"

                m_idx = _IDX_RE.match(name)
                if m_idx:
                    base, idx = m_idx.group(1), m_idx.group(2)
                    m_mode = _MODE_ROW_RE.match(base)
                    base_label = f"Mode {m_mode.group(1)} (GHz)" if m_mode else base
                    return f"{base_label} [Res {idx}]"

                m_mode = _MODE_ROW_RE.match(name)
                return f"Mode {m_mode.group(1)} (GHz)" if m_mode else name

            param_options = {p.name: format_param_name(p.name) for p in params}
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
                tag_select = ui.select(
                    tag_options, label="Designated Metric", with_input=True
                ).classes("w-64")

                def save_designation():
                    if not source_select.value or not tag_select.value:
                        ui.notify("Please select both a parameter and a tag", type="warning")
                        return

                    # Strip descriptive suffix if standard option was selected
                    true_tag = tag_select.value.split(" (")[0].strip()

                    try:
                        with get_unit_of_work() as uow:
                            # 1. Check if this exact designation already exists to avoid duplicates
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


# ── Per-Dataset Tab Content ──────────────────────────────────────────────────


def _render_dataset_tab(ds, params):
    """Render the full derived-results view for one dataset."""
    if not params:
        with ui.column().classes(
            "w-full p-8 items-center justify-center border-2 border-dashed border-border rounded-xl"
        ):
            ui.icon("science", size="xl").classes("text-muted mb-4 opacity-50")
            ui.label("No derived results yet").classes("text-lg font-bold text-fg")
            ui.label("Run an analysis from the Analysis page first.").classes(
                "text-sm text-muted mt-1"
            )
        return

    method_groups = _group_by_method(params)
    for method, mparams in method_groups.items():
        _render_method_section(ds, method, mparams)


# ── Cross-Dataset Comparison ────────────────────────────────────────────────


def _render_cross_dataset(dataset_params: dict[str, list]):
    """
    Build a comparison table for methods that appear across multiple datasets.
    Shows one table per shared method, with datasets as rows.
    """
    # Collect methods per dataset
    method_datasets: dict[str, list[str]] = defaultdict(list)
    for ds_name, params in dataset_params.items():
        for method in {p.method for p in params}:
            method_datasets[method].append(ds_name)

    # Keep only methods appearing in ≥2 datasets
    shared = {m: ds_list for m, ds_list in method_datasets.items() if len(ds_list) >= 2}

    if not shared:
        with ui.column().classes(
            "w-full p-8 items-center justify-center border-2 border-dashed border-border rounded-xl"
        ):
            ui.label("No common analysis methods found").classes("text-lg font-bold text-fg")
            ui.label("Run the same analysis on multiple datasets to compare.").classes(
                "text-sm text-muted mt-1"
            )
        return

    for method in sorted(shared.keys()):
        label = METHOD_LABELS.get(method, method)
        ds_names = shared[method]

        with (
            ui.expansion(f"{label}  ({len(ds_names)} datasets)", icon="compare_arrows")
            .classes("w-full bg-surface rounded-xl")
            .props("default-opened header-class='text-fg font-bold'")
        ):
            # Build a comparison DataFrame: rows = datasets, cols = param names
            rows = {}
            for ds_name in ds_names:
                row = {}
                for p in dataset_params[ds_name]:
                    if p.method == method and not _BIAS_RE.match(p.name):
                        col = f"{p.name} [{p.unit}]" if p.unit else p.name
                        row[col] = p.value
                rows[ds_name] = row

            df = pd.DataFrame.from_dict(rows, orient="index")
            df.index.name = "Dataset"
            if not df.empty:
                _render_aggrid_df(df)


# ── Page Entry Point ─────────────────────────────────────────────────────────


@ui.page("/results")
def results_page():
    def content():
        ui.label("Derived Results").classes("text-2xl font-bold text-fg mb-2")

        selected_ids = app.storage.user.get("selected_datasets", [])

        if not selected_ids:
            with ui.column().classes(
                "w-full p-12 items-center justify-center "
                "border-2 border-dashed border-border rounded-xl"
            ):
                ui.icon("bar_chart", size="xl").classes("text-muted mb-4 opacity-50")
                ui.label("No Datasets Selected").classes("text-xl text-fg font-bold")
                ui.label("Select datasets from the header to view their results.").classes(
                    "text-sm text-muted mt-2"
                )
            return

        try:
            with get_unit_of_work() as uow:
                # Fetch all data upfront
                datasets = []
                dataset_params: dict[str, list] = {}
                for ds_id in selected_ids:
                    ds = uow.datasets.get(ds_id)
                    if not ds:
                        continue
                    datasets.append(ds)
                    dataset_params[ds.name] = uow.derived_params.list_by_dataset(ds_id)

                if not datasets:
                    ui.label("Selected datasets not found.").classes("text-danger")
                    return

                # ── Section 1: Per-Dataset Tabs ──────────────────────────
                ui.label("Per-Dataset Results").classes(
                    "text-xs font-bold text-muted tracking-widest uppercase mb-2"
                )

                if len(datasets) == 1:
                    # Single dataset — no tabs needed
                    ds = datasets[0]
                    _render_dataset_tab(ds, dataset_params[ds.name])
                else:
                    with ui.tabs().classes("w-full") as tabs:
                        tab_objects = []
                        for ds in datasets:
                            t = ui.tab(ds.name).classes("text-fg")
                            tab_objects.append(t)

                    with ui.tab_panels(tabs).classes("w-full bg-transparent"):
                        for ds, tab in zip(datasets, tab_objects):
                            with ui.tab_panel(tab):
                                _render_dataset_tab(ds, dataset_params[ds.name])

                # ── Section 2: Cross-Dataset Comparison ──────────────────
                if len(datasets) >= 2:
                    ui.separator().classes("my-8 bg-border")
                    ui.label("Cross-Dataset Comparison").classes(
                        "text-xs font-bold text-muted tracking-widest uppercase mb-2"
                    )
                    _render_cross_dataset(dataset_params)

        except Exception as e:
            ui.label(f"Error loading results: {e}").classes("text-danger")

    app_shell(content)()
