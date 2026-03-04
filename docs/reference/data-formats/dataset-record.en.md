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
version: v1.3.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Dataset Record Schema

`DatasetRecord` is the core data storage format for managing simulation and measurement data.

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
  "raw_file": "data/raw/layout_simulation/admittance/PF6FQ.csv",
  "dataset_profile": {
    "schema_version": "1.0",
    "device_type": "squid",
    "capabilities": [
      "y_parameter_characterization",
      "y11_response_fitting",
      "squid_characterization"
    ],
    "source": "manual_override"
  }
}
```

**origin values**:
- `circuit_simulation` - JosephsonCircuits.jl circuit simulation
- `layout_simulation` - HFSS/Q3D EM simulation
- `measurement` - Experimental measurement

### dataset_profile (source_meta sub-contract)

`source_meta.dataset_profile` is a dataset-level summary and recommendation contract, not
trace-level run authority.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | str | ✅ | currently `1.0` |
| `device_type` | str | ✅ | `unspecified` / `single_junction` / `squid` / `traveling_wave` / `resonator` / `other` |
| `capabilities` | list[str] | ✅ | canonical capability keys |
| `source` | str | ✅ | `inferred` / `template` / `manual_override` |

!!! note "Current implementation (2026-03-04)"
    Characterization UI still renders profile-derived `Recommended/Available` hints and
    keeps `required_capabilities` / `excluded_capabilities` fields as recommendation signals.

!!! important "Contract (Trace-first authority)"
    Executability and run input scope must be decided by trace compatibility plus user-selected
    trace ids. `dataset_profile.capabilities` is recommendation/default/hint metadata only and
    must not hard-block runs by itself.

!!! warning "Backward compatibility"
    Legacy datasets without `dataset_profile` should fall back to `inferred`,
    derived from existing DataRecord metadata, so current workflows remain usable.

!!! note "Current behavior (2026-03-04)"
    Previous builds exposed metadata write entry points on `/raw-data` and `/simulation`.

!!! important "Metadata entry contract (Dashboard-only)"
    The only editable entry for `source_meta.dataset_profile` is Pipeline `/dashboard`.
    `/raw-data` and `/simulation` must remain read-only summary surfaces for metadata.

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

### ResultBundleRecord and ResultBundleDataLink

`ResultBundleRecord` models one run/import/analysis batch, and `ResultBundleDataLink`
models bundle-to-trace membership (`DataRecord` linkage).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | Primary key |
| `dataset_id` | int | ✅ | Parent Dataset |
| `bundle_type` | str | ✅ | e.g. `circuit_simulation` / `simulation_postprocess` / `characterization` |
| `role` | str | ✅ | e.g. `manual_export` / `derived_from_simulation` / `analysis_run` |
| `status` | str | ✅ | e.g. `completed` |
| `source_meta` | JSON | ✅ | Source description and provenance index |
| `config_snapshot` | JSON | ✅ | Run input snapshot |
| `result_payload` | JSON | - | Optional compact payload |

!!! important "Bundle scope contract"
    Characterization UI is dataset-centric and defaults to `All Dataset Records`.
    When internal provenance points to one specific `ResultBundleRecord`, only traces linked
    through `ResultBundleDataLink` may be analyzed; UI should not force explicit bundle operations.

!!! important "Provenance contract"
    `source_meta` + `config_snapshot` must be sufficient to reconstruct analysis input.
    At minimum: input bundle (nullable for full-dataset scope) and selected trace ids.

### Simulation post-process provenance (new)

When `bundle_type=simulation_postprocess`, `config_snapshot` should include:

- `input_y_source`: `raw_y` or `ptc_y`
- `hfss_comparable`: `true` / `false`
- `hfss_not_comparable_reason`: human-readable reason when `hfss_comparable=false`

!!! important "Raw/processed semantic alignment"
    `hfss_comparable` describes only whether the post-processed output satisfies
    HFSS-comparison preconditions. It does not mean Raw Result View `S` is rewritten.

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
uv run sc-db list


# Analyze specific dataset
uv run sc-analyze PF6FQ_Q0_XY --data Y11:imag
```

---

## Python Model

Defined in `src/core/shared/persistence/models.py`.

## Related

- [Data Handling](../guardrails/code-quality/data-handling.en.md) - Data handling rules
- [Raw Data Layout](raw-data-layout.md) - Raw data directory structure
