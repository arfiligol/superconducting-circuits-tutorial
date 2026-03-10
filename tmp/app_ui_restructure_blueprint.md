# App UI Restructure Blueprint

## Why This Exists

`src/app/pages/simulation/__init__.py` is now over 10,000 lines.
That is not a "large page"; it is a collapsed subsystem.

At this size, the file is doing too many jobs at once:

- page routing
- shell composition
- form state
- API polling
- persisted result recovery
- trace-store conversion
- plotting
- post-processing orchestration
- saved-setup management
- termination-compensation UI
- task/status UX

This violates SRP and makes the `src/app` tree unreadable.

The goal of this blueprint is:

- make `src/app` readable from directory structure alone
- make each feature own a clear UI boundary
- stop new 1k+ line page files from forming
- align UI code with the accepted persisted-task architecture

## Current Audit

Largest `src/app` Python files:

- `10298` lines: `src/app/pages/simulation/__init__.py`
- `2985` lines: `src/app/pages/characterization/__init__.py`
- `768` lines: `src/app/pages/raw_data.py`
- `683` lines: `src/app/services/characterization_runner.py`

Current structural problems:

1. `pages/` mixes route entrypoints with full feature implementation.
2. `services/` is a flat catch-all bucket rather than a readable application layer.
3. `simulation` and `characterization` are not modeled as feature packages end-to-end.
4. UI sections, state, task recovery, and visualization are still too entangled.
5. Shared widgets/patterns are not first-class packages, so pages rebuild local UI machinery.

## Target Principles

1. Route files are thin.
2. Feature packages are first-class.
3. Page layout and workflow orchestration are separate.
4. Shared UI primitives live in one obvious place.
5. View state is local to a feature package, not smeared across page files.
6. Persisted task/result authority stays outside widgets and panels.
7. Directory names should explain application structure without opening files.

## Target `src/app` Shape

```text
src/app/
├── main.py
├── layout.py
├── api/
│   ├── router.py
│   ├── dependencies.py
│   ├── schemas.py
│   └── routes/
├── auth/
│   ├── pages/
│   │   └── login_page.py
│   ├── services/
│   └── session.py
├── features/
│   ├── simulation/
│   │   ├── page.py
│   │   ├── state.py
│   │   ├── api_client.py
│   │   ├── task_authority.py
│   │   ├── submit/
│   │   │   ├── simulation.py
│   │   │   └── post_processing.py
│   │   ├── recovery/
│   │   │   ├── simulation_results.py
│   │   │   └── post_processing_results.py
│   │   ├── setup/
│   │   │   ├── saved_setups.py
│   │   │   ├── frequency_sweep.py
│   │   │   ├── sources.py
│   │   │   ├── parameter_sweep.py
│   │   │   └── termination_compensation.py
│   │   ├── views/
│   │   │   ├── netlist_panel.py
│   │   │   ├── simulation_results.py
│   │   │   ├── sweep_results.py
│   │   │   ├── post_processing_panel.py
│   │   │   └── post_processing_results.py
│   │   └── plotters/
│   ├── characterization/
│   │   ├── page.py
│   │   ├── state.py
│   │   ├── api_client.py
│   │   ├── task_authority.py
│   │   ├── submit.py
│   │   ├── recovery.py
│   │   ├── views/
│   │   │   ├── dataset_scope.py
│   │   │   ├── trace_selection.py
│   │   │   ├── run_panel.py
│   │   │   └── result_views.py
│   │   └── query/
│   ├── raw_data/
│   │   ├── page.py
│   │   ├── filters.py
│   │   └── table.py
│   ├── schemas/
│   │   ├── page.py
│   │   ├── editor_page.py
│   │   └── schemdraw_preview_page.py
│   └── dashboard/
│       └── page.py
├── services/
│   ├── execution_context.py
│   ├── task_progress.py
│   ├── task_submission.py
│   ├── latest_result_lookup.py
│   └── feature_shared/
├── ui/
│   ├── cards.py
│   ├── forms.py
│   ├── status.py
│   ├── result_family_explorer.py
│   ├── tables.py
│   └── empty_states.py
└── styles/
```

## Reading Rules

If someone looks only at the directory tree, they should be able to answer:

- where routing lives
- where auth lives
- where simulation UI lives
- where characterization UI lives
- where shared UI widgets live
- where persisted task/result orchestration lives

If the answer is "open a 3k line file and search", the structure is still wrong.

## Required Boundaries

### 1. Route Entry Boundary

Each route entry file should do only:

- `@ui.page(...)`
- page-specific auth guard wiring
- call a feature `build_page(...)` or `render_page(...)`

No heavy workflow logic in route files.

### 2. Feature Page Boundary

`features/<feature>/page.py` may compose:

- sections/panels
- feature-local state
- feature-local callbacks
- persisted authority refresh hooks

But it should not own:

