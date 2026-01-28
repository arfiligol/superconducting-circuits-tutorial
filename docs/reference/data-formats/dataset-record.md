---
aliases:
  - "Dataset Record Schema"
  - "DatasetRecord 格式"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "DatasetRecord SQLite Schema 詳細定義與使用規範"
version: v1.0.0
last_updated: 2026-01-26
updated_by: docs-team
---

# Dataset Record Schema

`DatasetRecord` 是本專案的核心數據儲存格式，用於管理模擬與量測數據。

!!! note "取代 ComponentRecord"
    此 Schema 取代舊版 `ComponentRecord`，改用 SQLite 儲存並支援 Tag 系統。

## 概念

```
DatasetRecord (集合)
├── name: "PF6FQ_Q0_XY"
├── tags: [PF6FQ, Q0, XY_Line]
├── source_meta: {origin, solver, raw_file}
├── parameters: {L_jun_nH: 0.5}
│
├── DataRecord[] (數據)
│   ├── Y11 real
│   ├── Y11 imag
│   └── S11 mag
│
└── DerivedParameter[] (萃取參數)
    ├── f_resonance: 5.12 GHz
    └── Q_factor: 1200
```

---

## Schema 定義

### DatasetRecord

數據集合，可包含多筆 `DataRecord`。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | 主鍵 |
| `name` | str | ✅ | 唯一識別碼 (e.g., `PF6FQ_Q0_XY`) |
| `source_meta` | JSON | - | 來源資訊 |
| `parameters` | JSON | - | 模擬/量測參數 |
| `created_at` | datetime | Auto | 建立時間 |

**source_meta 範例**:

```json
{
  "origin": "layout_simulation",
  "solver": "hfss_driven",
  "raw_file": "data/raw/layout_simulation/admittance/PF6FQ.csv"
}
```

**origin 可用值**:
- `circuit_simulation` - JosephsonCircuits.jl 等電路模擬
- `layout_simulation` - HFSS/Q3D 等 EM 模擬
- `measurement` - 實驗量測

---

### DataRecord

單筆數據 (e.g., Y11 imaginary part)。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | 主鍵 |
| `dataset_id` | int | ✅ | 所屬 DatasetRecord |
| `data_type` | str | ✅ | `s_params`, `y_params`, `z_params` |
| `parameter` | str | ✅ | `S11`, `Y21`, `C12` 等 |
| `representation` | str | ✅ | `real`, `imaginary`, `amplitude`, `phase` |
| `axes` | JSON | ✅ | 軸定義 |
| `values` | JSON | ✅ | 數值陣列 |

**axes 格式**:

```json
[
  {"name": "frequency", "unit": "GHz", "values": [1.0, 2.0, 3.0]},
  {"name": "L_jun", "unit": "nH", "values": [0.1, 0.2]}
]
```

**values 格式**:
- 1D: `[0.01, 0.02, 0.03]`
- 2D: `[[0.01, 0.02], [0.03, 0.04], [0.05, 0.06]]` (row=axis[0], col=axis[1])

---

### Tag

標籤系統，用於組織和搜尋。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | 主鍵 |
| `name` | str | ✅ | 標籤名稱 (unique) |

**使用範例**:
- `PF6FQ` - 晶片版本
- `Q0` - 元件
- `XY_Line` - 結構類型

---

### DerivedParameter

從 DataRecord 萃取的物理參數。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | 主鍵 |
| `dataset_id` | int | ✅ | 所屬 DatasetRecord |
| `device_type` | str | ✅ | `resonator`, `qubit`, `jpa`, `other` |
| `name` | str | ✅ | 參數名稱 |
| `value` | float | ✅ | 數值 |
| `unit` | str | - | 單位 |
| `method` | str | - | 萃取方法 |
| `metadata` | JSON | - | 額外資訊 |

**支援的物理參數**:

| Device Type | Parameters |
|-------------|------------|
| **All** | `f_resonance`, `Q_factor`, `C_eff`, `L_eff` |
| **Qubit** | `f_qubit`, `detuning`, `g_coupling`, `anharmonicity` |
| **JPA** | `f_pump`, `pump_type`, `gain_dB`, `bandwidth`, `P_saturation` |

---

## 資料庫位置

```
data/database.db    # SQLite 資料庫檔案
```

---

## CLI 使用

```bash
# 匯入 HFSS CSV 並貼標籤
uv run sc-import-hfss data.csv --name PF6FQ_Q0_XY --tags PF6FQ,Q0

# 列出所有 Dataset
uv run sc-db list


# 分析指定 Dataset
uv run sc-analyze PF6FQ_Q0_XY --data Y11:imag
```

---

## Python Model

定義於 `src/core/shared/persistence/models.py`。

## Related

- [Data Handling](../guardrails/code-quality/data-handling.md) - 數據處理規範
- [Raw Data Layout](raw-data-layout.md) - 原始數據目錄結構
