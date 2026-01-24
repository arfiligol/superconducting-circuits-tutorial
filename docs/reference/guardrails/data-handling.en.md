---
aliases:
  - "Data Handling Rules"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "Data Handling Rules: Read-only Raw Data, Path Constants"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Data Handling

Data handling and path standards.

## Directory Structure

```
data/
├── raw/                    # Raw Data (Read-Only)
│   ├── measurement/
│   │   └── flux_dependence/
│   ├── circuit_simulation/
│   └── layout_simulation/
│       ├── admittance/
│       └── phase/
├── preprocessed/           # Transformed JSON
└── processed/
    └── reports/            # Analysis Outputs
```

## Rules

### 1. Raw Data is Read-Only

All files under `data/raw/` are considered immutable:
- Do not modify raw files
- Do not delete raw files
- Write transformation results to `data/preprocessed/`

### 2. Use Path Helpers

Use constants provided by `src/utils/paths.py`:

```python
from src.utils import (
    RAW_LAYOUT_ADMITTANCE_DIR,
    RAW_LAYOUT_PHASE_DIR,
    RAW_MEASUREMENT_FLUX_DEPENDENCE_DIR,
    PREPROCESSED_DATA_DIR,
    PROCESSED_REPORTS_DIR,
)

# ✅ Correct
output_path = PROCESSED_REPORTS_DIR / "result.json"

# ❌ Incorrect
output_path = Path("data/processed/reports/result.json")
```

### 3. Output Locations

| Type | Target Directory |
|------|------------------|
| Preprocessed JSON | `data/preprocessed/` |
| Analysis Reports | `data/processed/reports/` |
| Figures/Plots | `data/processed/reports/` |

## Related

- [Raw Data Layout](../data-formats/raw-data-layout.md) - Directory structure details
- [Script Authoring](script-authoring.md) - Script writing rules

---

## Agent Rule { #agent-rule }

```markdown
## Data Handling
- **Immutable**: `data/raw/` is READ-ONLY.
- **Paths**: NEVER hardcode paths.
    - **MUST** import from `src.utils.paths`.
    - Keywords: `RAW_*_DIR`, `PREPROCESSED_DATA_DIR`, `PROCESSED_REPORTS_DIR`.
- **Flow**: Raw -> Preprocessing Script -> Preprocessed (JSON) -> Analysis Script -> Processed (Reports).
- **Format**: Prefer **JSON** for light data, **CSV** for tabular data.
```
