---
aliases:
  - "多 Agent 協作"
  - "Multiple Agent Collaboration"
  - "Agent Collaboration Framework"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Documentation / Planning / Implementation / Review / Test Agents 的責任分工、交接順序與並行協作規範"
version: v2.0.0
last_updated: 2026-03-14
updated_by: codex
---

# 多 Agent 協作

規範本專案的多 Agent 協作框架，確保文件、計劃、實作、驗收與測試有明確 owner。

!!! important "Single Review Authority"
    同一條交付線（同一主題 / PR / milestone）在同一時間只允許 **1 位 active Review Agent** 負責整合與主線回收。
    可以同時有多位 Documentation / Planning / Implementation / Test Agents，但不可同時有多位 Review Agents 對同一交付線做最終整合。

!!! info "Document-first execution"
    正式流程是：先收斂文件，再寫計劃，再做實作，再補 integration / E2E，最後由 Review Agent 收回主線。

## Collaboration Map

| stage | primary owner | output |
| --- | --- | --- |
| Documentation | Documentation Agent | updated SoT / decision notes |
| Planning | Planning Agent | plan artifact + test backlog |
| Implementation | Frontend / Backend / Core / CLI Agent | code + unit tests + delivery report |
| Test | Test Agent | integration / E2E tests + evidence |
| Review | Review Agent | integrated delivery + final verification |

## Agent Families

| Agent family | Primary responsibility | Not responsible for |
|---|---|---|
| Documentation Agents | 與人類開發者討論需求、整理決策、把 SoT 寫進 docs、先定義 architecture / contracts / page specs | 大量 feature code、integration / E2E |
| Planning Agents | 比對文件與現有程式碼、找出缺漏、撰寫 plan artifact、拆 implementation slices、列出缺的 integration / E2E coverage | 大量產品實作、最終整合 |
| Implementation Agents | 依計劃撰寫 `Frontend / Backend / Core / CLI` 實作與 unit tests | integration tests、E2E tests、最終主線整合 |
| Review Agents | 回收 implementation/test deliverables、做 cherry-pick / conflict resolution / final verification、收回主線 | 日常 feature 開發、繞過計劃直接大幅擴張 scope |
| Test Agents | 依計劃撰寫 integration / E2E tests、補 test fixtures 與 cross-surface verification | feature unit work、最終 merge authority |

## Role Boundaries

### Documentation Agents

- 負責與人類開發者對齊需求、語意、owner boundary 與 acceptance。
- 若新功能或重構涉及 contract / workflow / shell context / permission model，必須先補或更新 SoT。
- 可直接修改文件，但不得把未確認的設計假設寫成既成事實。

### Planning Agents

- 必須讀 SoT 與現有 code，再產出可交付的 plan artifact。
- plan artifact 至少要回答：
  - 哪些文件已定義、哪些尚未落地
  - 哪些 implementation slices 需要前端 / 後端 / core / CLI Agents
  - 哪些功能尚未具備 integration tests / E2E tests
  - 每個 slice 的 verification 與 non-goals
- 不應在沒有 plan artifact 的情況下直接大規模派工。

### Implementation Agents

- 固定分成四條 implementation lanes：
  - `Frontend Agent`
  - `Backend Agent`
  - `Core Agent`
  - `CLI Agent`
- 只負責自己的領域實作與 unit tests。
- 若需要跨界改檔，必須回交 Planning 或 Review Agent 重新切分。
- 不負責 integration / E2E test。

### Review Agents

- 是唯一可把 accepted changes 收回主交付 branch 的角色。
- 負責：
  - 回收 implementation 與 test deliverables
  - conflict resolution
  - final verification
  - 回主線後的 regression summary
- 若使用者的 delivery branch 是 `main`，預設整回 `main`。
- 若使用者明確在其他 branch 工作，Review Agent 必須整回該 branch。

### Test Agents

- 只負責 integration tests、E2E tests、cross-surface verification。
- 必須直接依 Planning Agent 的 test backlog 與 SoT 撰寫測試。
- 不應把 integration / E2E 缺口留給 Implementation Agents 臨時補。

## Delivery Flow

1. **Documentation**
   - Documentation Agent 與人類對齊需求。
   - 必要時先更新 SoT。

2. **Planning**
   - Planning Agent 讀文件與程式碼。
   - 產出 plan artifact 與 test backlog。

