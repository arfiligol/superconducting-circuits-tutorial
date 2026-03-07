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
version: v1.2.0
last_updated: 2026-03-07
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
- **Contributor Agent**：
  - 只在被分派範圍內修改
  - 只能產出可被整合的原子 commits 與交接說明

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
- **Never**:
    - Never revert/overwrite others' unintegrated work.
    - Never use destructive git cleanup on shared work.
```
