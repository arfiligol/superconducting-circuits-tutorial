---
aliases:
 - Notebook Roles
 - Pluto and Python notebook roles
tags:
 - diataxis/reference
 - audience/team
 - sot/true
 - topic/research-contracts
status: stable
owner: docs-team
audience: team
scope: Contract-level Pluto and Python notebook responsibilities, including the accepted staged Circuit Runtime boundary.
version: v1.2.0
last_updated: 2026-09-08
updated_by: codex
title: Notebook Roles
description: Defines Pluto and Python notebook responsibilities for circuit execution, external-result analysis, quantum modeling, and pulse simulation.
sidebar:
 label: Notebook Roles
 order: 50
---

# Notebook Roles

Notebooks are research surfaces, not package ownership surfaces. Each notebook type has a route-specific job.

## Package And Consumer Responsibilities

Read the Workbench documentation matching the installed package revision.
Package usage does not require SCQ collaboration Skills or a parent checkout.
Use the host's research contract only when the work needs its design meaning.

The consumer repository owns Notebook placement, the editable source, pairing,
execution permission, environment, and output retention. Preserve its accepted
format and Human outputs; do not convert existing Pluto or paired Python
Notebooks merely for uniformity. Where pairing is used, keep one editable
source and use that repository's deterministic synchronization procedure.

Workbench owns API usage, prerequisites, result schemas, and generic reporting.
Its [Python consumer contract](circuit-runtime-python-consumer.md) defines the
available stages, independent operations, artifact binding, and failure behavior.
Consumer code declares the plan, controls, and input data; it does not duplicate
the package's solvers, receipt writers, or report builders.

## Pluto Notebook

Pluto owns the direct Julia research cockpit:

- reusable circuit authoring experiments
- Julia Core component and plan-builder studies
- JosephsonCircuits.jl response studies
- sweep design and inspection
- result figure exploration through Julia Visualizer
- explicit bridge calls into Python Analysis Core when the analysis belongs beside a Julia study

Pluto may consume normalized external result packages, but it should not become the primary external RF file importer.

The [Pluto authoring and presentation reference](../agent-skills/write-pluto-notebook.mdx)
owns the retained reactive cell, PlutoUI, Markdown, figure-layout, environment,
and raw-file conventions. The [Pluto Authoring Workflow](../../workflows/reusable-circuit-authoring/pluto-authoring-workflow.mdx)
owns the concrete Julia Core procedure. These apply to Workbench Pluto users;
they do not define another package's Runtime API.

## Python Notebook

Python notebooks are the routine client for the public circuit runtime
and also own Python-native research exploration:

- visible generic `CircuitPlan` assembly and consumer-owned circuit libraries
- declarative artifact bindings, reduction, cared outputs, objective, exact
  Human-authorized Gates, variables, and optimizer controls
- explicit `CircuitSim` stages: `optimize`, `refine_winner`,
  `evaluate_responses`, `fit_c11`, `evaluate_t1`, and `build_report`
- an explicit visible `execute` or `resolve` selection, which may be shared
  across stage calls according to the consumer's Notebook UX
- pure-Python, read-only result, campaign, and report resolution

- trace table, Touchstone, and Zarr ingestion sketches
- scikit-rf-compatible inspection and conversion
- fitting experiments before promotion to Python Analysis Core
- scqubits, QuTiP, and qutip-qip studies
- consumer-specific report interpretation

Python notebooks may read local/exported/canonical data files directly for ad
hoc analysis. Persistent application state mutations stay out of research
notebooks and use the application service contracts.

## Process Boundary

`execute` performs one complete named stage. A Julia-backed stage starts exactly
one Julia process for that action; candidate and frequency-point work never
calls back into Python. Python-owned fit/report stages start none. `resolve` and
the result/campaign/report readers are pure Python and read-only: they start no
Julia process, recompute nothing, mutate nothing, and fail closed over absent,
stale, incomplete, or identity-mismatched evidence.

The notebook owns visible plan assembly and consumer declarations, not stage
orchestration internals, identities, receipt writing, scientific calculations,
or generic report construction. Each independent case should use an explicit
run directory; campaign readers consume only the directories the notebook
lists and never select a latest run.

Python notebooks must not import `juliacall`, invoke Julia Core directly, build
C/K/G, or call Schur helpers. Application execution remains a separate
persisted service/Julia Runner path. See
[Circuit Runtime / Python Consumer](circuit-runtime-python-consumer.md) for the
accepted package, schema, ownership, and failure contract.

## Results And Report Presentation

Use the package's result and report readers for generic tables and plots.
Present the exact input/source identity, parameters and units, backend,
frequency grid, and run identity from the existing machine-readable evidence;
retain CSV/JSON or the repository-native evidence with review figures and HTML
under the consumer's retention and data-classification rules.

Optimization views should make the request, history, residuals, winner
parameters, and response evidence inspectable when those stages were requested.
T1 views must state the admittance definition, capacitance/model assumptions,
and evaluation frequency supported by the result. A readable report preserves
missing, failed, or diagnostic states and does not confer scientific acceptance.
Do not invent missing results, optimization claims, or acceptance thresholds.

## Related

- [Notebook Interface](../notebooks/index.md)
- [FEM Result To Equivalent Circuit](../../workflows/fem-result-to-equivalent-circuit/index.md)
- [Equivalent Circuit To Quantum Model](../../workflows/equivalent-circuit-to-quantum-model/index.md)
- [Quantum Dynamics / Pulse Simulation](../../workflows/quantum-dynamics-pulse-simulation/index.md)
- [Circuit Research Routes](../../concepts/gdsfactory-compatible-artifacts/circuit-research-routes.md)
- [Circuit Runtime / Python Consumer](circuit-runtime-python-consumer.md)
