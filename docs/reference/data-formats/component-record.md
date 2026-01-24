---
aliases:
  - "Component Record Schema"
  - "ComponentRecord 格式"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "ComponentRecord JSON 格式詳細定義"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Component Record Schema

`ComponentRecord` 是本專案的核心數據交換格式（Source of Truth）。

## JSON Structure

```json
{
  "component_id": "LJPAL658_v1",
  "source_type": "circuit_simulation",
  "datasets": [
    {
      "dataset_id": "y11_imag",
      "family": "y_parameters",
      "parameter": "Y11",
      "representation": "imaginary",
      "axes": [
        {
          "name": "frequency",
          "unit": "GHz",
          "values": [4.0, 4.01, 4.02]
        },
        {
          "name": "L_jun",
          "unit": "nH",
          "values": [0.1, 0.2]
        }
      ],
      "values": [
        [0.01, 0.02],
        [0.015, 0.025],
        [0.018, 0.028]
      ]
    }
  ],
  "raw_files": [
    {
      "path": "data/raw/..."
    }
  ]
}
```

## Fields

### ComponentRecord
| Field | Type | Description |
|-------|------|-------------|
| `component_id` | str | 唯一識別碼 |
| `source_type` | enum | `measurement`, `circuit_simulation`, `layout_simulation` |
| `datasets` | list | 包含的數據集列表 |

### ParameterDataset
| Field | Type | Description |
|-------|------|-------------|
| `family` | enum | `s_parameters`, `y_parameters`, `z_parameters` |
| `representation` | enum | `amplitude`, `phase`, `real`, `imaginary` |
| `axes` | list | 軸定義。對於 2D 矩陣，順序對應 `values` 的 `[row, col]`。 |
| `values` | list | 數值矩陣。 |

## Python Model

定義於 `src/preprocess/schema.py`。

## Related

- [Schema Design](../../explanation/architecture/design-decisions/schema-design.md) - 架構設計決策Rationale]]
