---
aliases:
  - "Parity Matrix"
  - "遷移對等矩陣"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
status: draft
owner: docs-team
audience: team
scope: "追蹤目前 required capability 與新架構對等進度的單一矩陣"
version: v0.2.0
last_updated: 2026-03-13
updated_by: team
---

# Parity Matrix

本文件是 migration 驗收的追蹤矩陣。
唯一成功條件是：**目前被列為 required 的 capability，重構後都能做到。**

## Status Legend

| Status | 定義 |
| --- | --- |
| `done` | 新架構已可完成該能力，且主要驗收已過 |
| `in_progress` | 已有新實作，但尚未達到完整 parity |
| `planned` | 已納入 phase，但尚未開始 |
| `blocked` | 缺 canonical contract、storage、execution 或 auth 先決條件 |

## Matrix

| Required Capability | Reference Source | New Owner | Phase | Status | Recovery Parity | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Dataset list / detail / metadata update | `docs/reference/app/frontend/workspace/raw-data-browser.md`, `docs/reference/app/frontend/workspace/dashboard.md` | backend + frontend | Phase 3 | `in_progress` | `no` | rewrite `Data Browser` 已接真 API，但 app-wide active dataset 尚未完整接線 |
| Circuit definition list / create / update / delete | `docs/reference/app/frontend/definition/schemas.md`, `docs/reference/app/frontend/definition/schema-editor.md`, `docs/reference/data-formats/circuit-netlist.md` | `sc_core` + backend + frontend + CLI | Phase 3 | `in_progress` | `partial` | editor 已接 API，CLI 仍只到 inspect proof |
| Validate / normalize circuit definition | `docs/reference/data-formats/circuit-netlist.md` | `sc_core` + backend + CLI | Phase 4.5 / 6 | `in_progress` | `n/a` | `sc_core` 已有 inspection path，但 full parity 未完成 |
| Schemdraw readiness / preview | `docs/reference/app/frontend/research-workflow/schemdraw.md`, `docs/reference/app/backend/schemdraw-render.md`, `docs/reference/app/frontend/definition/schema-editor.md` | frontend + backend + `sc_core` | Phase 3 / 6 | `in_progress` | `no` | frontend page spec 與 backend render contract 已定義；正式 render runtime 仍待完整落地 |
| Active dataset context | `docs/reference/app/frontend/workspace/dashboard.md`, `docs/reference/architecture/identity-workspace-model.md` | backend + frontend + CLI | Phase 4 | `planned` | `no` | session/task visibility 尚未 fully persistent |
| Multi-user authentication / session | session/auth spec baseline + Phase 4 specs | backend + frontend + CLI | Phase 4 | `planned` | `n/a` | 目前只有 development stub |
| Task list / status / detail | `docs/reference/architecture/task-semantics.md` | backend + frontend + CLI + worker | Phase 5B | `in_progress` | `partial` | API scaffold 已有，尚未接真 execution |
| Simulation submit / status / logs / result | `docs/reference/app/frontend/research-workflow/circuit-simulation.md`, CLI reference | `sc_core` + backend + worker + frontend + CLI | Phase 5B / 6 / 7 | `planned` | `no` | execution foundation 尚未完成 |
| Characterization workflow | `docs/reference/app/frontend/research-workflow/characterization.md`, CLI reference | `sc_core` + backend + frontend + CLI | Phase 6 / 7 | `planned` | `no` | analysis/result linkage 未完整重建 |
| TraceStore CRUD / provenance linkage | `docs/reference/data-formats/dataset-record.md`, `docs/reference/data-formats/analysis-result.md` | backend + `sc_core` + CLI | Phase 5A | `planned` | `n/a` | SQLite + TraceStore 正式落地尚未完成 |
| CLI operational baseline | `docs/reference/cli/index.md` | CLI + `sc_core` + backend | Phase 4.5 | `in_progress` | `n/a` | `sc` scaffold 已有，但 commands coverage 很窄 |
| Desktop local wrapper | project overview + desktop direction | desktop + frontend + backend | Phase 7 | `planned` | `n/a` | Electron shell scaffold 已有，尚未完成 parity |

## Usage Rules

- 每當 public contract 或 workflow 變更時，必須同步更新本矩陣
- 若某能力依賴 recovery parity，`done` 前必須把 `Recovery Parity` 欄位升到 `yes`
- 若存在例外相容處理，必須在 `Notes` 說明原因與 owner