- shared plotting helpers
- general task submission infrastructure
- raw persistence repository logic

### 3. Feature State Boundary

`state.py` holds only feature-local UI state:

- selected tabs
- selected row ids
- current task id
- visible warnings
- transient input state

It must not become a dumping ground for:

- trace-store conversion helpers
- plotting builders
- persistence adapters

### 4. Shared Service Boundary

`src/app/services/` should be reserved for cross-feature application services:

- task submission
- result lookup
- auth/session helpers
- shared execution context

Feature-specific service logic should move into feature packages unless it is truly shared.

### 5. Shared UI Boundary

Reusable UI widgets belong under `src/app/ui/`, not hidden inside feature pages:

- app cards
- status banners
- result family explorers
- reusable filter bars
- empty states

## Mandatory File Size Budgets

These are enforcement budgets, not suggestions:

- route entry file: `<= 120` lines
- feature `page.py`: `<= 400` lines
- any UI panel/view module: `<= 300` lines
- any app service module: `<= 250` lines unless justified
- if a file exceeds `500` lines, it must be split before adding new workflow logic

With these budgets:

- `simulation` will become a package of 10 to 20 modules
- `characterization` will become a package of 6 to 12 modules
- large but readable is acceptable
- giant omnifiles are not

## Concrete Split Plan

### Phase A: Stop the Bleeding

Do this first:

1. No new feature logic goes into `src/app/pages/simulation/__init__.py`
2. No new feature logic goes into `src/app/pages/characterization/__init__.py`
3. Add TODO headers in those files marking them as decomposition targets

### Phase B: Normalize Route Layout

Move from:

- `src/app/pages/simulation/__init__.py`
- `src/app/pages/characterization/__init__.py`

Toward:

- `src/app/features/simulation/page.py`
- `src/app/features/characterization/page.py`
- tiny route wrappers under `src/app/pages/`

### Phase C: Extract Simulation by Responsibility

Split `simulation` into these buckets first:

1. `setup/`
   - saved setups
   - frequency sweep
   - sources
   - parameter sweep
   - termination compensation
2. `submit/`
   - simulation task submit
   - post-processing task submit
3. `recovery/`
   - persisted task polling
   - latest-result restore
4. `views/`
   - raw result view
   - sweep result view
   - post-processing input panel
   - post-processing result view
5. `plotters/`
   - plot-building only

### Phase D: Extract Characterization by Responsibility

Split `characterization` into:

1. `query/`
   - trace scope
   - dataset/run query helpers
2. `submit.py`
   - characterization task submit
3. `recovery.py`
   - persisted task/run restore
4. `views/`
   - trace selection
   - result artifacts
   - run controls
   - post-run result views

### Phase E: Create Shared UI Package

Promote reusable UI patterns to `src/app/ui/`:

- status cards
- task progress blocks
- result family explorer
- common form rows
- reusable table wrappers

### Phase F: Clean `services/`

Split `services/` into:

- truly shared cross-feature services stay in `src/app/services/`
- feature-specific helpers move into `src/app/features/<feature>/...`

Current likely candidates to remain shared:

- `auth_service.py`
- `execution_context.py`
- `task_progress.py`
- `task_submission.py`
- `latest_result_lookup.py`

Current likely candidates to move under features:

- `simulation_runner.py`
- `simulation_submission.py`
- `simulation_batch_persistence.py`
- `post_processing_runner.py`
- `post_processing_support.py`
- `post_processing_batch_persistence.py`
- `characterization_runner.py`
- `characterization_trace_scope.py`

## The Main Refactor Rule

Each extraction must preserve this dependency direction:

- `pages/route wrapper` -> `features/<feature>/page.py`
- `features/<feature>/page.py` -> feature-local modules + shared app services
- shared app services -> core/shared persistence + core application boundaries

Never reverse it.

## What "Good" Looks Like

After the restructure:

- opening `src/app/` should show product structure, not a random bucket of pages/services
- `simulation` and `characterization` should each read like self-contained feature packages
- route entry files should become boring
- app services should become obviously cross-feature
- page modules should be compositional, not encyclopedic

## Recommended Execution Order

1. Introduce `src/app/features/`
2. Move route wrappers to thin page entry files
3. Extract `simulation/setup/termination_compensation.py`
4. Extract `simulation/views/`
5. Extract `simulation/recovery/`
6. Extract `characterization/recovery.py`
7. Extract `characterization/views/`
8. Promote shared widgets to `src/app/ui/`
9. Flatten and shrink `src/app/services/`

## Success Criteria

The restructure is successful when:

- no UI file exceeds the file-size budgets above
- `src/app/pages/` becomes thin route wrappers
- `src/app/features/` becomes the primary app-reading surface
- `simulation` and `characterization` no longer require reading giant `__init__.py` files to understand the feature
- a new contributor can infer the application architecture from the tree alone
