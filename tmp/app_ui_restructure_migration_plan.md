# App UI Restructure Migration Plan

## 0. Purpose

This migration plan restructures `src/app` so that:

- the directory tree explains the app architecture
- route files become thin
- `simulation` and `characterization` stop depending on giant page files
- cross-feature services and shared UI become explicit layers
- future contributors can keep working without rebuilding context from 10k-line files

This is **not** a feature migration like the prior persisted-task architecture work.
It is a **UI structure migration** on top of the accepted architecture.

## 1. Current Problem Statement

Current largest files:

- `src/app/pages/simulation/__init__.py` ≈ 10k lines
- `src/app/pages/characterization/__init__.py` ≈ 3k lines

The current `src/app` layout hides the architecture:

- `pages/` mixes route entrypoints with full feature implementation
- `services/` mixes shared services with feature-specific helpers
- simulation and characterization are not treated as first-class feature packages
- reusable UI patterns are not promoted to a visible shared layer

This causes:

- poor navigability
- SRP violations
- high regression risk
- slow contributor onboarding
- frequent “search the giant file” maintenance

## 2. Migration Scope

### In scope

- restructure `src/app` into feature-oriented packages
- make `pages/` thin route wrappers
- progressively extract simulation and characterization responsibilities
- promote shared UI widgets/primitives into a visible `ui/` layer
- shrink and clarify `services/`
- preserve accepted persisted-task / worker / API architecture

### Out of scope

- redesigning business architecture
- redoing WS2-WS10 persisted-task semantics
- API redesign
- auth redesign
- worker topology redesign
- visual redesign as the primary goal
- broad cross-repo cleanup unrelated to UI structure

## 3. Frozen Constraints

The following accepted architecture remains frozen during this restructure:

- persisted task/result authority remains canonical
- app-side route/page code must not retake heavy execution authority
- dual worker lanes remain intact
- public `/api/v1/*` remains intact
- local auth/session remains intact
- no new module-level process-global caches

## 4. Target Structure

The target `src/app` shape is:

```text
src/app/
├── main.py
├── layout.py
├── api/
├── auth/
├── features/
│   ├── simulation/
│   ├── characterization/
│   ├── raw_data/
│   ├── schemas/
│   └── dashboard/
├── services/
├── ui/
└── styles/
```

Interpretation:

- `pages/`: route wrappers only
- `features/`: actual page/feature implementation
- `services/`: cross-feature app services only
- `ui/`: reusable UI building blocks

## 5. File Responsibility Rules

### 5.1 `pages/`

Allowed responsibilities:

- route decorator
- auth guard
- invoke feature page builder

Not allowed:

- feature workflow
- task polling logic
- persisted recovery orchestration
- heavy result view composition

### 5.2 `features/<feature>/`

Allowed responsibilities:

- feature page composition
- feature-local state
- feature-local callbacks
- feature-local recovery/submit wiring
- feature-local views

### 5.3 `services/`

Reserved for truly shared app services only:

- auth/session services
- task submission
- latest result lookup
- execution context
- task progress mapping

### 5.4 `ui/`

Reserved for reusable UI widgets and display patterns:

- cards
- status/empty states
- shared result explorers
- table wrappers
- common forms

## 6. Size Budgets

These are migration enforcement budgets:

- route wrapper file: `<= 120` lines
- feature `page.py`: `<= 400` lines
- view/panel module: `<= 300` lines
- app service module: `<= 250` lines unless strongly justified

If a file exceeds `500` lines after migration, it is still a decomposition target.

## 7. Review-First Workflow

This migration uses **review-first** execution.

Meaning:

- Contributor Agent focuses on implementation and clean handoff
- Integrator reviews code for risk/regression/architecture drift
- heavy runtime validation is not the main acceptance gate for now
- if checks are not run, the contributor must say so explicitly

Required contributor handoff:

- commit hashes
- changed files with reasons
- impact summary
- known risks
- any checks run, honestly reported

## 8. Workstreams

### UI-WS1: Establish the Feature Skeleton

Goal:

- introduce `src/app/features/`
- introduce thin route-wrapper direction
- create the first explicit package boundaries without large behavior changes

Primary deliverables:

- `src/app/features/simulation/`
- `src/app/features/characterization/`
- route wrappers or route-adjacent modules that forward into feature page builders
- minimal imports rewired so the new structure becomes the canonical reading surface

Non-goals:

- no major workflow extraction yet
- no large behavior changes
- no API changes unless required for import relocation

Success criteria:

- `src/app/features/` exists and is real, not placeholder-only
- route entrypoints become visibly thinner
- future extractions have a stable landing zone

### UI-WS2: Extract Simulation Setup Modules

Goal:

- remove setup/config responsibilities from the simulation giant file

Expected split:

- `features/simulation/setup/saved_setups.py`
- `features/simulation/setup/frequency_sweep.py`
- `features/simulation/setup/sources.py`
- `features/simulation/setup/parameter_sweep.py`
- `features/simulation/setup/termination_compensation.py`

Success criteria:

