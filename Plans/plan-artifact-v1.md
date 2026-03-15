# Plan Artifact v1

This file is the sole planning baseline for the rewrite as of 2026-03-14.
All prior files under `Plans/` are superseded and removed.
This artifact uses the current Source of Truth only. Historical plans, migration assumptions, and branch intent are not authority.

## 0) Task Information

- Agent: `Planning Agent`
- Task ID / Topic: `L3M-SoT-Rebaseline`
- Status: `Active / Execution checkpoint 2026-03-16`

## 1) Goal

- Rebaseline planning against the current SoT and current code only.
- Identify where code already aligns, where code is behind the SoT, and where legacy design should be removed.
- Define directly assignable implementation slices for Frontend, Backend, Core, CLI, and shared cross-layer work.
- Capture unit, integration, E2E, contract-verification, and removal-safety backlog without writing migration strategy.

## 1.1) Mainline Checkpoint (2026-03-16)

- `main` has already absorbed major progress across `F2`, `F3`, `B3`, `B5`, `C1`, `C2`, `L1`, and `L2`:
  - definition authoring route split, action adoption, and contract polish
  - characterization results, identify/tagging, registry/history, and test evidence
  - canonical backend task queue/control surface and audit-log query surface
  - core task runtime canonicalization, persistence canonicalization, and explicit scope write proofs
  - CLI standalone local runtime, result bundles, and definition bundle interchange
- The largest remaining cross-layer blocker is still `X1` + `B1`: canonical authentication, session, workspace membership, active workspace, active dataset, capability, and allowed-action adoption.
- Execution priority is therefore updated:
  1. `X1` shared identity / auth / envelope adoption
  2. `B1` backend session / workspace / auth surface
  3. frontend shell adoption against the canonical auth/session authority
  4. integration / E2E + docs synchronization pass
- Human choice of external auth provider still remains open, but that decision does **not** block contract-level session/auth adoption.

## 2) Source of Truth

### Primary Authority

- `../docs/reference/index.md`
- `../docs/reference/app/shared/index.md`
- `../docs/reference/app/frontend/index.md`
- `../docs/reference/app/backend/index.md`
- `../docs/reference/cli/index.md`
- `../docs/reference/core/index.md`
- `../docs/reference/data-formats/index.md`

### High-priority Shared Contracts

- `../docs/reference/app/shared/identity-workspace-model.md`
- `../docs/reference/app/shared/resource-ownership-and-visibility.md`
- `../docs/reference/app/shared/authentication-and-authorization.md`
- `../docs/reference/app/shared/response-and-error-contract.md`
- `../docs/reference/app/shared/task-runtime-and-processors.md`
- `../docs/reference/app/shared/audit-logging.md`

### Secondary Consistency Checks

- `../docs/reference/architecture/canonical-contract-registry.md`
- `../docs/reference/architecture/parity-matrix.md`

### Authority Owners

- App Shared owns identity, workspace, auth, visibility, response/error, task runtime, and audit contracts.
- Frontend owns shell, routes, workflow pages, and page-level behavior.
- Backend owns HTTP surfaces and server-side contract delivery.
- CLI owns standalone-first runtime and local/app interchange.
- Core owns validation, runtime contracts, and persistence boundaries.
- Data Formats owns persisted payload shape and canonical naming.

## 3) Current Implementation State

### Aligned Enough To Build From

- The rewrite codebase is already separated into `frontend/`, `backend/`, `cli/`, and `src/core/`.
- Rewrite surfaces for session, datasets, tasks, circuit definitions, and research workflows already exist and can be replaced in place.

### Not Yet Aligned To SoT

- `backend/src/app/api/routers/session.py`, `backend/src/app/services/session_service.py`, and `backend/src/app/domain/session.py` still expose scaffold session fields such as `development_stub`, `scopes`, `can_submit_tasks`, and `can_manage_datasets`, instead of canonical membership, capability, workspace, and allowed-action contracts.
- `backend/src/app/api/errors.py` and `frontend/src/lib/api/client.ts` still use non-canonical response envelopes instead of the shared `ok/data/meta` and canonical error contract.
- `frontend/src/lib/navigation.ts`, `frontend/src/components/layout/workspace-header.tsx`, `frontend/src/components/layout/workspace-shell.tsx`, and `frontend/src/components/layout/workspace-status-strip.tsx` do not implement the SoT shell model for active workspace, active dataset, task queue trigger, and user menu.
- `frontend/src/features/data-browser/components/data-browser-workspace.tsx` conflates dashboard and raw-data browser responsibilities.
- `frontend/src/features/circuit-definition-editor/components/circuit-definition-editor-workspace.tsx` still uses a YAML-like draft model instead of the canonical circuit-netlist structure.
- `backend/src/app/api/routers/tasks.py`, `backend/src/app/services/task_service.py`, and `backend/src/app/infrastructure/runtime.py` do not implement the canonical task lifecycle, control actions, or result-availability model.
- `backend/src/app/api/routers/` does not yet expose schemdraw render, characterization result, or audit-log surfaces.
- `cli/src/sc_cli/runtime.py` and `backend/sc_backend/rewrite_cli.py` keep the CLI service-backed instead of standalone-first.
- `src/core/sc_core/circuit_definitions/inspection.py` is still a placeholder parser and does not validate the canonical circuit-netlist contract.
- `src/core/shared/persistence/models.py`, `src/core/shared/persistence/repositories/contracts.py`, and `src/core/analysis/domain/trace_records.py` still carry legacy naming, aliasing, and `dataset_id` or `design_id` fallback semantics that conflict with current ownership and data-format contracts.

