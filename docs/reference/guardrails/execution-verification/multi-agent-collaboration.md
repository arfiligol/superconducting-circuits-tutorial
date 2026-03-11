---
aliases:
  - "多 Agent 協作"
  - "Multiple Agent Collaboration"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "本地多 Agent 並行開發的隔離、整合與衝突避免規範"
version: v1.4.0
last_updated: 2026-03-12
updated_by: codex
---

# 多 Agent 協作

規範本地多 Agent 並行工作時的責任分工與防衝突流程。

!!! important "單一整合者原則（Mandatory）"
    同一條交付線（同一主題/PR）在同一時間只允許 **1 位 Integrator Agent**。
    其餘 Agent 僅負責各自子任務，不得自行整合他人變更。

## 角色定義

- **Integrator Agent**：
  - 唯一可進行整合動作（cherry-pick、resolve conflict、最終 merge 準備）
  - 負責整體驗收與回歸結果彙整
  - 負責把 Contributor 在各自 `worktree + branch` 產出的變更整合回主交付 branch
  - 若使用者平常工作的 branch 是 `main`，預設整合回 `main`
  - 若使用者明確在另一條開發 branch / IDE 所在 branch 上工作，則整合回該 branch，而不是只停留在 Integrator 自己的隔離 branch
  - 負責決定每輪任務的拆分方式、Prompt 結構、驗收條件、整合順序
  - 負責判斷何時應維持固定 Contributor Agent 模式，何時需要臨時增派專項 Agent
- **Contributor Agent**：
  - 只在被分派範圍內修改
  - 只能產出可被整合的原子 commits 與交接說明

## Fixed Agent Pool

本專案當前固定使用下列 Agent 身份：

1. **Integration Agent**
   - 唯一的整合者
   - 只負責 task split、prompt 發派、contributor 回收、cherry-pick、conflict resolution、驗證與最終整合
   - 不負責日常 feature 開發，除非使用者明確要求例外
2. **Frontend Contributor Agent**
   - 負責 `frontend/` 與前端 UI/API integration 任務
3. **Backend Contributor Agent**
   - 負責 `backend/` 與 API/service/infrastructure 任務
4. **Core Contributor Agent**
   - 負責 `src/core/` 與共享科學邏輯、shared workflow 任務
5. **CLI Contributor Agent**
   - 負責 `cli/` 與正式 CLI adapter / command surface 任務

!!! important "Contributor identities are fixed"
    除了 `Frontend Contributor Agent`、`Backend Contributor Agent`、`Core Contributor Agent`、`CLI Contributor Agent` 之外，
    不應再建立其他 Contributor 身份。
    若某項工作跨越多個領域，應由 Integration Agent 重新切分任務，或分派給上述既有角色之一，而不是臨時發明新的 Contributor 類型。

## Integrator First Workflow

每次開一位新的 Integrator Agent，都應先做以下流程：

1. **讀 SoT**
   - 先讀本文件與當前主題的 architecture / guardrail SoT。
   - 先判斷目前是延續既有交付線，還是開啟新的一輪 phase。

2. **盤點主線狀態**
   - 確認使用者實際工作的 delivery branch（通常是 `main`）。
   - 盤點目前已整合、未整合、已過時的 branches / worktrees。
   - 不得把「僅存在 Integrator 隔離 branch」誤當成已完成整合。

3. **決定任務切分**
   - 先決定哪些工作必須由 Integrator 自己處理：
     - cherry-pick / conflict resolution
     - cross-agent overlap 熱區
     - 最終 regression / acceptance
   - 再決定哪些工作可外包給 Contributors。

4. **先文件、再程式**
   - 若任務涉及新 contract / architecture / semantics，先要求 contributor 讀 guardrails，先補文件，再一次性改程式碼。
   - Integrator 本人也應遵守同一原則。

