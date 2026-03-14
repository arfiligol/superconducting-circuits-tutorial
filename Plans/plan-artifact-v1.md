# Plan Artifact v1

This file is the sole planning baseline for the rewrite as of 2026-03-15.
All prior files under `Plans/` are superseded and removed.
This artifact uses the current Source of Truth only. Historical plans, migration assumptions, and branch intent are not authority.

## 0) Task Information

- Agent: `Planning & Reviewing Agent`
- Task ID / Topic: `L3M-SoT-Rebaseline`
- Status: `Active / Rolling baseline`

## 1) Goal

- Rebaseline planning against the current SoT and current code only.
- Preserve planning continuity after context compaction by recording delivered slices, still-open gaps, and current dispatch rules in one artifact.
- Define assignable implementation and test slices without writing migration strategy.
- Keep the planning baseline compatible with the reduced 4-agent workflow.

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

## 3) Execution Model Update

### Active Agent Families

- `Document Agent`: owns `docs/reference/**` and SoT changes only.
- `Planning & Reviewing Agent`: owns `Plans/**`, dispatch, report intake, code review, integration, and mainline recovery.
- `Implementation Agent`: owns code + unit tests across frontend, backend, core, and CLI.
- `Test Agent`: owns integration, E2E, and cross-surface verification.

### Dispatch Rule

- Frontend / Backend / Core / CLI slices below remain code-area planning buckets, not separate agent identities.
- New prompts issued after this update should be only:
  - `Implementation Agent Prompt`
  - `Test Agent Prompt`
- A single implementation prompt may cover multiple stable slices as long as `Allowed Files`, `Non-Goals`, and verification stay explicit.
- Test prompts remain SoT-first: expected behavior comes from docs and this plan; code is used only to discover harnesses, entrypoints, fixtures, and selectors.

### Sequencing Rule

- No new prompt should be issued for a workstream until the previous delivery report for that workstream has been reviewed by the Planning & Reviewing Agent.
- Definition-authoring is now in the review-and-integration phase, while CLI fixup was the last active implementation lane and is now delivered.

## 4) Current Implementation State

### Aligned Enough To Build From

- The rewrite codebase is already separated into `frontend/`, `backend/`, `cli/`, and `src/core/`.
- Rewrite surfaces for session, datasets, tasks, circuit definitions, and research workflows already exist and can be replaced in place.

### Received Delivery Inputs

These inputs are now part of planning state and must not be lost after context compaction:

- `5eea822` `feat(core): add canonical circuit netlist inspection`
  - delivered `C1` core circuit inspection baseline
- `25950c8` `feat(backend): add circuit definition authoring slice`
  - delivered backend definition catalog, detail, mutation, and schemdraw request/response surface
- `ba1de0f` `feat(frontend): finalize circuit-definition-authoring slice (L1-FE-Finalize-Definition-Authoring-Delivery)`
  - delivered schema catalog/editor + schemdraw frontend definition-authoring slice
- `423f529` `test: finalize definition-authoring integration and E2E evidence`
  - delivered backend integration + rewrite E2E evidence for definition-authoring
- `e400bfc` `fix: decouple standalone circuit definition contract`
  - delivered CLI local contract fixup for `sc circuit-definition`
- `08992b7` `feat(core): canonicalize design-scoped persistence naming`
  - delivered the first `C2` persistence canonicalization slice
- `8eae48c` `feat(frontend): realign shared shell navigation`
  - delivered `F1` shared shell / navigation realignment
- `4661d65` `feat(backend): adopt canonical session workspace surface`
  - delivered `B1` canonical session / workspace surface

### Delivered But Still Requiring Integration Review

- Definition-authoring workstream now has deliverables in Core, Backend, Frontend, and Test; these need unified review/integration before opening the next definition-authoring milestone.
- CLI standalone contract drift fix is delivered; broader standalone runtime and interchange work are still open.
- Shell/session work now has both backend and frontend deliveries, but still lacks full cross-surface integration review and test follow-up.

### Not Yet Aligned To SoT

