#!/usr/bin/env python3
"""Generate CLI reference pages from `--help` output."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(add_completion=False)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT_DIR = REPO_ROOT / "docs" / "reference" / "cli" / "generated"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"


@dataclass(frozen=True)
class CommandSpec:
    name: str
    entrypoint: str


def load_project_scripts() -> list[CommandSpec]:
    """Load [project.scripts] from pyproject.toml."""
    import tomllib

    data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    scripts = data.get("project", {}).get("scripts", {})
    specs: list[CommandSpec] = []
    for name, entrypoint in scripts.items():
        specs.append(CommandSpec(name=name, entrypoint=entrypoint))
    return specs


def render_markdown_zh(command: str, help_text: str) -> str:
    """Render zh-TW reference page with frontmatter and help output."""
    return f"""---
aliases:
  - "{command} 指令參考"
  - "{command} CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# {command}

此頁面由自動化產生, 請勿手動編輯。

```text
{help_text.strip()}
```
"""


def render_markdown_en(command: str, help_text: str) -> str:
    """Render English reference page with frontmatter and help output."""
    return f"""---
aliases:
  - "{command} CLI Reference"
  - "{command} 指令參考"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/generated
owner: I-LI CHIU
---

# {command}

This page is auto-generated. Do not edit manually.

```text
{help_text.strip()}
```
"""


def collect_help(command: str) -> str:
    """Collect `--help` output using uv run."""
    result = subprocess.run(
        ["uv", "run", command, "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to run '{command} --help': {result.stderr.strip()}")
    return result.stdout or result.stderr


@app.command()
def main(
    output_dir: Annotated[
        Path,
        typer.Option(
            help="Output directory for generated CLI reference pages",
            dir_okay=True,
            file_okay=False,
        ),
    ] = DEFAULT_OUT_DIR,
    overwrite: Annotated[
        bool,
        typer.Option(help="Allow overwriting existing files"),
    ] = False,
    include: Annotated[
        list[str] | None,
        typer.Option(help="Only generate for specified commands"),
    ] = None,
    exclude: Annotated[
        list[str] | None,
        typer.Option(help="Skip specified commands"),
    ] = None,
) -> None:
    """Generate CLI reference docs from `--help` output."""
    include = include or []
    exclude = exclude or ["sc-docs-cli", "sc-docs-cli-sync"]

    specs = load_project_scripts()
    commands = [s.name for s in specs]

    if include:
        commands = [c for c in commands if c in include]

    if exclude:
        commands = [c for c in commands if c not in exclude]

    output_dir.mkdir(parents=True, exist_ok=True)

    for command in commands:
        help_text = collect_help(command)
        content_zh = render_markdown_zh(command, help_text)
        content_en = render_markdown_en(command, help_text)

        targets = [
            output_dir / f"{command}.md",
            output_dir / f"{command}.en.md",
        ]
        if any(t.exists() for t in targets) and not overwrite:
            typer.echo(f"Skip existing: {targets[0]}")
            continue
        targets[0].write_text(content_zh, encoding="utf-8")
        targets[1].write_text(content_en, encoding="utf-8")
        typer.echo(f"Wrote: {targets[0]}")
        typer.echo(f"Wrote: {targets[1]}")


if __name__ == "__main__":
    app()