### Clear Conflict Points

- The shared identity/workspace/auth model is defined in SoT but the backend and frontend still consume a development-stub session model.
- The shared response/error contract is defined in SoT but both client and server still parse and emit a legacy envelope.
- The CLI SoT requires standalone-first runtime, while the current CLI imports backend app facade code.
- The data-format SoT defines canonical dataset, design, trace, and result ownership, while core persistence still preserves legacy aliases and mixed naming.

## 4) Removal Candidates

### Legacy App Surface

- Candidate: `src/app/**`
- Why it is removable: workspace folder-structure guardrails already mark it as legacy or migration-only, and current owner docs define the rewrite surfaces elsewhere.
- Impacted dependents: `tests/app/**`, old `/api/v1/*` expectations, and any remaining direct imports into legacy services.
- Verification before removal: replacement rewrite integration and E2E coverage must exist, and rewrite modules must have no `src/app` imports.

### Backend Facade For CLI

- Candidate: `backend/sc_backend/**`
- Why it is removable: it keeps CLI semantics coupled to app backend contracts and blocks standalone-first CLI delivery.
- Impacted dependents: all current `sc_*` commands that resolve through the backend facade.
- Verification before removal: standalone CLI runtime and interchange tests must pass with no backend facade dependency.

### Legacy Core Persistence Aliases

- Candidate: legacy alias models and repository contracts in `src/core/shared/persistence/models.py`, `src/core/shared/persistence/repositories/contracts.py`, and mixed fallback logic in `src/core/analysis/domain/trace_records.py`
- Why they are removable: current SoT already defines canonical naming and ownership; dual naming only preserves stale compatibility semantics.
- Impacted dependents: legacy tests, backend scaffold mappers, and any old service logic still using legacy alias types.
- Verification before removal: canonical persistence round-trip tests and backend dataset or result contract tests must pass.

### Rewrite Scaffold Repositories And Naming

- Candidate: `backend/src/app/infrastructure/rewrite_catalog_repository.py`, `backend/src/app/infrastructure/rewrite_app_state_repository.py`, `backend/src/app/infrastructure/runtime.py`, and other `rewrite_*` transitional scaffolds
- Why they are removable: they encode seeded, stubbed, or transitional behavior that is superseded by current owner docs.
- Impacted dependents: frontend scaffold assumptions, backend seed behavior, and current CLI fallback paths.
- Verification before removal: canonical backend surfaces must exist and integration tests must run against them.

### Historical Planning Files

- Candidate: all prior files previously under `Plans/`
- Why they are removable: they are no longer authority and would reintroduce migration-first framing.
- Impacted dependents: human planning only.
- Verification before removal: this artifact exists and is accepted as the sole planning baseline.

## 5) Implementation Slices

### Shared / Cross-layer Slices

#### X1 Shared identity and envelope adoption

- Goal: adopt canonical session, workspace, capability, visibility, allowed-action, and response/error envelopes as the only cross-layer contract.
- Allowed Files: `frontend/src/lib/**`, `backend/src/app/**`, `cli/src/sc_cli/**`
- Depends on: none
- Non-goals: production identity-provider integration, deployment-specific auth transport
- Required unit tests: DTO and envelope schema tests for success, error, membership, capability, and allowed-action payloads
- Required integration / E2E follow-up: backend `/session` and canonical error snapshot tests; frontend decoder integration tests

#### X2 Shared task runtime and audit model

- Goal: unify task states, actions, result availability, worker summary, and audit payload shape across layers.
- Allowed Files: `backend/src/app/**`, `frontend/src/lib/api/**`, `src/core/sc_core/**`, `cli/src/sc_cli/commands/**`
- Depends on: `X1`
- Non-goals: processor deployment topology, infrastructure scheduling decisions
- Required unit tests: runtime state matrix, action guard matrix, audit payload schema tests
- Required integration / E2E follow-up: queue, task-event, control-action, and audit integration suites

### Frontend Slices

#### F1 Shell and navigation realignment

