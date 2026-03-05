---
aliases:
  - Data Formats Reference
  - Data Format Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data-format
status: stable
owner: docs-team
audience: team
scope: Raw ingest, SQLite persistence, and analysis-output format contracts
version: v1.5.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Data Formats

This section is the reference SoT for data contracts across:

- raw source files (`data/raw/`)
- SQLite persistence (`DatasetRecord`, `DataRecord`, `ResultBundleRecord`)
- analysis outputs consumed by Characterization/Simulation views

!!! important "Design baseline (2026-03-04)"
    - Analysis eligibility is **trace-first** (DataRecord-level), not dataset-name-first.
    - `dataset_profile` is a dataset-level **summary and recommendation**.
    - Result provenance and reuse are anchored by `ResultBundleRecord`.

## Topics

| Topic | Description |
|---|---|
| [Raw Data Layout](raw-data-layout.en.md) | Source folder contract and ingest boundary for `data/raw/` |
| [Dataset Record](dataset-record.en.md) | SQLite core model, `dataset_profile`, and Trace Index contract |
| [Circuit Netlist](circuit-netlist.en.md) | Circuit Netlist source/expanded contract and repeat expansion |
| [Analysis Result](analysis-result.en.md) | `ResultBundleRecord`, `analysis_result` DataRecord, and DerivedParameter contracts |

## Implementation Alignment (2026-03-04)

!!! note "Current state"
    Characterization Run Analysis currently uses a mixed gating path:
    1. dataset-profile capability gating
    2. trace compatibility checks (`data_type` / `parameter` / `representation`)
    3. explicit trace-id selection
    Execution still requires compatible and selected traces.

!!! warning "Sync requirement"
    This reference defines trace-first as the data contract direction.
    When capability hard-blocking is removed, update [Characterization UI Reference](../ui/characterization.en.md) accordingly.

## Related

- [Pipeline Data Flow](../../explanation/architecture/pipeline/data-flow.en.md)
- [Characterization UI](../ui/characterization.en.md)
- [Data Handling Guardrail](../guardrails/code-quality/data-handling.en.md)
