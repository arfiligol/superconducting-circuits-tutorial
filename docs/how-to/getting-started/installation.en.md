---
aliases:
  - "Installation"
tags:
  - diataxis/how-to
  - status/draft
  - topic/getting-started
---

# Installation

This tutorial uses Julia and the JosephsonCircuits.jl package.

## Prerequisites

- Julia 1.9 or later
- Git (for version control)

## Install Julia

### macOS

Using Homebrew:

```bash
brew install julia
```

### Windows / Linux

Download the installer from the [Julia website](https://julialang.org/downloads/).

## Clone the Project

```bash
git clone https://github.com/arfiligol/superconducting-circuits-tutorial.git
cd superconducting-circuits-tutorial
```

## Install Dependencies

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

This will install all required packages based on `Project.toml`, including:

- **JosephsonCircuits.jl** — Core simulation engine
- **PlotlyJS** — Interactive plotting
- **CSV / DataFrames** — Data handling

## Verify Installation

```bash
julia --project=. -e 'using JosephsonCircuits; println("Installation successful!")'
```

## Next Steps

👉 [First Simulation](first-simulation.md)
