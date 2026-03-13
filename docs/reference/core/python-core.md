---
aliases:
  - Python Core Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/core-reference
status: stable
owner: docs-team
audience: team
scope: Python core 能力、共享 contract 與 orchestration-facing reference surface。
version: v0.3.0
last_updated: 2026-03-13
updated_by: team
---

# Python Core

本頁記錄 Python-owned core surface：`sc_core` 的 canonical contracts，以及 Python adopter 如何在 persistence、worker、CLI、backend 中消費這些 contracts。

!!! info "Owned Surface"
    Python core 的 canonical owner 是 installable `sc_core` package。
    `src/core/shared/`、`src/worker/`、backend adapters、CLI commands 都是 adopter，不是 contract owner。

!!! warning "Do Not Move Ownership"
    HTTP schema、CLI presenter、ORM / repository implementation、Electron runtime concerns 不得寫成 `Python Core` 的 owner 範圍。
    這些屬於 adapter 或 app layer。

## Exported Families

=== "Circuit Definitions"

    | Surface | Focus | Primary exports |
    |---|---|---|
    | `sc_core.circuit_definitions` | canonical source inspection、validation、preview artifact naming | `inspect_circuit_definition_source`, `CircuitDefinitionInspection`, `ValidationNotice`, `ValidationLevel`, `DEFAULT_PREVIEW_ARTIFACTS` |

=== "Tasking"

    | Surface | Focus | Primary exports |
    |---|---|---|
    | `sc_core.tasking` | task submission kind、lane naming、dispatch routing、worker enqueue payload | `TaskSubmissionKind`, `LaneName`, `WorkerDispatchPlan`, `resolve_worker_task_route`, `build_worker_dispatch_plan`, `build_worker_enqueue_kwargs` |

=== "Execution"

    | Surface | Focus | Primary exports |
    |---|---|---|
    | `sc_core.execution` | task creation、lifecycle mutation、execution operation、history / audit payload | `TaskCreationSpec`, `TaskExecutionOperation`, `TaskExecutionTransition`, `TaskLifecycleMutation`, `TaskResultHandle`, lifecycle builder helpers |

=== "Storage"

    | Surface | Focus | Primary exports |
    |---|---|---|
    | `sc_core.storage` | trace / result handles、trace-store locator、payload lifecycle、version markers | `StorageRecordHandle`, `TraceBatchHandle`, `TraceStoreLocator`, `TraceStorePayloadLifecycle`, `TraceStoreVersionMarkers`, `TraceResultLinkage` |

## Python Adopters

| Adopter Surface | Role | Why it is not the owner |
|---|---|---|
| `src/core/shared/persistence/repositories/` | 將 persisted rows 映射到 `TaskCreationSpec`、`TaskExecutionOperation`、`TraceResultLinkage` 等 canonical objects | repository 實作是 adapter；canonical shape 由 `sc_core` 決定 |
| `src/core/shared/persistence/trace_store.py` | 實作 TraceStore backend binding，採用 `TraceStoreLocator` 與 payload lifecycle contract | backend binding 與 runtime config 不等於 storage contract owner |
| `src/worker/dispatch.py` | 消費 `WorkerDispatchPlan` 與 routing helpers | worker 只是 dispatcher consumer |
| `src/worker/runtime.py` | 持久化 `TaskExecutionOperation`，驅動 managed-task lifecycle | worker runtime 不定義 lifecycle contract |
| CLI command groups | 透過 `sc_core` inspection / contract surfaces 對外暴露 CLI | CLI 只做 transport / presentation |

## Consumer Pairing

| Consumer | 主要依賴的 Python core family |
|---|---|
| Backend task / dataset / definition adapters | `circuit_definitions`, `execution`, `storage` |
| Worker dispatch / runtime | `tasking`, `execution`, `storage` |
| CLI | `circuit_definitions`, `tasking`, `execution` |

## Architecture Pair

| Concern | SoT |
|---|---|
| ownership boundary | [Core Blueprint](../architecture/core-blueprint.md) |
| canonical contract ownership | [Canonical Contract Registry](../architecture/canonical-contract-registry.md) |
| task lifecycle semantics | [Task Semantics](../architecture/task-semantics.md) |

## Related

- [Core Reference](index.md)
- [Julia Wrapper](julia-wrapper.md)
