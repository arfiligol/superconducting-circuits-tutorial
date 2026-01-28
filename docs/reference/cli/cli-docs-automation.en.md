---
aliases:
  - "CLI Docs Automation"
  - "CLI 文件自動生成"
tags:
  - diataxis/reference
  - status/draft
  - audience/contributor
  - topic/cli
  - topic/documentation
owner: I-LI CHIU
---

# CLI Docs Automation

This page defines how to **automatically generate CLI Reference docs** and how they should be maintained.

## Current Status

`docs/reference/cli/` is still maintained manually. After the Typer migration, CLI Reference pages should be generated to avoid drift from the implementation.

## Goals

- Use CLI help output as the single source of truth
- Auto-generate `docs/reference/cli/*.md`
- Replace hand-written CLI Options content while keeping a minimal index and guidance pages

## Integration Rules

1. **Source**: Generate from each CLI command's `--help` output.
2. **Output**: Write to `docs/reference/cli/`.
3. **Manual content**: Keep only index and supplemental guidance pages; do not edit generated pages by hand.
4. **When to update**: Regenerate after any CLI parameter changes.

## Follow-ups (after Typer migration)

- Add a CLI docs generator (recommended location: `scripts/docs/`).
- Register a command entry in `pyproject.toml` (e.g., `sc-docs-cli`).
- Let generated output replace current CLI Reference pages (or replace the generated sections).

!!! note "Status"
    This workflow is not enabled yet. It will be activated after the Typer migration is complete.

## Related

- [CLI Reference](index.md)
