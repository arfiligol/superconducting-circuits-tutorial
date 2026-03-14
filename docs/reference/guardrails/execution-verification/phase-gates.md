---
aliases:
  - "Phase Gates"
  - "階段驗收關卡"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: team
scope: "定義 migration phases 最低驗收條件、對應測試類型與深度並行前置條件"
version: v1.2.0
last_updated: 2026-03-14
updated_by: codex
---

# Phase Gates

本文件定義 migration 各 phase 最低驗收門檻。

## Required Planning Artifacts

在深入 `Phase 4` 以前，必須已有：

- parity matrix
- canonical contract registry
- source-of-truth ordering
- identity/workspace minimal model
- task runtime / processor contract
- error model
- planning artifact format

## Minimum Gates by Phase

| Phase | 最低必過項目 |
| --- | --- |
| Phase 3 | backend API contract tests、frontend build/type/test、schema/dataset parity entries 更新 |
| Phase 4 | auth/session contract tests、workspace-context tests、frontend app-state integration tests |
| Phase 4.5 | CLI command tests for session/dataset/definition/task basics |
| Phase 5A | repository/persistence tests、TraceStore contract tests、provenance linkage tests |
| Phase 5B | task lifecycle tests、worker/execution tests、retry/failure classification tests |
| Phase 6 | workflow integration tests、recovery/reattach tests、parity matrix workflow sign-off |
| Phase 7 | full CLI parity checks、desktop smoke tests、migration sign-off against parity matrix |

## Phase-to-Test Mapping

| 範圍 | 最低測試類型 |
| --- | --- |
| `sc_core` | invariant / contract tests、pure helper tests |
| backend | API contract tests、service tests、repository/persistence tests |
| frontend | build/type/lint、shared hook/provider tests、必要時 integration tests |
| CLI | command behavior tests、machine-readable output tests |
| worker / execution | task lifecycle tests、retry/failure tests、recovery attach tests |
| docs | nav source check、site build、built route check |

## Entry Criteria for Deep Implementation

在 Implementation Agents 與 Test Agents 可以大規模並行開工前，至少要有：

- [Source of Truth Order](../project-basics/source-of-truth-order.md)
- [Contract Versioning](../code-quality/contract-versioning.md)
- [Error Handling](../code-quality/error-handling.md)
- [Identity & Workspace Model](../../app/shared/identity-workspace-model.md)
- [App / Backend / Tasks & Execution](../../app/backend/tasks-execution.md)
- [Parity Matrix](../../architecture/parity-matrix.md)
- [Canonical Contract Registry](../../architecture/canonical-contract-registry.md)
- [Multiple Agent Collaboration](./multi-agent-collaboration.md)
- [Agent Handoff Formats](./contributor-reporting.md)

## Agent Rule { #agent-rule }

```markdown
## Phase Gates
- Do not declare a migration phase complete until its minimum contract/test gates are green.
- Before deep Phase 4 work, require:
    - parity matrix
    - canonical contract registry
    - source-of-truth ordering
    - identity/workspace minimal model
    - task runtime / processor contract
    - error model
    - planning artifact format
- If a public contract changes during any phase, update the parity matrix, contract registry, and relevant tests in the same delivery line.
- Treat recovery/reattach tests as mandatory for workflow-parity phases, not optional polish.
```
