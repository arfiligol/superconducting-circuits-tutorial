---
aliases:
  - Project Overview
  - Product Scope
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/project-basics
status: stable
owner: docs-team
audience: contributor
scope: Defines the rewrite-branch mission, product scope, desktop support, and migration direction.
version: v2.1.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Project Overview

This project no longer treats NiceGUI as the primary product direction.
The current branch goal is to rebuild the existing requirements as a **separated frontend/backend superconducting-circuit workbench** while preserving CLI workflows, the scientific core, and a local desktop runtime option.

## Mission

Build a platform where researchers can perform the following within one system:

- Data Browser
- Circuit Definition Editor
- Circuit Schemdraw
- Circuit Simulation
- Characterization & Analysis
- CLI Available

## Scope

### Core Product Surfaces

| Capability | Description |
| --- | --- |
| Data Browser | Browse metadata, trace summaries, analysis results, and lineage |
| Circuit Definition Editor | Edit canonical circuit/netlist/schema definitions with validation and formatting |
| Circuit Schemdraw | Generate circuit diagrams from the canonical circuit definition |
| Circuit Simulation | Run simulations and sweeps powered by `JosephsonCircuits.jl` |
| Characterization & Analysis | Apply one shared workflow to simulation / layout / measurement traces, including post-processing, fitting, comparison, extraction, and visualization |
| CLI Available | Every critical workflow must remain executable from CLI, not UI-only |

### Accepted Data Sources

- circuit simulation traces
- layout simulation traces (for example HFSS / Q3D)
- measurement traces (for example VNA)
- compatible S/Y/Z matrix traces and their derived analysis results

### Rewrite Direction

- UI: **Next.js App Router**
- API: **FastAPI**
- CLI: stays first-class and shares rules/services with the API/core
- Desktop: **Electron** may wrap the frontend to provide a locally runnable desktop app
- Legacy: existing NiceGUI remains migration reference only, not the default implementation target for new work

## Target Audience

- superconducting-circuit and quantum-hardware researchers
- users who need to align simulation / layout / measurement workflows
- developers who need reproducible CLI workflows plus an extensible web UI

## Agent Rule { #agent-rule }

```markdown
## Project Goal
- **Mission**: Build a superconducting-circuit workbench with a separated frontend/backend architecture and first-class CLI support.
- **Core product surfaces**:
    - Data Browser
    - Circuit Definition Editor
    - Circuit Schemdraw
    - Circuit Simulation
    - Characterization & Analysis
    - CLI Available
- **Data sources**:
    - circuit simulation
    - layout simulation
    - measurement
    - compatible S/Y/Z traces
- **Architecture direction**:
    - UI uses Next.js App Router
    - API uses FastAPI
    - CLI stays supported and must share business rules with the core/backend
    - Electron is an allowed desktop wrapper for local-first desktop runtime
    - existing NiceGUI code is legacy, not the default place for new work
- **Core values**:
    - scientific accuracy
    - reproducible workflows
    - one canonical definition feeding UI, API, CLI, simulation, and schemdraw
- **Audience**: researchers, students, and developers working on superconducting-circuit simulation and analysis workflows.
```
