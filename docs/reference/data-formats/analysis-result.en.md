---
aliases:
  - Analysis Result Schema
  - Analysis Result Format
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data
status: stable
owner: docs-team
audience: team
scope: Persistence and provenance contract for Characterization analysis runs
version: v0.3.1
last_updated: 2026-03-04
updated_by: docs-team
---

# Analysis Result Schema

This page defines the formal persistence contract for Characterization analysis results.

!!! note "Current implementation (2026-03-04)"
    Analysis outputs are currently persisted in two layers:
    1) `ResultBundleRecord(bundle_type=characterization, role=analysis_run)` for run provenance
    2) `DerivedParameter` grouped by method for Result View rendering

!!! important "Contract"
    Analysis authority is trace-first:
    - compatible traces are required
    - selected trace ids are required
    - `dataset_profile` is recommendation/hint metadata only and must not hard-block runs

## Run Bundle Contract

Every successful run must create a new `ResultBundleRecord`:

| Field | Required | Contract |
|---|---|---|
| `bundle_type` | ✅ | `characterization` |
| `role` | ✅ | `analysis_run` |
| `status` | ✅ | `completed` |
| `source_meta.origin` | ✅ | `characterization` |
| `source_meta.analysis_id` | ✅ | registry analysis id |
| `source_meta.input_bundle_id` | ✅ | Internal provenance source bundle id; nullable for dataset-level scope |
| `config_snapshot` | ✅ | must include selected trace ids and analysis config |

### `config_snapshot` minimum fields

- `selected_trace_ids: list[int]`
- `selected_trace_mode_group: "base" | "sideband"`
- analysis-specific fields (for example `fit_model`, `f_min`, `f_max`)

!!! warning "Provenance completeness"
    Missing either `input_bundle_id` or `selected_trace_ids` means analysis input scope cannot
    be reconstructed and violates this contract.

## Result Parameter Contract

Analysis outputs are persisted as `DerivedParameter` rows, minimum requirements:

- `dataset_id`
- `method` (must align with `analysis_registry.completed_methods`)
- `name` / `value` / `unit`
- `extra.trace_mode_group` (`base` / `sideband`)

!!! important "Result View filter contract"
    Result View `Trace Mode Filter` (All/Base/Sideband) must consume
    `DerivedParameter.extra.trace_mode_group` directly; no parallel inference path is allowed.

## Scope Bridge Contract (Simulation -> Characterization)

!!! note "Current behavior (2026-03-04)"
    The persistence model still supports bundle-level lineage (`input_bundle_id`).

!!! important "Contract (Dataset-centric UI, internal bundle provenance)"
    Characterization UI is dataset-centric and must not expose "select characterization bundle as input"
    as the primary run flow. Run candidate traces come from dataset-level trace index with trace-first filtering;
    provenance may still persist `input_bundle_id` internally for reconstruction.

!!! warning "Input hygiene"
    `analysis_result`-typed data must not be reused as trace input unless a specific analysis
    explicitly declares that contract.

!!! note "Simulation post-process HFSS metadata"
    `hfss_comparable` and `input_y_source` belong to `simulation_postprocess` bundle provenance,
    defined in `Dataset Record Schema`.
    Characterization `analysis_run` bundles should not duplicate these fields as run authority.

## JSON Example (characterization run bundle)

```json
{
  "bundle_type": "characterization",
  "role": "analysis_run",
  "status": "completed",
  "source_meta": {
    "origin": "characterization",
    "analysis_id": "squid_fitting",
    "analysis_label": "SQUID Fitting",
    "input_bundle_id": 42
  },
  "config_snapshot": {
    "fit_model": "WITH_LS",
    "fit_min_nh": 0.5,
    "fit_max_nh": 5.0,
    "selected_trace_ids": [101, 118, 120],
    "selected_trace_mode_group": "base"
  }
}
```

## Related

- [Dataset Record Schema](dataset-record.en.md)
- [Characterization](../ui/characterization.en.md)
