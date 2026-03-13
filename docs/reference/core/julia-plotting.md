---
aliases:
  - Julia Plotting Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/core-reference
status: stable
owner: docs-team
audience: team
scope: Julia plotting 與 Julia-owned visualization reference surface。
version: v0.3.0
last_updated: 2026-03-13
updated_by: team
---

# Julia Plotting

本頁收錄 repository 內目前可見的 Julia-owned plotting / visualization helper surface。

!!! info "Surface Boundary"
    本頁描述的是 Julia-side figure helper，而不是 result persistence contract。
    trace / result handles 仍由 backend 與 Python-owned core contract 決定。

!!! warning "Authority Rule"
    本頁只記錄 `src/julia/plotting.jl` 與 `src/julia/utils.jl` 目前實際可見的 helper surface。
    若 helper 名稱與 repository file 不一致，應以 repository file 為準。

## Published Helpers

| Helper | File | Responsibility |
|---|---|---|
| `unwrap_phase(phases)` | `src/julia/plotting.jl` | 將 phase trace 做 unwrapping |
| `format_value_with_unit(val, param_name)` | `src/julia/plotting.jl` | 以參數名稱 heuristic 格式化顯示值 |
| `apply_plotly_layout(p; ...)` | `src/julia/plotting.jl` | 為 PlotlyJS plot 套用 title、axis、legend、range、size layout |
| `plot_result(result; type=:phase, fixed_indices=...)` | `src/julia/plotting.jl` | 依 `SimulationResult` 產生 PlotlyJS figure |
| helper alias boundary | `src/julia/utils.jl` | 提供 Julia-side helper re-export 入口 |

## `plot_result` Modes

| `type` value | Meaning |
|---|---|
| `:phase` | 顯示 phase (deg) sweep |
| `:magnitude` | 顯示 magnitude sweep |
| `:imY11` | 顯示 imaginary admittance sweep |

## `apply_plotly_layout` Parameters

| Parameter | Meaning |
|---|---|
| `title` | plot title |
| `xaxis_title` | x-axis label |
| `yaxis_title` | y-axis label |
| `legend_title` | legend title |
| `x_range`, `y_range` | axis range override |
| `width`, `height` | figure size override |

!!! example "Usage"
    ```julia
    include("src/julia/plotting.jl")

    p = plot_result(result; type=:phase)
    display(p)
    ```

## Related

- [Julia Core](julia-core.md)
- [How-to / Native Julia Simulation](../../how-to/simulation/native-julia.md)