- Goal: rebuild root routing, header, and sidebar around the SoT shell model.
- Allowed Files: `frontend/src/app/**`, `frontend/src/components/layout/**`, `frontend/src/lib/navigation.ts`
- Depends on: `X1`, `B1`
- Non-goals: page-specific feature internals
- Required unit tests: navigation map, header rendering, sidebar section visibility, active workspace and dataset UI state
- Required integration / E2E follow-up: route smoke tests, workspace switch, active dataset switch, queue trigger visibility

#### F2 Schema catalog and editor adoption

- Goal: split schema catalog from editor and adopt the canonical circuit-netlist model in the editor.
- Allowed Files: `frontend/src/features/circuit-definition-editor/**`, `frontend/src/app/**`
- Depends on: `C1`, `B4`
- Non-goals: schemdraw render execution, simulation execution
- Required unit tests: editor serializer, validator bindings, action availability, publish or clone state handling
- Required integration / E2E follow-up: create, update, publish, clone, and open-in-editor flows

#### F3 Research workflow task surfaces

- Goal: unify schemdraw, simulation, and characterization pages around the canonical task queue and task-detail contracts.
- Allowed Files: `frontend/src/features/circuit-schemdraw/**`, `frontend/src/features/simulation/**`, `frontend/src/features/characterization/**`, `frontend/src/lib/api/tasks.ts`
- Depends on: `X2`, `B3`, `B4`, `B5`
- Non-goals: worker orchestration internals
- Required unit tests: task action gating, state badge rendering, result-availability view-model transforms
- Required integration / E2E follow-up: submit, cancel, retry, inspect result, and cross-page task detail flows

#### F4 Dashboard and raw-data split

- Goal: separate the current combined data-browser implementation into dashboard and raw-data browser pages that match the SoT.
- Allowed Files: `frontend/src/features/data-browser/**`, `frontend/src/app/**`
- Depends on: `X1`, `B2`, `B5`
- Non-goals: workspace administration UI
- Required unit tests: dataset summary transforms, raw-data browser list and detail transforms, pagination and filter state
- Required integration / E2E follow-up: dashboard-to-raw-data navigation, dataset detail, trace detail, and result browsing flows

### Backend Slices

#### B1 Session, workspace, and auth surface

