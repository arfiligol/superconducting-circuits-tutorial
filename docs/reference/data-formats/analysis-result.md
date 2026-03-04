---
aliases:
  - Analysis Result Schema
  - 分析結果格式
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/data
status: stable
owner: docs-team
audience: team
scope: Characterization analysis run 的 persistence / provenance 契約
version: v0.3.1
last_updated: 2026-03-04
updated_by: docs-team
---

# Analysis Result Schema

本頁定義 Characterization 分析結果在資料層的正式契約。

!!! note "Current implementation（2026-03-04）"
    目前分析結果主要由兩層組成：
    1) `ResultBundleRecord(bundle_type=characterization, role=analysis_run)` 記錄一次 run 的 provenance
    2) `DerivedParameter` 以 method 分組保存可顯示結果

!!! important "Contract"
    Analysis run authority 採 trace-first：
    - 必須有 compatible traces
    - 必須有 selected trace ids
    - `dataset_profile` 僅作推薦/提示，不能單獨阻擋 run

## Run Bundle Contract

每次成功 run 必須建立新的 `ResultBundleRecord`：

| Field | Required | Contract |
|---|---|---|
| `bundle_type` | ✅ | `characterization` |
| `role` | ✅ | `analysis_run` |
| `status` | ✅ | `completed` |
| `source_meta.origin` | ✅ | `characterization` |
| `source_meta.analysis_id` | ✅ | registry analysis id |
| `source_meta.input_bundle_id` | ✅ | 內部 provenance 的來源 bundle id；dataset-level scope 時可為 `null` |
| `config_snapshot` | ✅ | 必須含 selected trace ids 與本次 analysis config |

### `config_snapshot` minimum fields

- `selected_trace_ids: list[int]`
- `selected_trace_mode_group: "base" | "sideband"`
- analysis-specific config fields（例如 `fit_model`, `f_min`, `f_max`）

!!! warning "Provenance completeness"
    只要缺少 `input_bundle_id` 或 `selected_trace_ids`，就無法完整回推 analysis input scope，視為違反契約。

## Result Parameter Contract

分析輸出由 `DerivedParameter` 持久化，最小要求：

- `dataset_id`
- `method`（需與 `analysis_registry.completed_methods` 對齊）
- `name` / `value` / `unit`
- `extra.trace_mode_group`（`base` / `sideband`）

!!! important "Result View filter contract"
    Result View 的 `Trace Mode Filter`（All/Base/Sideband）必須直接依賴
    `DerivedParameter.extra.trace_mode_group`，不可使用第二套推論器。

## Scope Bridge Contract（Simulation -> Characterization）

!!! note "Current behavior（2026-03-04）"
    既有資料模型仍可記錄 bundle 層級來源（`input_bundle_id`）。

!!! important "Contract（Dataset-centric UI, bundle provenance internal）"
    Characterization UI 以 dataset 為主，不暴露「手動選 Characterization bundle 作為輸入」流程。
    run 候選 traces 由 dataset-level trace index 做 trace-first 篩選；
    provenance 仍可在內部保存 `input_bundle_id` 以支援追溯。

!!! warning "Input hygiene"
    `analysis_result` 型資料不得被當作下一輪 trace 輸入，除非特定 analysis 有明確契約宣告。

!!! note "Simulation post-process HFSS metadata"
    `hfss_comparable` 與 `input_y_source` 屬於 `simulation_postprocess` bundle 的 provenance 欄位，
    定義於 `Dataset Record Schema`。
    Characterization `analysis_run` bundle 不應重複宣告這些欄位作為 authority。

## JSON Example（characterization run bundle）

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

- [Dataset Record Schema](dataset-record.md)
- [Characterization](../ui/characterization.md)