- `backend/src/app/api/errors.py` and `frontend/src/lib/api/client.ts` still use non-canonical response parsing outside the newly delivered session surface; broader envelope adoption remains open under `X1`.
- `frontend/src/features/data-browser/components/data-browser-workspace.tsx` still conflates dashboard and raw-data browser responsibilities.
- `backend/src/app/api/routers/tasks.py`, `backend/src/app/services/task_service.py`, and `backend/src/app/infrastructure/runtime.py` do not yet implement the canonical task lifecycle, control actions, or result-availability model required for simulation and characterization.
- `backend/src/app/api/routers/` does not yet expose separate characterization-result and audit-log surfaces.
- `cli/src/sc_cli/runtime.py` and `backend/sc_backend/rewrite_cli.py` still route broader standalone flows through backend-facade code; the contract fixup does not complete `L1` or `L2`.
- `src/core/shared/persistence/repositories/contracts.py` and downstream adapters still carry legacy dataset/design dual naming beyond the `C2` slice already delivered.

### Clear Conflict Points

- The shared response/error contract is defined in SoT but cross-surface adoption is still incomplete outside the delivered session and definition surfaces.
- The CLI SoT requires standalone-first runtime, while the current CLI still uses backend-facade code for broader standalone paths; the misalignment is over scope, not over the existence of `backend/sc_backend/` itself.
- The data-format SoT defines `design_id` as canonical dataset-local design scope; delivered `C2` work started that correction, but adapters still mix canonical `design_id` with legacy alias and wrapper semantics.
- Schemdraw is defined as request/response editor assist, not shared task queue. Delivered definition-authoring slices adopt this, but later prompts must not regress this boundary.

## 5) Removal Candidates

### Legacy App Surface

- Candidate: `src/app/**`
- Why it is removable: workspace folder-structure guardrails already mark it as legacy or migration-only, and current owner docs define the rewrite surfaces elsewhere.
- Impacted dependents: `tests/app/**`, old `/api/v1/*` expectations, and any remaining direct imports into legacy services.
- Verification before removal: replacement rewrite integration and E2E coverage must exist, and rewrite modules must have no `src/app` imports.

### Backend Facade Scope Reduction

- Candidate: narrow `backend/sc_backend/**` to CLI-safe backend bridge or interchange-only surfaces instead of using it as the primary runtime path for standalone CLI commands.
- Why it is not directly removable: current folder-structure and CLI SoT still define `backend/sc_backend/` as the formal location for a CLI-safe backend facade, especially around local/app interchange and controlled bridge surfaces.
- Impacted dependents: any current or future import/export/copy-with-lineage bridge flow, plus existing CLI code that still resolves primary commands through the facade.
- Verification before future shrink or removal review: standalone session, dataset, task, simulation, and characterization flows must run from local runtime without facade dependency; interchange coverage must prove the remaining facade surface is bridge-only; only then can further shrink or removal be re-evaluated.

### Legacy Core Persistence Aliases

- Candidate: legacy alias models and repository contracts in `src/core/shared/persistence/models.py`, `src/core/shared/persistence/repositories/contracts.py`, and mixed fallback logic in `src/core/analysis/domain/trace_records.py`
- Why they are removable: current SoT already defines canonical dataset and dataset-local design semantics; the removable part is the dual naming, aliasing, and fallback behavior, not `design_id` itself.
- Impacted dependents: legacy tests, backend scaffold mappers, and any old service logic still using alias types or treating dataset and design scope as interchangeable.
- Verification before removal: canonical persistence round-trip tests and backend dataset, design-scope, or result contract tests must pass.

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

## 6) Implementation Slices

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
- Delivery status: received in `8eae48c`, pending unified review/integration

#### F2 Schema catalog and editor adoption

- Goal: split schema catalog from editor and adopt the canonical circuit-netlist model in the editor.
- Allowed Files: `frontend/src/features/circuit-definition-editor/**`, `frontend/src/app/**`
- Depends on: `C1`, `B4`
- Non-goals: schemdraw render execution, simulation execution
- Required unit tests: editor serializer, validator bindings, action availability, publish or clone state handling
- Required integration / E2E follow-up: create, update, publish, clone, and open-in-editor flows
- Delivery status: received as part of `ba1de0f`, pending unified review/integration

#### F3 Schemdraw editor-assist surface

- Goal: implement Schemdraw as a request/response editor-assist surface with source editing, relation config, backend validation and render, diagnostics, and SVG preview.
- Allowed Files: `frontend/src/features/circuit-schemdraw/**`, `frontend/src/lib/api/**`, `frontend/src/app/**`
- Depends on: `X1`, `B4`
- Non-goals: shared task lifecycle, persisted run history, simulation or characterization queue flows
- Required unit tests: source and relation editor state, stale-preview handling, latest-only apply, diagnostics rendering
- Required integration / E2E follow-up: backend validation and render round-trips, linked-schema visibility handling, stale-response discard, manual render and debounced render flows
- Delivery status: received as part of `ba1de0f`, pending unified review/integration

