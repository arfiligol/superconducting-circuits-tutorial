---
aliases:
  - "flux-dependence-plot"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "磁通依賴熱圖繪製指令說明"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# flux-dependence-plot

繪製磁通依賴 (Flux Dependence) 掃描數據的熱圖 (Heatmap) 與切片圖 (Slice)。

## Usage

```bash
uv run flux-dependence-plot [OPTIONS] [components ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `components` | `data/preprocessed/` 下的組件 ID 或 JSON 路徑 | 內建預設清單 |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--parameter` | 參數名稱 (例如 `S11`) | `S11` |
| `--view` | 繪製視圖 (`amplitude`, `phase`, `combined`, `all`) | `all` |
| `--phase-unit` | 相位單位 (`rad`, `deg`) | `rad` |
| `--wrap-phase` | 是否將相位包裹在 $\pm\pi$ 或 $\pm 180^\circ$ | False |
| `--slice-frequency` | 擷取特定頻率 (GHz) 的 Bias 切片 | |
| `--slice-bias` | 擷取特定 Bias (mA) 的頻率切片 | |
| `--device` | 自訂圖表中的 Device 標籤 | Component ID |
| `--matplotlib` | 使用 Matplotlib 渲染 (預設: Plotly) | False |

## Examples

**繪製所有視圖 (Amplitude + Phase)**
```bash
uv run flux-dependence-plot LJPAL6572_B44D1
```

**僅繪製相視圖 (Phase)，使用角度顯示**
```bash
uv run flux-dependence-plot --view phase --phase-unit deg LJPAL6572_B44D1
```

**繪製特定切片**
```bash
uv run flux-dependence-plot \
    --slice-frequency 6.0 \
    --slice-bias 0.0 \
    LJPAL6572_B44D1
```
