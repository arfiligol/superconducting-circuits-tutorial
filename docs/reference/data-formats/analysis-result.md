---
aliases:
  - "Analysis Result Schema"
  - "分析結果格式"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "分析腳本輸出的結果格式 (TypedDict)"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Analysis Result Schema

分析腳本（如 `squid-model-fit`）輸出的分析結果結構，定義於 `src/types.py`。

## ModeFitResult

單一 Mode 的擬合結果。

```python
class ModeFitSuccess(TypedDict):
    status: Literal["success"]
    params: ModeFitParams       # { "Ls_nH": float, "C_eff_pF": float }
    metrics: ModeFitMetrics     # { "RMSE": float }
    raw_data: ModeFitSeries     # { "L_jun": [], "Freq": [] }
    fit_curve: ModeFitSeries    # { "L_jun": [], "Freq": [] }
```

## FitResultsByMode

整個元件的擬合結果（包含多個 Mode）。

```python
FitResultsByMode = dict[str, ModeFitResult]
# Key: "Mode 1", "Mode 2", ...
```

## AnalysisEntry

單一檔案的完整分析紀錄。

```python
class AnalysisEntry(TypedDict):
    filename: str
    fits: FitResultsByMode
```

## Usage

這些結構主要用於：
1. 分析腳本內部的數據傳遞。
2. 視覺化模組 (`src/visualization/plot_utils.py`) 繪製圖表時的輸入格式。

## Related

- [Admittance Fit](../../how-to/analysis/admittance-fit.md) - 產生 Report 的工具
