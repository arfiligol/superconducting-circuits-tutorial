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
version: v1.7.0
last_updated: 2026-03-06
updated_by: codex
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
| [Query Indexing Strategy](query-indexing-strategy.en.md) | High-frequency query paths, index candidates, and monitoring guidance |

## Quick Lookup (Start Here)

| Question | Read this first |
|---|---|
| Is Circuit Definition components-first or parameters-first? | [Circuit Netlist](circuit-netlist.en.md) |
| Where are Simulation sweep outputs (including multi-axis) persisted? | [Dataset Record](dataset-record.en.md) |
| Which fields are valid sweep targets (netlist parameters vs source/bias fields)? | [Circuit Netlist](circuit-netlist.en.md) + [Circuit Simulation UI](../ui/circuit-simulation.en.md) |
| Where is Characterization run provenance / selected traces stored? | [Analysis Result](analysis-result.en.md) |
| Why does UI show availability but run still depends on trace selection? | [Analysis Result](analysis-result.en.md) + [Dataset Record](dataset-record.en.md) |
| Does adding sweep require Characterization changes at the same time? | [Dataset Record](dataset-record.en.md) + [Analysis Result](analysis-result.en.md) |
| Which contract covers large-data querying and indexing? | [Query Indexing Strategy](query-indexing-strategy.en.md) |

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