- Goal: implement the canonical session envelope, workspace memberships, active workspace switching, active dataset handling, capabilities, and allowed actions.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/domain/**`, `backend/src/app/infrastructure/**`
- Depends on: `X1`
- Non-goals: external IdP and email-vendor integration details
- Required unit tests: capability derivation, membership selection, allowed-action derivation, auth error mapping
- Required integration / E2E follow-up: `/session`, workspace switch, active-dataset mutation, auth-required and permission-denied cases

#### B2 Datasets and results surface

- Goal: replace flat scaffold dataset payloads with canonical dataset, design, trace, and result contracts.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/domain/**`
- Depends on: `X1`, `C2`
- Non-goals: dashboard page implementation
- Required unit tests: canonical mapper tests for dataset, design, trace, trace batch, and result summaries
- Required integration / E2E follow-up: list, detail, filter, pagination meta, ownership, and permission cases

#### B3 Tasks and execution API

- Goal: implement canonical queue read model, task filters, submit, cancel, terminate, retry, result availability, worker summary, and audit emission.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/domain/**`, `backend/src/app/infrastructure/**`
- Depends on: `X2`, `C1`
- Non-goals: cluster deployment or queue-provider selection
- Required unit tests: lifecycle transitions, action guards, result availability, event mapping
- Required integration / E2E follow-up: list, get, events, submit, cancel, terminate, retry, and queue filter flows

#### B4 Circuit definitions and schemdraw API

- Goal: provide canonical circuit-definition catalog, detail, update, publish, clone, and schemdraw render surfaces.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/infrastructure/**`
- Depends on: `C1`, `X1`
- Non-goals: simulation and characterization execution
- Required unit tests: netlist validation mapping, render request mapping, publish and clone action rules
- Required integration / E2E follow-up: catalog, detail, update, publish, clone, and render endpoint tests

#### B5 Characterization results and audit log surface

- Goal: expose characterization summaries, details, and audit-log query surfaces aligned with workspace and resource ownership.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/domain/**`, `src/core/shared/persistence/**`
- Depends on: `X2`, `C2`
- Non-goals: generic observability platform design
- Required unit tests: characterization summary mapping, audit filter derivation, permission filters
- Required integration / E2E follow-up: characterization result list and detail, audit query, and permission enforcement tests

### Core Slices

#### C1 Canonical circuit and task core contracts

- Goal: replace placeholder circuit inspection and simplified task runtime abstractions with canonical validators, state machine, and processor contracts.
- Allowed Files: `src/core/sc_core/circuit_definitions/**`, `src/core/sc_core/tasking/**`, `src/core/sc_core/execution/**`
- Depends on: none
- Non-goals: frontend or backend DTO shaping
- Required unit tests: netlist validator suite, task state matrix, processor contract tests
- Required integration / E2E follow-up: backend contract suites consuming canonical core contracts

#### C2 Persistence and data-format canonicalization

- Goal: canonicalize dataset, design, trace, trace-batch, result, and audit persistence contracts and remove legacy alias semantics.
- Allowed Files: `src/core/shared/persistence/**`, `src/core/analysis/domain/trace_records.py`
- Depends on: `C1`
- Non-goals: legacy compatibility preservation
- Required unit tests: repository round-trip, ownership naming, trace-batch persistence, audit-store tests
- Required integration / E2E follow-up: backend dataset, result, and audit query integration tests

### CLI Slices

#### L1 Standalone runtime decoupling

- Goal: remove the CLI's primary dependency on backend facade code and make the local runtime canonical.
- Allowed Files: `cli/src/sc_cli/**`, `backend/sc_backend/**`
- Depends on: `C1`, `C2`, `X2`
- Non-goals: app API client expansion beyond interchange needs
- Required unit tests: command contract tests for local session, dataset, task, and run flows
- Required integration / E2E follow-up: local run, list, show, cancel, and inspect flows without backend facade imports

#### L2 Local and app interchange plus canonical output

- Goal: implement import, export, copy-with-lineage, and canonical machine-readable output for CLI surfaces.
- Allowed Files: `cli/src/sc_cli/**`
- Depends on: `L1`, `B2`, `B3`
- Non-goals: cloud sync and remote auth workflows
- Required unit tests: bundle manifest tests, canonical JSON output snapshots, lineage preservation tests
- Required integration / E2E follow-up: local-to-app-to-local round-trip and cross-surface output verification

## 6) Test Backlog

### Integration

- Session and workspace switch with active dataset and capability derivation
- Canonical response and error envelope snapshots
- Dataset, design, trace, trace batch, and result list or detail or filter cases
- Task queue, submit, events, cancel, terminate, retry, and result-availability cases
- Circuit-definition catalog, detail, update, publish, clone, and schemdraw render cases
- Characterization result and audit-log query cases
- CLI standalone runtime and local/app interchange round-trip cases

### E2E

- Shell navigation, workspace selection, active dataset selection, and queue trigger flow
- Dashboard to raw-data browser to task workflow
- Schemas to editor to schemdraw to simulation or characterization journey
- Auth-required and permission-denied UI handling

### Contract Verification

- Backend success and error snapshot contracts
- Frontend decoder contract snapshots
- Core circuit-netlist and analysis-result serialization snapshots
- CLI canonical JSON output snapshots

### Removal Safety Checks

- Assert rewrite surfaces do not import `src/app/**`
- Assert CLI surfaces do not depend on `backend/sc_backend/**`
- Assert no new usage of `owned` visibility or `dataset_id` or `design_id` fallback semantics is introduced
- Require replacement tests before deleting remaining legacy tests

## 7) Verification Matrix

| Slice | Verification |
| --- | --- |
| `X1` | Backend `/session` snapshots, canonical error snapshots, frontend decoder integration |
| `X2` | Core runtime state matrix, backend queue-control integration, audit payload tests |
| `F1` | React shell and nav tests, route and context Playwright smoke |
| `F2` | Editor serializer and validator tests, schema create or update or publish or clone integration |
| `F3` | Task action gating tests, submit or cancel or retry or inspect-result E2E |
| `F4` | Dataset and raw-data view-model tests, dashboard to raw-data E2E |
| `B1` | Capability and membership unit tests, session and workspace integration suite |
| `B2` | Canonical dataset/result mapper tests, list and detail and filter integration suite |
| `B3` | Lifecycle and action-guard tests, queue and control integration suite |
| `B4` | Netlist and render mapping tests, circuit-definition and render integration suite |
| `B5` | Characterization and audit mapper tests, permission-filter integration suite |
| `C1` | Canonical validator suite, task-state matrix, processor contract tests |
| `C2` | Persistence round-trip suite, ownership naming tests, backend query integration |
| `L1` | CLI command unit suite, local runtime integration without backend facade |
| `L2` | Bundle and JSON snapshot tests, local/app interchange round-trip |

### Expected Verification Commands

- `npm run rewrite:check`
- `uv run pytest`
- `cd backend && uv run pytest`
- `npm run test --prefix frontend`
- `npm run test:e2e --prefix frontend`

## 8) Open Decisions

- No blocking SoT gaps were found for planning. Current owner docs are sufficient to dispatch the slices above.
- Human decision is still needed for auth-provider and invite-delivery implementation choice.
- Human decision is still needed for processor deployment topology.
- Those decisions are deployment-level choices and do not block contract adoption or slice dispatch.
