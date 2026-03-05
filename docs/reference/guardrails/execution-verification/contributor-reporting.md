---
aliases:
  - "Contributor Agent 回報格式"
  - "Contributor Reporting"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Contributor Agent 標準回報格式，供 Integrator 與 PM 直接複製貼上使用"
version: v1.0.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Contributor Agent 回報格式

規範 Contributor Agent 的回報結構，讓使用者可直接閱讀，且可直接複製貼上給 Integrator Agent 進行整合判斷。

!!! important "目標"
    回報必須同時滿足兩件事：
    1) 人類可快速看懂成果與風險
    2) Integrator Agent 可直接機器化提取 commit / 檔案 / 測試 / 風險

## 標準回報模板（必須使用）

```markdown
## Contributor Report v1

### 0) 任務資訊
- Agent: <name>
- Task ID / Topic: <id-or-title>
- Branch / Worktree: <branch-or-path>
- Scope (Allowed Files): <summary>
- 狀態: <done|blocked|needs-integrator>

### 1) Summary
- 目標: <what was requested>
- 結果: <what is now true>

### 2) Preflight 與邊界遵守
- 開工前 `git status --porcelain`: <clean|dirty + note>
- 是否遇到跨界需求: <no|yes + reason>
- 跨界處理方式: <n/a|handoff-to-integrator>

### 3) 變更內容
- Commit(s):
  - `<hash>` `<message>`
  - `<hash>` `<message>`
- Changed Files:
  - `<path>`: <why changed>
  - `<path>`: <why changed>

### 4) 文件更新（若有）
- `<path>`: <contract/spec change>

### 5) 測試結果
- Commands:
  - `<command>`
  - `<command>`
- Results:
  - `<pass/fail + key output>`

### 6) Playwright / E2E（若任務要求）
- Scenarios:
  - <scenario-1>
  - <scenario-2>
- Evidence:
  - `<screenshot-abs-path>`
  - `<log-or-report-abs-path>`
- 結果: <pass/fail>

### 7) 已知風險與限制
- <risk-1>
- <risk-2>

### 8) 需要 Integrator 決策的事項（若有）
- <decision-needed-1>
- <decision-needed-2>

### 9) 回退資訊
- 建議回退 commit: `<hash>`（若需要）
```

## 必填欄位

- 必須包含：`Commit(s)`、`Changed Files`、`測試結果`、`已知風險`
- 若任務要求 Playwright，必須包含：`Scenarios` + `Evidence` + `結果`
- `Changed Files` 必須附上每檔案變更理由，不可只有路徑清單

## 可讀性規範

- 先給結論，再給證據
- 不要貼整段長 log，改為「指令 + 結果摘要 + 證據路徑」
- 回報用語必須區分：
  - **已完成**
  - **已驗證**
  - **待 Integrator 決策**

---

## Agent Rule { #agent-rule }

```markdown
## Contributor Reporting Format
- Contributors MUST use `Contributor Report v1` structure for handoff.
- Mandatory sections:
    - Task info
    - Commit hashes
    - Changed files with reason
    - Test commands and results
    - Known risks
- If Playwright is required:
    - MUST include scenarios, evidence paths, and pass/fail result.
- Reporting quality rules:
    - Lead with conclusion, then evidence.
    - Summarize logs; do not dump long raw logs.
    - Explicitly separate completed work vs verified work vs items needing integrator decision.
```
