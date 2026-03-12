"""Installable Typer entrypoint for rewrite CLI commands."""

import typer

from sc_cli.commands import (
    characterization,
    circuit_definition,
    core,
    datasets,
    session,
    simulation,
    tasks,
)

app = typer.Typer(
    help="Rewrite CLI adapter for superconducting circuits workflows.",
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

app.add_typer(core.app, name="core", help="Inspect the shared core package boundary.")
app.add_typer(session.app, name="session", help="Inspect rewrite session state.")
app.add_typer(datasets.app, name="datasets", help="Inspect rewrite dataset state.")
app.add_typer(tasks.app, name="tasks", help="Inspect rewrite task state.")
app.add_typer(
    characterization.app,
    name="characterization",
    help="Operate on characterization-lane tasks.",
)
app.add_typer(simulation.app, name="simulation", help="Operate on simulation-lane tasks.")
app.add_typer(
    circuit_definition.app,
    name="circuit-definition",
    help="Inspect canonical circuit-definition inputs via sc_core.",
)
