from pathlib import Path

from typer.testing import CliRunner

from sc_cli.app import app


def test_preview_artifacts_command_lists_sc_core_exports() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["core", "preview-artifacts"])

    assert result.exit_code == 0
    assert "sc_core preview artifacts:" in result.stdout
    assert "definition.normalized.json" in result.stdout
    assert "parameter-bundle.toml" in result.stdout


def test_circuit_definition_inspect_command_delegates_to_sc_core(tmp_path: Path) -> None:
    source_file = tmp_path / "demo.circuit.yaml"
    source_file.write_text(
        "\n".join(
            [
                "name: fluxonium_demo",
                "family: fluxonium",
                "junction_1: JJ",
                "capacitor_1: C",
                "inductor_1: L",
            ]
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(app, ["circuit-definition", "inspect", str(source_file)])

    assert result.exit_code == 0
    assert f"source_file: {source_file.resolve()}" in result.stdout
    assert "circuit_name: fluxonium_demo" in result.stdout
    assert "family: fluxonium" in result.stdout
    assert '"schemdraw_ready": true' in result.stdout
    assert "Port mapping metadata still needs migration from legacy forms." in result.stdout
