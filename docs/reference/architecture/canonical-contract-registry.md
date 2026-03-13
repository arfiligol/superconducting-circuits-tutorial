---
aliases:
  - "Canonical Contract Registry"
  - "正典契約註冊表"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
status: draft
owner: docs-team
audience: team
scope: "列出 migration 期間每個 canonical contract 的 owner、SoT、adapter 與測試責任"
version: v0.3.0
last_updated: 2026-03-13
updated_by: team
---

# Canonical Contract Registry

本文件定義 migration 期間哪些 contract 是 canonical surface，以及它們由誰維護。
若某個 Contributor Agent 不確定規則歸屬，先查這份註冊表。

## Registry

| Contract | Owner | Source of Truth | Primary Code Surface | Adapters Using It | Compatibility Rule | Minimum Tests |
| --- | --- | --- | --- | --- | --- | --- |
| Circuit Definition / Netlist | `sc_core` | `docs/reference/data-formats/circuit-netlist.md` | `src/core/sc_core/circuit_definitions/` | backend, frontend, CLI, worker | additive-first; persisted definitions need fallback | validator / normalization / API contract tests |
| Dataset Metadata Contract | backend + `sc_core` | `docs/reference/data-formats/dataset-record.md` | backend persistence + future `sc_core.datasets` | backend, frontend, CLI | persisted rows require read-compat or migration | repository / API / CLI inspect tests |
| Trace / Result / Provenance Contract | backend + `sc_core` | `docs/reference/data-formats/dataset-record.md`, `docs/reference/data-formats/analysis-result.md` | backend tracestore + future `sc_core.traces` | backend, frontend, CLI, worker | versioned persisted contract | persistence / provenance linkage tests |
| Task Submission / Status / Result | backend + `sc_core` | `docs/reference/architecture/task-semantics.md` | `src/core/sc_core/tasking/`, backend task APIs | backend, frontend, CLI, worker | task ids immutable; retry creates new task | task lifecycle / attach / retry tests |
| Session / Workspace Context | backend | `docs/reference/architecture/identity-workspace-model.md` | backend session APIs | frontend, CLI, worker visibility filters | lockstep migration branch; semantics must stay stable | auth/session / active dataset tests |
| Schemdraw Render Contract | backend + frontend | `docs/reference/app/backend/schemdraw-render.md`, `docs/reference/app/frontend/research-workflow/schemdraw.md` | backend render API + frontend schemdraw workspace | frontend | additive-first; diagnostics codes stable once published | contract / render / diagnostics tests |
| CLI Machine-readable Output | CLI + `sc_core` | `docs/reference/cli/index.md` and command docs | `cli/src/sc_cli/` presenters | CLI, automation, future scripting | changes must be documented as contract changes | CLI behavior / output tests |
| UI Workflow Contract | frontend + backend | `docs/reference/app/frontend/**/*.md` | frontend features + backend APIs | frontend only | route/workflow changes update parity matrix | integration / recovery tests |

## Rules

- 若 contract 有多個 owner，必須明確區分 canonical owner 與 adapter owner
- 若 primary code surface 與 Source of Truth 衝突，以 Source of Truth 為準
- 任何 breaking 變更都必須同步更新本表
- 若 contract 尚未有穩定 primary code surface，必須在 `Notes` 或相關 issue 中補上遷移計畫