3. **Implementation**
   - Frontend / Backend / Core / CLI Agents 依 slice 開發。
   - 每條 implementation lane 只做 code + unit tests。

4. **Test**
   - Test Agent 根據同一份 plan 補 integration / E2E tests。

5. **Review**
   - Review Agent 回收所有 deliverables。
   - 做整合、驗證、主線回收與最終摘要。

!!! warning "No direct jump from idea to code"
    若需求仍在變、authority boundary 未定、或 SoT 尚未更新，Implementation Agents 不得直接把設計猜進程式碼。

## Required Artifacts

| Stage | Required artifact |
|---|---|
| Documentation | updated SoT pages / decision notes |
| Planning | `Plan Artifact`，含 implementation slices 與 test backlog |
| Implementation | `Delivery Report`，含 commits、changed files、unit test results、known risks |
| Test | `Test Report`，含 scenarios、evidence、integration / E2E results |
| Review | `Review Merge Report`，含 accepted commits、conflicts、final verification、mainline status |

## Plan Artifact Minimum Content

Planning Agent 產出的 plan artifact 至少必須包含：

- `Task ID / Topic`
- `Goal`
- `Source of Truth`
- `Current Implementation State`
- `Gap List`
- `Implementation Slices`
- `Test Backlog`
- `Verification Matrix`
- `Open Decisions / Risks`

!!! tip "Plan artifacts are first-class docs"
    若該計劃需要被持續追蹤或多人共同引用，應把它寫成可保存的文件紀錄，而不是只留在短訊息或臨時聊天上下文中。

## Parallelism Rules

1. 同一時間可並行：
   - 多位 Documentation Agents
   - 多位 Planning Agents
   - 多位 Implementation Agents
   - 多位 Test Agents
2. 但同一交付線只能有一位 active Review Agent。
3. 同一 implementation slice 不得同時交給兩位 Implementation Agents。
4. 同一 integration / E2E scenario 不得同時交給兩位 Test Agents。

## Isolation Rules

1. 每位 Agent 必須使用獨立 `git worktree` + branch。
2. 開工前必須執行 `git status --porcelain`。
3. 若工作樹有非本人任務的 dirty changes，不得直接覆蓋。
4. `Allowed Files` 必須在 plan 或 review prompt 中明確列出。

## Escalation Rules

| Situation | Required escalation |
|---|---|
| SoT 缺頁或語意衝突 | 回 Documentation Agent |
| slice 邊界不穩或跨多領域 | 回 Planning Agent 重新拆分 |
| integration / E2E 缺口被 implementation 發現 | 回 Planning Agent，並轉交 Test Agent |
| deliverables 彼此衝突 | 交 Review Agent 做整合與裁決 |

## Forbidden Moves

- Implementation Agent 不得直接宣告 integration / E2E 已完成，除非該工作明確由 Test Agent 交回。
- Test Agent 不得順手重寫 feature implementation。
- Review Agent 不得在未回收 handoff 的情況下假設某工作已完成。
- Documentation Agent 不得把未確認的未來功能寫成現況。
- Planning Agent 不得只給口頭方向而沒有可追蹤的 plan artifact。

## Related

- [Prompt Grading](./prompt-grading.md)
- [Agent Handoff Formats](./contributor-reporting.md)
- [Phase Gates](./phase-gates.md)

## Agent Rule { #agent-rule }

```markdown
## Multiple Agent Collaboration
- Use five agent families:
    - Documentation Agents
    - Planning Agents
    - Implementation Agents
    - Review Agents
    - Test Agents
- Documentation Agents:
    - discuss with humans
    - update SoT and architecture/contracts before coding when needed
- Planning Agents:
    - compare docs and code
    - produce a written plan artifact
    - split implementation slices
    - enumerate missing integration/E2E coverage for Test Agents
- Implementation Agents:
    - restricted to Frontend / Backend / Core / CLI lanes
    - own code + unit tests only
    - do not own integration/E2E or final branch integration
- Review Agents:
    - one active Review Agent per delivery line
    - own cherry-pick, conflict resolution, final verification, and mainline integration
- Test Agents:
    - own integration tests and E2E tests
    - execute against the plan artifact and SoT
- Every agent must use an isolated worktree + branch and run `git status --porcelain` before editing.
- Do not skip the order:
    - docs -> planning -> implementation -> test -> review
```
