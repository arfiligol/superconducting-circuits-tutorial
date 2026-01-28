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

`docs/reference/cli/` uses a **hybrid model**: hand-written content plus an auto-generated help section. CLI help is generated and synced into the hand-written pages to prevent drift.

## Goals

- Use CLI help output as the single source of truth
- Auto-generate `docs/reference/cli/generated/*.md` (not rendered in nav)
- Sync help blocks into hand-written CLI Reference pages while keeping human-friendly content

## Integration Rules

1. **Source**: Generate help blocks from each CLI command's `--help` output.
2. **Generated location**: `docs/reference/cli/generated/` (not in nav).
3. **Sync**: Insert the help block into the `CLI Help (Auto-generated)` section in hand-written pages.
4. **When to update**: Regenerate and sync after any CLI parameter changes.

## Usage

1. Generate files under `generated/`:

```bash
uv run sc-docs-cli --output-dir docs/reference/cli/generated --overwrite
```

2. Sync help blocks into hand-written docs:

```bash
uv run sc-docs-cli-sync
```

3. Check consistency (CI-friendly):

```bash
uv run sc-docs-cli-sync --check
```

!!! note "Rendering"
    `docs/reference/cli/generated/` is the generated source only and is not rendered in nav.

## Related

- [CLI Reference](index.md)
