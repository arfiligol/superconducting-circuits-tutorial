---
aliases:
  - "繪圖工具 ili_plot"
tags:
  - diataxis/reference
  - status/draft
---

# 繪圖工具 ili_plot

`ili_plot` 是專案提供的 PlotlyJS 繪圖封裝，簡化繪圖流程。

## 基本用法

```julia
include("src/julia/plotting.jl")

traces = [
    scatter(x=freqs, y=data1, mode="lines", name="Trace 1"),
    scatter(x=freqs, y=data2, mode="lines", name="Trace 2"),
]

p = ili_plot(
    traces,                  # PlotlyJS traces
    "My Plot Title",         # 標題
    "X Axis Label",          # X 軸標籤
    "Y Axis Label",          # Y 軸標籤
    "Legend Title"           # 圖例標題
)

display(p)
```

## 函式簽名

```julia
function ili_plot(
    traces::Vector{<:AbstractTrace},
    title::String,
    xaxis_title::String,
    yaxis_title::String,
    legend_title::String="Legend";
    x_range=nothing,
    y_range=nothing,
    width=nothing,
    height=nothing
)
```

## 參數說明

| 參數 | 類型 | 說明 |
|------|------|------|
| `traces` | `Vector` | PlotlyJS scatter traces |
| `title` | `String` | 圖表標題 |
| `xaxis_title` | `String` | X 軸標籤 |
| `yaxis_title` | `String` | Y 軸標籤 |
| `legend_title` | `String` | 圖例標題 |
| `x_range` | `Tuple` | X 軸範圍，如 `(0, 10)` |
| `y_range` | `Tuple` | Y 軸範圍，如 `(-180, 180)` |

## 範例：限制 Y 軸範圍

```julia
p = ili_plot(
    traces,
    "S11 Phase",
    "Frequency (GHz)",
    "Phase (deg)",
    "Parameter";
    y_range=(-180, 180)
)
```

## 其他工具函式

### unwrap_phase

展開相位，避免 ±180° 跳變：

```julia
phase_rad = angle.(S11)
phase_unwrapped = unwrap_phase(phase_rad)
phase_deg = rad2deg.(phase_unwrapped)
```

### format_value_with_unit

自動格式化數值和單位：

```julia
format_value_with_unit(10e-9, :L)  # => "10.00 nH"
format_value_with_unit(1e-12, :C)  # => "1.00 pF"
```
