#!/usr/bin/env python3
"""
Unified Hierarchical CLI for Superconducting Circuits Analysis.
Entry point for `sc` command.
"""

import typer

# Import command modules
# Note: We import the 'main' function for single-command scripts,
# and the 'app' object for multi-command scripts (like manage_db).
from scripts.analysis import manage_analysis, manage_resonance_extract, squid_fit
from scripts.database import manage_db
from scripts.docs import generate_cli_reference, sync_cli_reference
from scripts.plot import admittance, flux_dependence, resonance_map
from scripts.preprocessing import (
    convert_flux_dependence,
    convert_hfss_admittance,
    convert_hfss_scattering,
)
from scripts.simulation import run_lc

# Main App
app = typer.Typer(
    help="Superconducting Circuits Analysis Platform CLI",
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# ==========================================
# 1. Analysis
# ==========================================
analysis_app = typer.Typer(help="Analysis and Fitting Tools")
app.add_typer(analysis_app, name="analysis")

# sc analysis fit ...
# Mount the fit sub-application (which contains 'lc-squid' command)
analysis_app.add_typer(squid_fit.app, name="fit")

# sc analysis resonance-fit ...
analysis_app.add_typer(
    manage_analysis.app, name="resonance-fit", help="Perform resonance fits on S-parameters."
)

# sc analysis resonance-extract ...
analysis_app.add_typer(
    manage_resonance_extract.app,
    name="resonance-extract",
    help="Extract resonance frequencies (non-fitting methods).",
)


# ==========================================
# 2. Preprocessing (Data Ingestion)
# ==========================================
preprocess_app = typer.Typer(help="Data Ingestion and Preprocessing")
app.add_typer(preprocess_app, name="preprocess")

# --- VNA Subgroup ---
vna_app = typer.Typer(help="VNA Measurement Data Preprocessing")
preprocess_app.add_typer(vna_app, name="vna")

# sc preprocess vna flux-dependence ...
vna_app.command(name="flux-dependence", help="Import VNA Flux Dependence TXT to DB.")(
    convert_flux_dependence.main
)

# --- HFSS Subgroup ---
hfss_app = typer.Typer(help="HFSS Simulation Data Preprocessing")
preprocess_app.add_typer(hfss_app, name="hfss")

# sc preprocess hfss admittance ...
hfss_app.command(name="admittance", help="Import HFSS Admittance Matrix CSV (Y-Param) to DB.")(
    convert_hfss_admittance.main
)

# sc preprocess hfss scattering ...
hfss_app.command(
    name="scattering", help="Import HFSS Scattering Matrix CSV (S-Param, Phase) to DB."
)(convert_hfss_scattering.main)


# ==========================================
# 3. Database
# ==========================================
# sc db ...
# manage_db.app already has subcommands: dataset-record, tag, etc.
app.add_typer(manage_db.app, name="db", help="Database Management")


# ==========================================
# 4. Simulation
# ==========================================
sim_app = typer.Typer(help="Julia-based Simulations")
app.add_typer(sim_app, name="sim")  # Alias 'simulation' if needed, but 'sim' is shorter

# sc sim lc ...
sim_app.command(name="lc", help="Simulate LC Circuit (Eigenmode).")(run_lc.main)


# ==========================================
# 5. Plotting
# ==========================================
plot_app = typer.Typer(help="Plotting and Visualization Tools")
app.add_typer(plot_app, name="plot")

# sc plot different-qubit-structure-frequency-comparison-table ...
plot_app.command(
    name="different-qubit-structure-frequency-comparison-table",
    help="Compare resonance frequencies across qubit structures (table-first).",
)(resonance_map.main)

# sc plot admittance ...
plot_app.command(
    name="admittance",
    help="Plot admittance records from DB (line views).",
)(admittance.main)

# sc plot flux-dependence ...
plot_app.command(
    name="flux-dependence",
    help="Plot flux-dependence maps and slices from DB.",
)(flux_dependence.main)

# Backward-compatible alias
plot_app.command(
    name="resonance-map",
    help="Alias of different-qubit-structure-frequency-comparison-table.",
    hidden=True,
)(resonance_map.main)


# ==========================================
# 6. Documentation
# ==========================================
docs_app = typer.Typer(help="Documentation Tooling")
app.add_typer(docs_app, name="docs")

# sc docs generate
docs_app.command(name="generate", help="Generate CLI Reference Markdown.")(
    generate_cli_reference.main
)

# sc docs sync
docs_app.command(name="sync", help="Sync CLI Reference frontmatter.")(sync_cli_reference.main)


if __name__ == "__main__":
    app()
