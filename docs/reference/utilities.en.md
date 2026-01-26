---
aliases:
  - "Plotting Utilities ili_plot"
tags:
  - diataxis/reference
  - status/draft
---

# Plotting Utilities ili_plot

`ili_plot` is the project's PlotlyJS plotting wrapper that simplifies the plotting workflow.

## Basic Usage

```julia
include("src/plotting.jl")

traces = [
    scatter(x=freqs, y=data1, mode="lines", name="Trace 1"),
    scatter(x=freqs, y=data2, mode="lines", name="Trace 2"),
]

p = ili_plot(
    traces,                  # PlotlyJS traces
    "My Plot Title",         # Title
    "X Axis Label",          # X-axis label
    "Y Axis Label",          # Y-axis label
    "Legend Title"           # Legend title
)

display(p)
```

## Function Signature

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

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `traces` | `Vector` | PlotlyJS scatter traces |
| `title` | `String` | Chart title |
| `xaxis_title` | `String` | X-axis label |
| `yaxis_title` | `String` | Y-axis label |
| `legend_title` | `String` | Legend title |
| `x_range` | `Tuple` | X-axis range, e.g., `(0, 10)` |
| `y_range` | `Tuple` | Y-axis range, e.g., `(-180, 180)` |

## Example: Limiting Y-axis Range

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

## Other Utility Functions

### unwrap_phase

Unwrap phase to avoid ±180° jumps:

```julia
phase_rad = angle.(S11)
phase_unwrapped = unwrap_phase(phase_rad)
phase_deg = rad2deg.(phase_unwrapped)
```

### format_value_with_unit

Auto-format values with units:

```julia
format_value_with_unit(10e-9, :L)  # => "10.00 nH"
format_value_with_unit(1e-12, :C)  # => "1.00 pF"
```
