---
aliases:
  - "Canonical Contract Registry"
  - "正典契約註冊表"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
status: stable
owner: docs-team
audience: team
scope: 系統目前 published canonical contracts 的 owner、SoT 與主要消費者
version: v0.7.0
last_updated: 2026-03-14
updated_by: team
---

# Canonical Contract Registry

本文件列出目前整個平台的 published canonical contracts，以及每一組 contract 的 owner、SoT 與主要消費者。

!!! info "Read With App / CLI / Core"
    如果你已經知道自己在看哪一個 page、shared app model、CLI surface 或 core runtime，請直接回到對應的 App、CLI 或 Core reference。
    本頁的用途是先判定 contract 到底歸誰管。

!!! warning "Registry Rule"
    若一個 public workflow、machine-readable payload 或 shared runtime behavior 已被其他層使用，就必須在本表有對應 row。
    找不到 row，代表 architecture-level ownership 尚未寫清楚。

## Registry

| Contract | Canonical owner | Source of truth | Primary consumers | Compatibility rule |
|---|---|---|---|---|
| Circuit Definition / Netlist | `sc_core` | [Data Formats / Circuit Netlist](../data-formats/circuit-netlist.md) | backend, CLI, definition workflows, simulation workflows | additive-first；persisted definitions 需維持 read compatibility |
| App Session / Workspace Context | app/shared + backend | [App / Shared / Identity & Workspace Model](../app/shared/identity-workspace-model.md), [App / Backend / Session & Workspace](../app/backend/session-workspace.md) | frontend shell, workspace pages | active dataset / workspace semantics 必須跨頁一致 |
| App Resource Ownership / Visibility | app/shared + backend | [App / Shared / Resource Ownership & Visibility](../app/shared/resource-ownership-and-visibility.md), [App / Backend / Session & Workspace](../app/backend/session-workspace.md) | datasets, definitions, tasks, results, audit logging | 每筆 resource 只屬於一個 workspace |
| App Authentication / Authorization Context | app/shared + backend | [App / Shared / Authentication & Authorization](../app/shared/authentication-and-authorization.md) | Header user menu, task queue controls, backend session surface, admin surfaces | role / capability flags 一旦 published 必須保持可解讀 |
| Dataset Metadata / Dataset Profile | backend + `sc_core` | [Data Formats / Design / Trace Schema](../data-formats/dataset-record.md), [App / Backend / Datasets & Results](../app/backend/datasets-results.md) | dashboard, raw data browser, characterization, CLI datasets | mutation 與 read model 必須維持相容 |
| Trace / Result / Provenance | backend + `sc_core` | [Data Formats / Design / Trace Schema](../data-formats/dataset-record.md), [Data Formats / Analysis Result](../data-formats/analysis-result.md) | raw data browser, characterization, worker, CLI results | persisted result / provenance contract 必須 version-aware |
| App Task Submission / Status / Result | app/backend + app/shared + `sc_core` | [App / Backend / Tasks & Execution](../app/backend/tasks-execution.md), [App / Shared / Task Runtime & Processors](../app/shared/task-runtime-and-processors.md) | simulation, characterization, worker | `task_id` immutable；retry 預設新 task |
| App Processor Runtime Status | app/shared + backend adapter | [App / Shared / Task Runtime & Processors](../app/shared/task-runtime-and-processors.md) | Header worker summary, queue controls, runtime operators | health summary 需由 runtime heartbeat 派生 |
| UI Shell Context | frontend + backend | [App / Frontend / Header](../app/frontend/shared-shell/header.md), [App / Frontend / Sidebar](../app/frontend/shared-shell/sidebar.md), [App / Backend / Session & Workspace](../app/backend/session-workspace.md) | all frontend pages | shell 顯示的 dataset / task / user context 不得分叉 |
| UI Task Management Workflow | frontend + backend | [App / Frontend / Task Management](../app/frontend/shared-workflow/task-management.md), [App / Backend / Tasks & Execution](../app/backend/tasks-execution.md) | simulation, characterization | queue / attach / control / recovery 必須依 persisted task state |
| Schemdraw Render Contract | backend + frontend | [App / Backend / Schemdraw Render](../app/backend/schemdraw-render.md), [App / Frontend / Schemdraw](../app/frontend/research-workflow/schemdraw.md) | schemdraw page | diagnostics code 一旦 published 應保持穩定 |
| App Audit Log Contract | app/shared + backend adapters | [App / Shared / Audit Logging](../app/shared/audit-logging.md) | admins, task governance, runtime control review | append-only；不得與 app DB 綁在同一個 operational store |
| CLI Local Runtime Context | CLI + `sc_core` | [CLI / Standalone Runtime](../cli/standalone-runtime.md), [CLI Options](../cli/index.md) | CLI, automation | CLI 不依賴 shared workspace / auth / queue semantics |
| CLI Machine-readable Output | CLI + `sc_core` | [CLI Options](../cli/index.md) | CLI, automation | machine-readable changes 必須視為 contract change |

## Related

* [Parity Matrix](parity-matrix.md)
* [App / Shared](../app/shared/index.md)
* [App / Frontend](../app/frontend/index.md)
* [App / Backend](../app/backend/index.md)
* [CLI Options](../cli/index.md)
