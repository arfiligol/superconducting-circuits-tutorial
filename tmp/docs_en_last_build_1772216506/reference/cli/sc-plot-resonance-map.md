---
aliases:
- sc-plot-resonance-map
tags:
- audience/team
status: draft
owner: docs-team
audience: team
scope: 2D resonance-frequency plot by qubit structure
version: v0.1.0
last_updated: 2026-02-11
updated_by: docs-team
---

# sc plot different-qubit-structure-frequency-comparison-table

Render a resonance-frequency comparison table (`Qubit x Structure`) by default, from DB records of
`analysis_result / f_resonance`.

## Usage

```bash
uv run sc plot different-qubit-structure-frequency-comparison-table [OPTIONS]
```

## Options

| Option | Description | Default |
|---|---|---|
| `--dataset`, `-d` | Filter by dataset name or ID (repeatable) | all |
| `--mode` | Mode label | `Mode 1` |
| `--l-jun-nh` | Target `L_jun` (nH), selects nearest point per cell | not set |
| `--aggregate` | Aggregation when `--l-jun-nh` is not set: `first`/`mean`/`min`/`max` | `first` |
| `--render` | Output type: `table` or `heatmap` | `table` |
| `--show` / `--no-show` | Open browser preview directly | `--show` |
| `--save-html` / `--no-save-html` | Save HTML output | `--no-save-html` |
| `--output`, `-o` | HTML output path | auto-generated |
| `--png-output` | Save PNG (requires `kaleido`) | not set |

## Examples

**Default comparison table (browser preview)**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table
```

**Select mode and target L_jun**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table --mode "Mode 1" --l-jun-nh 0.1
```

**Switch to 2D heatmap**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table --render heatmap
```

**Save table as HTML**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table --render table --save-html
```

## Alias

Backward-compatible alias:
```bash
uv run sc plot resonance-map
```
