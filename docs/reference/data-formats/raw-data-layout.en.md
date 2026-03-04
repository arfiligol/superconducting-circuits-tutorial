---
aliases:
  - Raw Data Layout
  - Raw Source Layout
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: Project-first source-folder contract and ingest auto-classification boundary for data/raw
version: v0.3.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Raw Data Layout

`data/raw/` stores externally produced source files (measurement exports and simulation exports).  
The raw-layout contract is **project-folder-first**, not phase/admittance subfolder-first.

## Directory structure (project-first)

```text
data/raw/
└── <project_name>/
    ├── *.csv
    ├── *.txt
    └── ...
```

Example:

```text
data/raw/
└── PF6FQ_Q0/
    ├── PF6FQ_Q0_XY_Im_Y11.csv
    ├── PF6FQ_Q0_Readout_ang_rad_S21.csv
    └── PF6FQ_Q0_flux_sweep.txt
```

## Auto-classification and preprocess routing

CLI/UI ingest can classify and route files based on filename and column signals:

| Rule type | Description |
|---|---|
| Filename semantics | for example `Y11`, `S21`, `Re_`, `Im_`, `ang`, `cang`, `deg`, `rad` |
| Representation inference | phase / unwrapped_phase / real / imaginary / magnitude |
| Skip policy | files not matching the selected processor can be skipped instead of hard-failing |

!!! important "No manual phase/admittance folder split required"
    The data-format contract does not require folders such as `admittance/` or `phase/`.  
    Type decisions are made during ingest.

!!! note "Raw vs Trace responsibilities"
    `data/raw/` stores source files only.  
    Analysis reads ingested `DataRecord` traces from SQLite.

## Rules

1. **Immutable by default**: treat imported raw files as read-only.
2. **Project-first**: organize by project first, then let ingest classify.
3. **Filename readability**: include parameter/representation/unit hints in filenames.
4. **Source fidelity**: keep files as exported by instruments/solvers (no in-place manual reshaping).

## Relationship to DatasetRecord

- `DatasetRecord.source_meta.raw_file` / `raw_files` can reference source files.
- Ingestion creates `DataRecord` traces and a logical Trace Index used by Characterization/Simulation views.
- `dataset_profile` is dataset-level summary metadata and does not replace trace-level compatibility checks.

## Related

- [Dataset Record](dataset-record.en.md)
- [Analysis Result](analysis-result.en.md)
- [Pipeline Data Flow](../../explanation/architecture/pipeline/data-flow.en.md)
