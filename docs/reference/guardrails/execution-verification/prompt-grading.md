---
aliases:
  - "Prompt Grading"
  - "Prompt 分級"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: team
scope: "定義 Integrator Agent 在多 Agent 協作時使用的 Prompt 分級、適用時機與驗收要求"
version: v1.0.0
last_updated: 2026-03-13
updated_by: codex
---

# Prompt Grading

本文件定義 Integrator Agent 發派 Contributor 任務時使用的 Prompt 分級。
目標不是讓 prompt 變得複雜，而是讓任務粒度、整合風險、驗收方式有一致標準。

!!! important "何時使用"
    Integrator Agent 在發出任何 Contributor Prompt 前，必須先決定本輪任務屬於哪個 Prompt Level。
    不得在同一輪同一工作流上同時混用多個互相矛盾的粒度。

## 設計原則

- Prompt 應該使用「**能完成一個有意義交付的最小等級**」。
- 若共享契約、邊界、驗收條件仍不穩，應降級，不應硬開大任務。
- 若共享契約、邊界、驗收條件已穩，且 Integrator 能承擔整合成本，應升級，不要把里程碑拆成大量零碎小修。
- 新一輪 Prompt 只能在前一輪相關 report 已回收、review、整合、驗證完成後再發出。

## Prompt Levels

### `L1 Fixup`

適用於：

- 單一 bug
- 單一 contract mismatch
- 單一 runtime error
- 單一 verify/test/build gate 失敗

特徵：

- 應明確指向一個問題
- 範圍窄
- 不應順便擴大成 redesign 或新功能

Done Definition：

- 問題被修掉
- 相關測試或 smoke check 綠燈
- 不引入新的邊界擴張

### `L2 Slice`

適用於：

- 一個完整 workflow slice
- 一個完整 command family slice
- 一個明確的 persisted/read/write slice
- 一個前後端可驗證的功能切片

特徵：

- 不只是小修
- 必須完成一段對使用者或系統有意義的路徑
- 仍限定在單一領域或單一產品面

Done Definition：

- 交付一條可描述、可驗證的完整路徑
- 不是只加一個 helper、button、欄位或 repository method

### `L3 Milestone`

適用於：

- 同一 workstream 的多個相關 slices
- 同一領域內的一個明顯里程碑
- 可用單一 review 準則驗收的一組交付

特徵：

- 可跨多個相關檔案與多個相關子模組
- 但仍應維持在單一邊界內
- Integrator 必須能清楚定義完成條件與驗收項目

Done Definition：

- 某一 workstream 的里程碑被明確推進
- 不只是多個 `L1/L2` 隨機綁在一起

### `L4 Phase Push`

適用於：

- 明確推進 migration phase 的一整段子目標
- 契約、邊界、驗收基線都已穩的情況

特徵：

- 風險最高
- 整合成本最高
- 只適合在 SoT、shared contracts、phase gates 都已清楚時使用

Done Definition：

- 對應 phase 的一段核心子目標被完成
- Integrator 能以 phase gate 或 parity 條目驗收

## 升級與降級規則

應升級 Prompt Level 的情況：

- 同一 workstream 已連續出現多輪小 prompt，整合成本開始高於實作成本
- 共享契約與邊界已穩，不再需要用小任務防止設計漂移
- 使用者明確要求加快 phase 推進

應降級 Prompt Level 的情況：

- backend/frontend/core/cli 共享契約仍常變
- 前一輪剛發生重大 review finding 或 integration conflict
- 同一區塊存在高風險 runtime 問題尚未釐清
- Integrator 尚未把前一輪報告整合完畢

## 每個 Prompt 必須包含的欄位

所有 Prompt Level 都必須明確提供：

- `Task ID / Topic`
- `Prompt Level`
- `Branch / Worktree`
- `Read first`
- `Current State`
- `Goal`
- `Allowed Files`
- `Non-Goals`
- `Implementation Requirements`
- `Verification`
- `Handoff`

### `L1 Fixup` 額外要求

- 必須明確指出單一問題來源
- 必須限制不要擴張成 broader redesign

### `L2 Slice` 額外要求

- 必須明確定義「這條 slice 完成後，什麼路徑會變成可用」
- 必須要求 agent 不要做到第一個小點就停

### `L3 Milestone` 額外要求

- 必須明確列出 milestone 的完成條件
- 必須明確說明哪些子區塊屬於同一里程碑

### `L4 Phase Push` 額外要求

- 必須引用 phase / parity / contract SoT
- 必須明確列出 phase gate 或整體驗收條件
- Integrator 必須準備更強的整合與回歸驗證

## Integrator Rules

- 同一 workstream 在同一時間只應有一份 active Prompt。
- 前一輪該 workstream 的 report 未回收前，不得先開下一輪。
- 如果 context compact 或回話中斷，Integrator 必須先重述：
  - 目前已整合的輪次
  - 尚未回收的輪次
  - 現在要開的是哪個 Prompt Level
- 若使用者要求加速，優先把 `L1` 與 `L2` 升級成更完整的 `L2` 或 `L3`，不要直接跳到 `L4`。

## Anti-Patterns

- 把一個明顯應該是 `L2 Slice` 的工作拆成多輪 `L1 Fixup`
- 在共享契約還不穩時直接開 `L4 Phase Push`
- 上一輪 report 還沒收回，就先發下一輪 prompt
- 一份 prompt 同時跨越多個不穩定邊界，導致 Integrator 無法可靠驗收
- 把多個不相關的小修補打包成假 `Milestone`

## 與其他規則的關係

- Prompt 分級屬於 Integrator 的工作方法規則，與 [Multiple Agent Collaboration](./multi-agent-collaboration.md) 一起使用。
- 若 task 涉及 phase 推進，應同時對照 [Phase Gates](./phase-gates.md)。
- 若 task 涉及 public contract 變更，仍必須同時更新 contract versioning、parity matrix 與相關測試。

## Agent Rule { #agent-rule }

```markdown
## Prompt Grading
- Integrator MUST assign a Prompt Level before issuing any Contributor Prompt.
- Prompt Levels:
    - `L1 Fixup`: one bug / one contract mismatch / one runtime issue.
    - `L2 Slice`: one coherent workflow or command/persistence slice.
    - `L3 Milestone`: one clear milestone within a single workstream.
    - `L4 Phase Push`: one phase-level push, only when contracts and gates are stable.
- Default rule:
    - choose the smallest level that can complete a meaningful delivery.
- Escalation rule:
    - if repeated small prompts are slowing down a stable workstream, escalate from `L1`/`L2` to `L2`/`L3`.
- Safety rule:
    - if shared boundaries are unstable or recent integration revealed major issues, downgrade prompt size.
- Integrator sequencing rule:
    - do not issue the next prompt for a workstream until the previous report has been reviewed, integrated, and verified.
- Required prompt fields:
    - Task ID / Topic
    - Prompt Level
    - Current State
    - Goal
    - Allowed Files
    - Non-Goals
    - Implementation Requirements
    - Verification
    - Handoff
```