5. **發派 Prompt**
   - 每個任務都必須明確提供：
     - `Task ID / Topic`
     - `Goal`
     - `Allowed Files`
     - `Non-Goals` / `Constraints`
     - `Verification`
     - `Contributor Report v1`
   - `Allowed Files` 由 Integrator 每輪任務明確定義，而不是由文件永久釘死。

6. **整合與驗證**
   - 只整合真正的增量 commit。
   - 若 contributor report 不完整、越界、或只有 dirty worktree 沒有 commit，Integrator 不應直接視為合格交付。
   - 最後一定要把 accepted changes 整回使用者的 delivery branch。

## Role Policy

- Contributor 角色集合固定為：
  - `Frontend Contributor Agent`
  - `Backend Contributor Agent`
  - `Core Contributor Agent`
  - `CLI Contributor Agent`
- Integrator 若遇到額外需求，應重新切分 `Allowed Files` 與 task scope，而不是新增新角色名稱。
- 若未來真的需要新增或替換 Contributor 類型，必須先更新本 SoT，再開始使用新身份。

## 必須遵守的協作流程

1. **Preflight 檢查**
   - 開工前必須回報 `git status --porcelain`。
   - 若工作樹存在非本人任務變更，必須停下並回報處理選項，不得直接覆蓋。

2. **隔離工作區**
   - 每位 Agent 必須使用獨立 `git worktree` + branch（Mandatory）。
   - 禁止多位 Agent 共用同一個髒工作樹同時編輯。

3. **檔案所有權**
   - 每個任務必須有 `Allowed Files`（允許修改清單）。
   - 需要跨界改檔時，先交由 Integrator 重新分派，不得直接越界編輯。

4. **交接**
   - Contributor 必須提供：
     - commit hashes
     - 變更檔案清單
     - 測試結果
     - 已知風險
   - Integrator 才可進行最終整合。
   - `最終整合` 的完成定義是：相關變更已從 contributor worktrees 整合回主交付 branch
     （通常是 `main`；若使用者正在另一條明確指定的開發 branch 上工作，則為該 branch）。

## 禁止事項

- 禁止覆寫或回退其他 Agent 的未整合變更。
- 禁止使用 destructive git 指令清空他人工作（例如 `git reset --hard`）。
- 禁止在未分派檔案上「順手修」。

---

## Agent Rule { #agent-rule }

```markdown
## Multiple Agent Collaboration
- **Single Integrator (Mandatory)**:
    - One delivery line/PR MUST have exactly one Integrator Agent at a time.
    - Only Integrator may perform final integration (cherry-pick/conflict resolution/merge prep).
    - Integrator MUST carry accepted contributor changes back to the delivery branch used by the user.
    - The default delivery branch is `main`; if the user is actively working on another explicit branch, integrate back to that branch instead.
    - Integrator MUST define the task split, prompt structure, `Allowed Files`, and acceptance criteria for each round.
    - Integrator MUST treat prompt design as part of the integration job, not as an optional extra.
- **Fixed Agent Pool**:
    - The contributor pool is restricted to exactly four contributor identities:
        - Frontend Contributor Agent
        - Backend Contributor Agent
        - Core Contributor Agent
        - CLI Contributor Agent
    - Integration Agent is the only integrator identity.
    - Do not invent temporary contributor role names without updating this source-of-truth first.
    - Exact file boundaries are still defined per task by the Integrator.
- **Contributor Boundaries**:
    - Contributors MUST edit only assigned files (`Allowed Files`).
    - If required changes exceed scope, stop and hand off to Integrator.
- **Preflight**:
    - Before editing, run `git status --porcelain`.
    - If unrelated dirty changes exist, do not proceed blindly; report and wait.
- **Isolation**:
    - MUST use one `git worktree` + one branch per agent/task.
    - Do not let multiple agents co-edit the same dirty worktree.
- **Handoff Required**:
    - Provide commit hashes, changed files, test results, and known risks.
    - Dirty worktree changes without a committed handoff are not a complete contributor deliverable.
- **Never**:
    - Never revert/overwrite others' unintegrated work.
    - Never use destructive git cleanup on shared work.
```
