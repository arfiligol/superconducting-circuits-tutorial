---
aliases:
  - "Project Overview"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Project Overview

The project goal has expanded from a tutorial website into a bilingual **superconducting-circuit design data platform** plus documentation system.

## Mission

Build a high-quality bilingual (Traditional Chinese / English) platform where users can, within a single `Design` scope:

- define and simulate circuits
- import and analyze layout simulation traces
- import and analyze measurement traces
- run one shared Characterization workflow over compatible S/Y/Z matrix traces
- compare layout / circuit / measurement outputs

## Scope

- **Data sources**
  - circuit simulation (`JosephsonCircuits.jl`)
  - layout simulation (HFSS/Q3D and similar tools)
  - measurement (for example VNA)
- **Unified analysis input**
  - S/Y/Z matrix traces
- **Core UI**
  - Schema Editor
  - Circuit Simulation
  - Post-Processing
  - Characterization
- **Documentation**
  - Zensical, bilingual (zh-TW / en)

## Target Audience

- researchers and students working on superconducting circuits / quantum hardware
- users comparing layout / circuit / measurement differences
- developers building trace-first characterization workflows

---

## Agent Rule { #agent-rule }

```markdown
## Project Goal
- **Mission**: Build a bilingual superconducting-circuit design data platform plus tutorial/docs system.
- **Scope**:
    - **Sources**: circuit simulation, layout simulation, and measurement.
    - **Simulation**: `JosephsonCircuits.jl` (Julia).
    - **Analysis**: one characterization workflow over compatible S/Y/Z matrix traces.
    - **Storage direction**: metadata DB + external trace store.
- **Core Values**:
    - **Scientific Accuracy**: physics and equations must remain rigorous.
    - **Trace-first analysis**: characterization operates on trace compatibility, not source-kind-specific UI rules.
    - **Bilingual**: primary content remains **Traditional Chinese (zh-TW)** with synced English pages.
- **Target Audience**: researchers, students, and developers working on superconducting-circuit simulation and analysis workflows.
```
