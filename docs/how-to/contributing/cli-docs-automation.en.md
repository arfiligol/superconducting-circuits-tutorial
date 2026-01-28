---
aliases:
  - "CLI Docs Automation"
  - "CLI 文件自動生成"
tags:
  - diataxis/how-to
  - status/draft
  - audience/contributor
  - topic/cli
  - topic/documentation
  - sot/true
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

## Hand-written Page Format (Required)

Hand-written pages must follow this structure (only the `CLI Help` block is auto-inserted):

1. **Title**: `# <command>`
2. **Intro**: one sentence describing purpose and scope
3. **Usage**: minimal runnable example (single line)
4. **Arguments**: required inputs (table)
5. **Options**: optional flags (table)
6. **Examples**: 2–3 common scenarios (may include options)
7. **Notes / Warnings**: use `!!! note/warning` if needed
8. **CLI Help (Auto-generated)**: inserted by `sc-docs-cli-sync`

**Template**:

```markdown
# sc-xxxx

One-line purpose statement.

## Usage

```bash
uv run sc-xxxx <args>
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| `arg` | Description | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--flag` | Description | - |

## Examples

**Basic**
```bash
uv run sc-xxxx ...
```

**Common scenario**
```bash
uv run sc-xxxx --option value ...
```

## Notes

!!! note "Optional"
    Extra notes or warnings.

<!-- CLI-HELP-START -->
... auto-generated block ...
<!-- CLI-HELP-END -->
```

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

- [CLI Reference](../../reference/cli/index.md)

---

## Agent Rule { #agent-rule }

```markdown
## CLI Docs Automation
- **Hybrid Model**: Hand-written content + auto-generated help block.
- **Generate**: `uv run sc-docs-cli --output-dir docs/reference/cli/generated --overwrite`
- **Sync**: `uv run sc-docs-cli-sync`
- **Check**: `uv run sc-docs-cli-sync --check`
- **Rendered Docs**: Do not render `docs/reference/cli/generated/` in nav.
```