- setup logic is no longer buried in one page file
- termination compensation becomes an isolated module
- simulation page file size materially decreases

### UI-WS3: Extract Simulation Views

Goal:

- remove rendering-heavy view code from the simulation giant file

Expected split:

- `features/simulation/views/netlist_panel.py`
- `features/simulation/views/simulation_results.py`
- `features/simulation/views/sweep_results.py`
- `features/simulation/views/post_processing_panel.py`
- `features/simulation/views/post_processing_results.py`

Success criteria:

- rendering concerns are separated from submit/recovery logic
- plot/result view code becomes locally understandable

### UI-WS4: Extract Simulation Recovery and Submit

Goal:

- isolate persisted authority orchestration inside feature-local modules

Expected split:

- `features/simulation/recovery/simulation_results.py`
- `features/simulation/recovery/post_processing_results.py`
- `features/simulation/submit/simulation.py`
- `features/simulation/submit/post_processing.py`

Success criteria:

- simulation page no longer directly owns all persisted polling/recovery/submit workflow
- feature page becomes coordinator, not giant executor

### UI-WS5: Extract Characterization Feature Package

Goal:

- shrink `src/app/pages/characterization/__init__.py`

Expected split:

- `features/characterization/page.py`
- `features/characterization/state.py`
- `features/characterization/api_client.py`
- `features/characterization/recovery.py`
- `features/characterization/submit.py`
- `features/characterization/query/`
- `features/characterization/views/`

Success criteria:

- characterization route/page becomes compositional
- persisted run/task authority remains intact
- page-local logic is clearly segmented

### UI-WS6: Promote Shared UI

Goal:

- create `src/app/ui/` and move reusable UI patterns there

Likely targets:

- empty states
- status banners
- result family explorer
- shared form fragments
- reusable table/pagination surfaces

Success criteria:

- duplication across simulation/characterization/raw-data routes decreases
- UI building blocks become discoverable

### UI-WS7: Shrink and Clarify `services/`

Goal:

- leave only cross-feature app services in `src/app/services/`

Likely to remain:

- `auth_service.py`
- `execution_context.py`
- `task_progress.py`
- `task_submission.py`
- `latest_result_lookup.py`

Likely to move to features:

- simulation-specific service helpers
- post-processing-specific service helpers
- characterization-specific service helpers

Success criteria:

- `services/` becomes obviously cross-feature
- feature-specific helpers stop polluting the shared service layer

### UI-WS8: Final Route Normalization and Budget Pass

Goal:

- ensure `pages/` is thin
- ensure major files meet the new budgets
- do a final directory readability pass

Success criteria:

- route wrappers are thin
- feature packages are the obvious app reading surface
- no giant page file remains the only way to understand the feature

## 9. Execution Order

Required order:

1. UI-WS1
2. UI-WS2
3. UI-WS3
4. UI-WS4
5. UI-WS5
6. UI-WS6
7. UI-WS7
8. UI-WS8

Reason:

- first create landing zones
- then extract the worst hot spot (`simulation`)
- then extract the second hot spot (`characterization`)
- only after that normalize shared layers

## 10. Allowed-Files Guidance Per Workstream

These are guidance boundaries for future contributor prompts.

### UI-WS1

- `src/app/pages/**`
- `src/app/features/**`
- minimal `src/app/main.py` / `src/app/layout.py` if route registration requires it
- tests only if import path updates need them

### UI-WS2 to UI-WS4

- `src/app/pages/simulation/**`
- `src/app/features/simulation/**`
- minimal shared app services if required
- relevant tests

### UI-WS5

- `src/app/pages/characterization/**`
- `src/app/features/characterization/**`
- minimal shared app services if required
- relevant tests

### UI-WS6

- `src/app/ui/**`
- touched feature views
- relevant tests

### UI-WS7

- `src/app/services/**`
- touched feature packages
- relevant tests

### UI-WS8

- `src/app/pages/**`
- `src/app/features/**`
- `src/app/ui/**`
- relevant docs/tests if route references change

## 11. Handoff / Reporting Rules

Every contributor batch must:

- stay inside its workstream
- produce one or more coherent commits
- explain why each moved module now belongs in its new location
- call out any remaining large residuals honestly

The Integrator review should prioritize:

- architecture drift
- wrong-layer logic
- hidden page-local authority returning
- imports that re-tangle feature boundaries
- fake extraction where code moved files but kept the same giant dependency knot

## 12. Definition of Done

This migration is done only when all of the following are true:

1. `src/app/features/` is the primary app-reading surface
2. `src/app/pages/` is thin and boring
3. `simulation` no longer requires reading a 10k-line file to understand the feature
4. `characterization` no longer requires reading a giant page file to understand the feature
5. `services/` clearly means cross-feature service
6. `ui/` clearly means shared UI building blocks
7. directory structure alone explains the application shape

## 13. First Contributor Task Recommendation

The first contributor task should be **UI-WS1 only**.

Reason:

- it is the safest structural foundation
- it creates stable landing zones for later extractions
- it avoids starting with the most volatile workflow code
- it is easier to review than a direct attack on the 10k-line simulation page
