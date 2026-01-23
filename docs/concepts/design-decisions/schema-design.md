---
aliases:
  - "Schema Design"
  - "Schema 設計"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "Pydantic Schema 設計細節"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Schema Design

我們使用 Pydantic 來定義 `ComponentRecord`。

## 核心實體

### `ParameterAxis`
定義掃描軸 (Sweep Axis)。
```python
class ParameterAxis(BaseModel):
    name: str          # e.g., "frequency", "flux_bias"
    unit: str          # e.g., "GHz", "mA"
    values: list[float]
```

### `ParameterDataset`
定義一組數據。支援多維矩陣。
```python
class ParameterDataset(BaseModel):
    family: ParameterFamily         # S, Y, Z
    representation: ParameterRepresentation # amplitude, phase, real, imag
    axes: list[ParameterAxis]       # [freq_axis, bias_axis]
    values: list[list[float]]       # 2D Matrix
```

### `ComponentRecord`
聚合一個元件的所有數據。
```python
class ComponentRecord(BaseModel):
    component_id: str
    datasets: list[ParameterDataset]
```

## 擴展性考量

- **多軸支援**：`datasets` 設計允許 1D (頻率掃描) 或 2D (Flux + 頻率) 甚至更高維度。
- **多參數**：一個 Component 可以同時包含 S11, S21, Y11 等多組數據。

## Related

- [[../../reference/data-formats/component-record.md|Component Record Reference]] - 完整欄位說明
