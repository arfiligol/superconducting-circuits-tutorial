---
aliases:
  - Backend Tasks Execution Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Backend task、execution runtime、event history 與 result attachment reference surface。
version: v0.5.0
last_updated: 2026-03-13
updated_by: team
---

# Tasks & Execution

本頁定義 simulation / characterization workflow 依賴的 generic task surface。

!!! info "Surface Boundary"
    本頁負責 task submission、status、event history、result attachment 與 recovery attach。
    analysis-specific result artifact 不屬於本頁責任。

!!! tip "Primary Consumers"
    主要消費者是 [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md) 與 [Characterization](../frontend/research-workflow/characterization.md)。

---

## 涵蓋範圍 (Coverage)

| Surface | 說明 |
| :--- | :--- |
| **Task Submission & Status** | 任務提交與狀態追蹤 |
| **Execution Runtime Metadata** | 執行環境元資料 |
| **Persisted Event History** | 持久化事件歷史 |
| **Result Attachment** | 結果附件與復原掛載 |

---

## Surface Contracts

=== "Submission"

    task submit response 至少必須提供：

    | 欄位 | 說明 |
    | :--- | :--- |
    | `task_id` | 任務唯一識別 |
    | `task_kind` | 任務種類 |
    | `status` | 初始狀態 |
    | `identity` | lane / owner / workspace-bound identity |

=== "Event History"

    backend 必須提供以下資訊以確保執行過程透明：

    * **Task Detail**: 任務詳細規格
    * **Task Events**: 執行過程中的離散事件
    * **Execution Metadata**: append-oriented 的執行元資料

=== "Result Attachment"

    task detail 至少必須能表示：

    | 屬性 | 說明 |
    | :--- | :--- |
    | **Terminal Status** | 終止狀態識別 |
    | **Result Ref** | 結果引用標記 (`result_ref`) |
    | **Persistence State** | 是否有 persisted result / artifact 可供後續頁面讀取 |

!!! warning "Task is the Execution Authority"
    simulation 與 characterization workflow 的執行狀態必須以 **persisted task state** 為準。
    frontend refresh 後不得退回 page-local memory state。

!!! tip "Recovery-first Event Model"
    event history 需要能在 refresh / reconnect 後重新讀回，不可依賴單次 live session 或頁面局部狀態。

---

## Delivery Rules

| 項目 | 規則 |
| :--- | :--- |
| **Refresh Recovery** | frontend refresh 後必須能以 persisted task detail 重建目前執行狀態。 |
| **Attach Latest Support** | surface 必須允許 workflow 重新附著到既有任務，而不是強迫重新送出。 |
| **Terminal Result Handoff** | 進入 terminal state 後，result ref 與 persisted artifact state 必須可供後續頁面讀取。 |
| **No Page-local Authority** | page-local memory 可做暫時顯示，但不得凌駕 persisted task state。 |

---

## Related

- [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md)
- [Characterization](../frontend/research-workflow/characterization.md)
- [Task Semantics](../../architecture/task-semantics.md)
- [Canonical Contract Registry](../../architecture/canonical-contract-registry.md)
