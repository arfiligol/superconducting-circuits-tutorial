---
aliases:
  - "Dataset Record Schema"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "DatasetRecord SQLite Schema definition and usage"
version: v1.0.0
last_updated: 2026-01-26
updated_by: docs-team
---

# Dataset Record Schema

`DatasetRecord` is the core data storage format for managing simulation and measurement data.

!!! note "Replaces ComponentRecord"
    This schema replaces the legacy `ComponentRecord` format, using SQLite storage with Tag system support.

## Concept

```
DatasetRecord (Collection)
├── name: "PF6FQ_Q0_XY"
├── tags: [PF6FQ, Q0, XY_Line]
├── source_meta: {origin, solver, raw_file}
├── parameters: {L_jun_nH: 0.5}
│
├── DataRecord[] (Data)
│   ├── Y11 real
│   ├── Y11 imag
│   └── S11 mag
│
└── DerivedParameter[] (Extracted)
    ├── f_resonance: 5.12 GHz
    └── Q_factor: 1200
```

---

## Schema Definition

### DatasetRecord

Collection that contains multiple `DataRecord` entries.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | Primary key |
| `name` | str | ✅ | Unique identifier (e.g., `PF6FQ_Q0_XY`) |
| `source_meta` | JSON | - | Source information |
| `parameters` | JSON | - | Simulation/measurement parameters |
| `created_at` | datetime | Auto | Creation timestamp |

**source_meta example**:

```json
{
  "origin": "layout_simulation",
  "solver": "hfss_driven",
  "raw_file": "data/raw/layout_simulation/admittance/PF6FQ.csv"
}
```

**origin values**:
- `circuit_simulation` - JosephsonCircuits.jl circuit simulation
- `layout_simulation` - HFSS/Q3D EM simulation
- `measurement` - Experimental measurement

---

### DataRecord

Single data record (e.g., Y11 imaginary part).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | Primary key |
| `dataset_id` | int | ✅ | Parent DatasetRecord |
| `data_type` | str | ✅ | `s_params`, `y_params`, `z_params` |
| `parameter` | str | ✅ | `S11`, `Y21`, `C12`, etc. |
| `representation` | str | ✅ | `real`, `imaginary`, `amplitude`, `phase` |
| `axes` | JSON | ✅ | Axis definitions |
| `values` | JSON | ✅ | Value array |

---

### Tag

Tag system for organizing and searching.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | Primary key |
| `name` | str | ✅ | Tag name (unique) |

---

### DerivedParameter

Physical parameters extracted from DataRecord.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | Primary key |
| `dataset_id` | int | ✅ | Parent DatasetRecord |
| `device_type` | str | ✅ | `resonator`, `qubit`, `jpa`, `other` |
| `name` | str | ✅ | Parameter name |
| `value` | float | ✅ | Numeric value |
| `unit` | str | - | Unit |
| `method` | str | - | Extraction method |

**Supported parameters**:

| Device Type | Parameters |
|-------------|------------|
| **All** | `f_resonance`, `Q_factor`, `C_eff`, `L_eff` |
| **Qubit** | `f_qubit`, `detuning`, `g_coupling`, `anharmonicity` |
| **JPA** | `f_pump`, `pump_type`, `gain_dB`, `bandwidth`, `P_saturation` |

---

## Database Location

```
data/database.db    # SQLite database file
```

---

## CLI Usage

```bash
# Import HFSS CSV with tags
uv run sc-import-hfss data.csv --name PF6FQ_Q0_XY --tags PF6FQ,Q0

# List all datasets
uv run sc-list-datasets

# Filter by tag
uv run sc-list-datasets --tag PF6FQ

# Analyze specific dataset
uv run sc-analyze PF6FQ_Q0_XY --data Y11:imag
```

---

## Python Model

Defined in `src/core/shared/persistence/models.py`.

## Related

- [Data Handling](../guardrails/code-quality/data-handling.en.md) - Data handling rules
- [Raw Data Layout](raw-data-layout.md) - Raw data directory structure
