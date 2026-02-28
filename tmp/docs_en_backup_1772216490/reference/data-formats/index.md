---
aliases:
  - Data Formats Reference
  - 數據格式參考
tags:
  - diataxis/reference
  - audience/team
status: stable
owner: docs-team
audience: team
scope: Data format specifications, including directory layout and schema definitions
version: v1.3.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Data Formats

Data format specification reference.

## Topics

- [Raw Data Layout](raw-data-layout.md) - `data/raw/` directory layout
- [Dataset Record](dataset-record.md) - `DatasetRecord` SQLite schema (**recommended**)
- [Circuit Netlist](circuit-netlist.md) - `CircuitDefinition` format, `value_ref`, `parameters`, and sweep rules
- [Analysis Result](analysis-result.md) - analysis result `TypedDict` format

## Related

- [Pipeline](../../explanation/architecture/pipeline/data-flow.md) - understand the data flow
- [Data Handling](../guardrails/code-quality/data-handling.en.md) - data handling guardrails
