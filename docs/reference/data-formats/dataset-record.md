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
version: v1.5.0
last_updated: 2026-03-07
updated_by: codex
---

# Dataset Record Schema

`DatasetRecord` 是本專案的核心數據儲存格式，用於管理模擬與量測數據。

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

**origin 可用值**:
- `circuit_simulation` - JosephsonCircuits.jl 等電路模擬
- `layout_simulation` - HFSS/Q3D 等 EM 模擬
- `measurement` - 實驗量測

### dataset_profile（source_meta 子契約）

`source_meta.dataset_profile` 是 Dataset 層級的摘要與建議契約（summary/recommendation），
不是 trace-level run authority。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | str | ✅ | 目前 `1.0` |
| `device_type` | str | ✅ | `unspecified` / `single_junction` / `squid` / `traveling_wave` / `resonator` / `other` |
| `capabilities` | list[str] | ✅ | canonical capability keys |
| `source` | str | ✅ | `inferred` / `template` / `manual_override` |

!!! note "Current implementation（2026-03-04）"
    Characterization UI 仍會顯示 profile 衍生的 `Recommended/Available` 提示，
    並保留 `required_capabilities` / `excluded_capabilities` 欄位作為建議訊息來源。

!!! important "Contract（Trace-first authority）"
    Analysis 可執行性與實際輸入範圍必須由 trace 相容性 + 使用者選取 trace ids 決定。
    `dataset_profile.capabilities` 僅作為建議、預設與提示，不可單獨 hard-block run。

!!! warning "Backward compatibility"
    舊資料若沒有 `dataset_profile`，應 fallback 為 `inferred`，
    從現有 DataRecord metadata 推導基礎 capabilities，避免既有流程中斷。

!!! note "Current behavior（2026-03-04）"
    歷史版本曾在 `/raw-data` 與 `/simulation` 提供 metadata 寫入入口。

!!! important "Metadata entry contract（Dashboard-only）"
    `source_meta.dataset_profile` 的可編輯入口唯一位於 Pipeline `/dashboard`。
    `/raw-data` 與 `/simulation` 僅可顯示 read-only summary，不得直接寫入 metadata。

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

### ResultBundleRecord 與 ResultBundleDataLink

`ResultBundleRecord` 表示一次 run/import/analysis 批次；`ResultBundleDataLink` 負責 bundle 與 trace (`DataRecord`) 關聯。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | int | Auto | 主鍵 |
| `dataset_id` | int | ✅ | 所屬 Dataset |
| `bundle_type` | str | ✅ | 例如 `circuit_simulation` / `simulation_postprocess` / `characterization` |
| `role` | str | ✅ | 例如 `manual_export` / `derived_from_simulation` / `analysis_run` |
| `status` | str | ✅ | 例如 `completed` |
| `source_meta` | JSON | ✅ | 來源描述與 provenance 索引 |
| `config_snapshot` | JSON | ✅ | 本次 run 輸入設定快照 |
| `result_payload` | JSON | - | 可選摘要 payload |

!!! important "Bundle Scope Contract"
    Characterization UI 以 dataset-centric 為主，預設使用 `All Dataset Records`。
    若內部 provenance 指向特定 `ResultBundleRecord`，僅能分析該 bundle 透過
    `ResultBundleDataLink` 連結的 traces；不應在 UI 強迫使用者手動操作 bundle。

!!! important "Provenance Contract"
    `source_meta` + `config_snapshot` 必須能回推一次分析輸入：
    至少包含 input bundle（可為 `null` 代表全 dataset）與 selected trace ids。

### Simulation Post-Process provenance（新增）

當 `bundle_type=simulation_postprocess` 時，`config_snapshot` 應包含：

- `input_y_source`: `raw_y` 或 `ptc_y`
- `hfss_comparable`: `true` / `false`
- `hfss_not_comparable_reason`: 當 `hfss_comparable=false` 時的可讀理由

!!! important "Raw/Processed 語意對齊"
    `hfss_comparable` 只描述 post-processed 輸出是否符合 HFSS 比對前提，
    不代表 Raw Result View 的 `S` 已被改寫或替換。

!!! note "Current behavior（2026-03-07）"
    現有契約已定義 post-processing 的 flow provenance 與輸出 traces，
    但尚未把「parameter sweep 輸入下的完整 post-processed sweep payload」寫成已完成能力。

### Simulation Post-Process over Sweep（Target）

若 `simulation_postprocess` 的來源 simulation bundle 為 `run_kind=parameter_sweep`，最低契約應包含：

- `source_meta.source_simulation_bundle_id`
- `source_meta.source_run_kind = "parameter_sweep"`
- `config_snapshot.sweep_setup_hash`
- `config_snapshot` 的完整 post-processing flow spec
- `result_payload.run_kind = "parameter_sweep"`
- `result_payload.sweep_axes`
- `result_payload.point_count`
- `result_payload.points[]`
  - 每點至少含 `source_point_index`
  - `axis_indices`
  - `axis_values`
  - 該點 post-processed result 或可穩定回推該點結果的 handle
- `result_payload.representative_point_index`

!!! important "Representative point is projection only"
    `representative_point_index` 只能作 quick-inspect projection。
    若缺少完整 `sweep_axes` / `points[]` / point metadata，就不能宣稱此 bundle 是完整的 post-processed sweep authority。

### Simulation Sweep provenance（新增）

當 `bundle_type=circuit_simulation` 且是 sweep run，`result_payload` 應包含：

- `run_kind`: `parameter_sweep`
- `sweep_axes`: 軸定義陣列（每軸 target/unit/values）
- `point_count`: 總點數
- `points`: 每點的 `axis_values` 與該點 simulation result

`config_snapshot` 應包含：

- `sweep_setup_hash`
- sweep setup 的完整快照（至少含 `axes`）

!!! important "Canonical vs projection"
    Sweep 的 canonical run authority 在 `ResultBundleRecord.result_payload`。
    `DataRecord` 是 projection/index 化視圖（可附 sweep 軸 metadata），供查詢與分析流程使用。
    高維 sweep 不應把「只為 UI 一次瀏覽」的資料設計成唯一 SoT。

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
- [Circuit Netlist](circuit-netlist.md) - netlist 參數層 sweep target 定義
- [Circuit Simulation UI](../ui/circuit-simulation.md) - source/bias sweep setup 與 Result View 顯示契約