#### F4 Research workflow task surfaces

- Goal: unify simulation and characterization pages around the canonical task queue and task-detail contracts.
- Allowed Files: `frontend/src/features/simulation/**`, `frontend/src/features/characterization/**`, `frontend/src/lib/api/tasks.ts`
- Depends on: `X2`, `B3`, `B5`
- Non-goals: Schemdraw preview workflow or backend render assist behavior
- Required unit tests: task action gating, state badge rendering, result-availability view-model transforms
- Required integration / E2E follow-up: submit, cancel, retry, inspect result, and cross-page task detail flows for simulation and characterization

#### F5 Dashboard and raw-data split

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
- Delivery status: received in `4661d65`, pending unified review/integration with frontend shell

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

- Goal: provide canonical circuit-definition catalog, detail, update, publish, clone, and request/response schemdraw render surfaces with diagnostics and SVG preview.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/infrastructure/**`
- Depends on: `C1`, `X1`
- Non-goals: shared task queue semantics, simulation execution, characterization execution
- Required unit tests: netlist validation mapping, render request mapping, diagnostics mapping, publish and clone action rules
- Required integration / E2E follow-up: catalog, detail, update, publish, clone, render endpoint, and linked-schema visibility tests
- Delivery status: received in `25950c8`, pending unified review/integration

#### B5 Characterization results surface

- Goal: expose characterization analysis registry, run history, artifact manifest and payload, and tagging mutation surfaces aligned with canonical persisted result contracts.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/domain/**`, `src/core/shared/persistence/**`
- Depends on: `B3`, `C2`
- Non-goals: task lifecycle control, audit-log governance queries
- Required unit tests: registry summary mapping, run-history mapping, artifact-payload mapping, tagging propagation rules
- Required integration / E2E follow-up: run-history queries, artifact payload queries, tagging mutation, and dashboard summary refresh checks

#### B6 Audit log surface

- Goal: expose governance-oriented audit list, audit detail, and export-summary read surfaces aligned with shared audit logging and permission boundaries.
- Allowed Files: `backend/src/app/api/routers/**`, `backend/src/app/services/**`, `backend/src/app/domain/**`, `src/core/shared/persistence/**`
- Depends on: `X1`, `X2`, `C2`
- Non-goals: characterization result views, page analytics, task-event timeline UI
- Required unit tests: audit list mapper, detail mapper, export-summary mapper, permission-filter derivation
- Required integration / E2E follow-up: audit list, detail, export summary, cursor meta, and permission enforcement tests

### Core Slices

#### C1 Canonical circuit and task core contracts

- Goal: replace placeholder circuit inspection and simplified task runtime abstractions with canonical validators, state machine, and processor contracts.
- Allowed Files: `src/core/sc_core/circuit_definitions/**`, `src/core/sc_core/tasking/**`, `src/core/sc_core/execution/**`
- Depends on: none
- Non-goals: frontend or backend DTO shaping
- Required unit tests: netlist validator suite, task state matrix, processor contract tests
- Required integration / E2E follow-up: backend contract suites consuming canonical core contracts
- Delivery status: received in `5eea822`

#### C2 Persistence and data-format canonicalization

- Goal: canonicalize dataset, design, trace, trace-batch, result, and audit persistence contracts and remove legacy alias semantics while preserving canonical `design_id` dataset-local scope.
- Allowed Files: `src/core/shared/persistence/**`, `src/core/analysis/domain/trace_records.py`
- Depends on: `C1`
- Non-goals: legacy compatibility preservation
- Required unit tests: repository round-trip, ownership naming, trace-batch persistence, audit-store tests
- Required integration / E2E follow-up: backend dataset, result, audit, and design-scope query integration tests
- Delivery status: first slice received in `08992b7`; downstream adapter adoption still open

### CLI Slices

#### L1 Standalone runtime decoupling

- Goal: remove the CLI's primary dependency on backend-facade code for standalone session, dataset, task, simulation, and characterization flows.
- Allowed Files: `cli/src/sc_cli/**`
- Depends on: `C1`, `C2`, `X2`
- Non-goals: deleting `backend/sc_backend/**` or redefining app bridge responsibilities
- Required unit tests: command contract tests for local session, dataset, task, and run flows
- Required integration / E2E follow-up: local run, list, show, cancel, and inspect flows without backend-facade usage in standalone paths
- Delivery status: contract fixup received in `e400bfc`; broader standalone runtime decoupling remains open

#### L2 Local and app interchange plus canonical output

- Goal: implement import, export, copy-with-lineage, and canonical machine-readable output while restricting `backend/sc_backend/**` to CLI-safe backend bridge or interchange-only surfaces.
- Allowed Files: `cli/src/sc_cli/**`, `backend/sc_backend/**`
- Depends on: `L1`, `B2`, `B3`
- Non-goals: cloud sync, remote auth workflows, or outright facade removal
- Required unit tests: bundle manifest tests, canonical JSON output snapshots, lineage preservation tests
- Required integration / E2E follow-up: local-to-app-to-local round-trip and bridge-surface verification

## 7) Test Backlog

### Integration

- Session and workspace switch with active dataset and capability derivation
- Canonical response and error envelope snapshots
- Dataset, design, trace, trace batch, and result list or detail or filter cases
- Schemdraw render request, diagnostics, SVG preview, linked-schema visibility, and latest-only response handling
- Task queue, submit, events, cancel, terminate, retry, and result-availability cases for simulation and characterization
- Circuit-definition catalog, detail, update, publish, and clone cases
- Characterization run-history, artifact-payload, and tagging-propagation cases
- Audit-log list, detail, export-summary, and permission cases
- CLI standalone runtime and local/app interchange round-trip cases

### E2E

- Shell navigation, workspace selection, active dataset selection, and queue trigger flow
- Dashboard to raw-data browser to task workflow
- Schemas to editor to Schemdraw preview journey
- Simulation and characterization task submission, result inspection, and retry or cancel journey
- Auth-required and permission-denied UI handling

### Contract Verification

- Backend success and error snapshot contracts
- Frontend decoder contract snapshots
- Core circuit-netlist and analysis-result serialization snapshots
- CLI canonical JSON output snapshots

### Removal Safety Checks

- Assert rewrite surfaces do not import `src/app/**`
- Assert standalone CLI surfaces do not use `backend/sc_backend/**` for primary runtime flows
- Assert no new usage of dual naming or fallback semantics erases the canonical `dataset_id + design_id` pairing
- Require replacement tests before deleting remaining legacy tests

## 8) Verification Matrix

| Slice | Verification |
| --- | --- |
| `X1` | Backend `/session` snapshots, canonical error snapshots, frontend decoder integration |
| `X2` | Core runtime state matrix, backend queue-control integration, audit payload tests |
| `F1` | React shell and nav tests, route and context Playwright smoke |
| `F2` | Editor serializer and validator tests, schema create or update or publish or clone integration |
| `F3` | Schemdraw editor state tests, diagnostics rendering, backend validation or render round-trips |
| `F4` | Task action gating tests, submit or cancel or retry or inspect-result E2E |
| `F5` | Dataset and raw-data view-model tests, dashboard to raw-data E2E |
| `B1` | Capability and membership unit tests, session and workspace integration suite |
| `B2` | Canonical dataset/result mapper tests, list and detail and filter integration suite |
| `B3` | Lifecycle and action-guard tests, queue and control integration suite |
| `B4` | Netlist and render mapping tests, circuit-definition and render integration suite |
| `B5` | Characterization registry/history/artifact tests, tagging integration suite |
| `B6` | Audit list/detail/export tests, permission-filter integration suite |
| `C1` | Canonical validator suite, task-state matrix, processor contract tests |
| `C2` | Persistence round-trip suite, ownership naming tests, backend query integration |
| `L1` | CLI command unit suite, local runtime integration without backend-facade usage in standalone paths |
| `L2` | Bundle and JSON snapshot tests, local/app interchange round-trip |

### Expected Verification Commands

- `npm run rewrite:check`
- `uv run pytest`
- `cd backend && uv run pytest`
- `npm run test --prefix frontend`
- `npm run test:e2e --prefix frontend`

## 9) Open Decisions / Current Dispatch Gate

- No blocking SoT gaps were found for planning. Current owner docs are sufficient to keep dispatching implementation and test work.
- Human decision is still needed for auth-provider and invite-delivery implementation choice.
- Human decision is still needed for processor deployment topology.
- Those decisions are deployment-level choices and do not block contract adoption or slice dispatch.
- Current dispatch policy after this update:
  - only `Implementation Agent Prompt`
  - only `Test Agent Prompt`
- The next prompt should be composite, not lane-split by Frontend / Backend / Core / CLI agent identities.
