---
aliases:
- CLI Reference
- CLI 指令參考
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/cli
status: stable
owner: docs-team
audience: team
scope: 目前正式支援的 `sc` 命令列介面，說明 CLI 如何調用 core 與 backend-facing capability。
version: v0.4.0
last_updated: 2026-03-13
updated_by: team
---

# CLI Options

本區收錄 `sc` 的正式 command surface，以及 CLI 如何以 shared core 與 backend authority 實踐研究 workflow。

!!! info "How To Read CLI Docs"
    先讀 `Session`、`Datasets`、`Circuit Definition` 取得目前工作上下文，再讀 `Tasks`、`Events`、`Results` 查 persisted state，最後讀 `Simulation`、`Characterization`、`Ops` 了解 workflow-level 操作。

!!! warning "Published Surface Rule"
    只要 command group 已由 `cli/src/sc_cli/app.py` 掛進 root `sc`，本區就必須有對應 reference page。
    `uv run sc --help` 與 CLI reference 不得分岐。

## Command Map

=== "Foundation"

    | Command | 核心聚焦 | Authority Pair |
    |---|---|---|
    | [sc session](sc-session.md) | session、workspace、active dataset context | [Backend / Session & Workspace](../app/backend/session-workspace.md) |
    | [sc datasets](sc-datasets.md) | dataset catalog、dataset detail、metadata mutation | [Backend / Datasets & Results](../app/backend/datasets-results.md) |
    | [sc circuit-definition](sc-circuit-definition.md) | canonical definition inspection、persisted definition CRUD | [Backend / Circuit Definitions](../app/backend/circuit-definitions.md), [Core / Python Core](../core/python-core.md) |

=== "Inspection"

    | Command | 核心聚焦 | Authority Pair |
    |---|---|---|
    | [sc tasks](sc-tasks.md) | generic task list、detail、submit、wait | [Backend / Tasks & Execution](../app/backend/tasks-execution.md), [Architecture / Task Semantics](../architecture/task-semantics.md) |
    | [sc events](sc-events.md) | persisted task event history | [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |
    | [sc results](sc-results.md) | persisted result refs、trace payload、result handles | [Backend / Datasets & Results](../app/backend/datasets-results.md), [Backend / Tasks & Execution](../app/backend/tasks-execution.md) |

=== "Workflow"

    | Command | 核心聚焦 | Authority Pair |
    |---|---|---|
    | [sc simulation](sc-simulation.md) | simulation-lane submit / inspect / wait | [Backend / Tasks & Execution](../app/backend/tasks-execution.md), [Backend / Circuit Definitions](../app/backend/circuit-definitions.md) |
    | [sc characterization](sc-characterization.md) | characterization-lane submit / inspect / wait | [Backend / Tasks & Execution](../app/backend/tasks-execution.md), [Backend / Characterization Results](../app/backend/characterization-results.md) |
    | [sc ops](sc-ops.md) | connected operator bundle across task, event, result surfaces | [Backend / Tasks & Execution](../app/backend/tasks-execution.md), [Backend / Datasets & Results](../app/backend/datasets-results.md) |

=== "Core Boundary"

    | Command | 核心聚焦 | Authority Pair |
    |---|---|---|
    | [sc core](sc-core.md) | inspect the installable `sc_core` boundary | [Core / Python Core](../core/python-core.md) |

## Shared Contracts

| Concern | CLI Rule | SoT |
|---|---|---|
| Machine-readable output | 多數 operational subcommands 支援 `--output text|json`。目前 `sc core preview-artifacts` 仍為 text-only。 | [Canonical Contract Registry](../architecture/canonical-contract-registry.md) |
| Task lifecycle | `task_id` 是 attach / wait / inspect 的 primary key。lane-specific commands 只是在 generic task contract 上加 lane filter。 | [Task Semantics](../architecture/task-semantics.md) |
| Session context | 若命令接受 `--dataset-id`，省略時可回退到目前 active dataset。 | [Backend / Session & Workspace](../app/backend/session-workspace.md) |
| Circuit-definition inspection | 本地 source inspection 由 `sc_core` canonical inspection surface 決定，而不是 CLI 自行解析。 | [Core / Python Core](../core/python-core.md) |

!!! example "Root Command"
    ```bash
    uv run sc --help
    ```
    目前 root command 會公開：
    `core`、`session`、`datasets`、`tasks`、`ops`、`events`、`results`、`characterization`、`simulation`、`circuit-definition`

## Related

- [Core Reference](../core/index.md) - 核心能力與 Python/Julia 邊界
- [Backend Reference](../app/backend/index.md) - backend-facing reference surface
- [How-to Guides](../../how-to/index.md) - 操作指南
