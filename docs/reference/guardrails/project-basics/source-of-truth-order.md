---
aliases:
  - "Source of Truth Order"
  - "單一真理優先順序"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/project-basics
status: stable
owner: docs-team
audience: team
scope: "定義 migration 過程中 reference docs、shared core、adapter、legacy behavior 的裁決順序"
version: v1.2.0
last_updated: 2026-03-13
updated_by: team
---

# Source of Truth Order

本文件定義 migration 過程中各種規格來源的優先順序，避免 Contributor Agent 在 reference、legacy 與新實作之間自行猜測。

## Canonical Ordering

若同一能力的描述彼此衝突，應依下列順序裁決：

1. `docs/reference/data-formats/*`、`docs/reference/app/frontend/**/*`、`docs/reference/cli/*`
2. `docs/reference/architecture/*` 與後續的 contract registry / migration parity 文件
3. `src/core/sc_core/*` 的 canonical implementation
4. `backend/`、`frontend/`、`cli/`、`desktop/` adapters
5. legacy `src/app/` 與舊 `src/scripts/*` 行為

## Scope Boundaries

- `docs/reference/data-formats/*`：資料格式、schema version、欄位語意
- `docs/reference/app/frontend/**/*`：使用者可見 workflow、頁面行為、recovery parity
- `docs/reference/cli/*`：命令名稱、主要參數、輸出契約
- `docs/reference/architecture/*`：identity/workspace、task semantics、parity matrix、contract registry
- `src/core/sc_core/*`：canonical invariants、validators、shared transforms、task routing helpers
- adapters：transport、mapping、storage/runtime integration，不可反向改寫 canonical truth

## Conflict Handling

### Typical Cases

| 衝突情境 | 裁決方式 |
| --- | --- |
| reference docs 與 legacy 行為不同 | 以 reference docs 為準，legacy 僅作 parity evidence |
| `sc_core` 與 backend/frontend/cli adapter 不同 | 先修 adapter；若 `sc_core` 缺規格，再同步補 docs 與 `sc_core` |
| frontend mock 與 backend schema 不同 | 以 backend schema + reference docs 為準，前端需改 |
| CLI 舊命令輸出與新 contract 不同 | 以 reference CLI contract 為準；若需保留舊輸出，必須在 contract registry 記錄 |
| legacy 特例需要保留 | 必須在 parity matrix 和 contract registry 顯式標記，不可只留在程式碼內 |

## Interpretation Rules

- **Reference-first**：
  若 reference 文件與 legacy 行為衝突，預設以 reference 文件為準。
- **Legacy is parity evidence, not canonical law**：
  legacy 行為只作為 parity 驗收與遷移參考，不自動成為 canonical truth。
- **Shared core beats adapters**：
  若 `sc_core` 與 adapter 行為衝突，先修 adapter；只有在 contract 本身不完整時才修 `sc_core` 與其文件。
- **Do not silently rewrite docs to match code**：
  發現 adapter 或 legacy 與 reference 不一致時，不可直接改文件湊合程式碼，除非使用者明確確認規格要變。
- **Parity exceptions must be explicit**：
  若確定要保留 legacy 特例，必須在 parity matrix 或 contract registry 顯式記錄，不能只留在程式碼內。

## Required Follow-up Documents

本文件不單獨生效。若發生跨層衝突，應一併檢查：

- [Task Semantics](../../architecture/task-semantics.md)
- [Identity / Workspace Minimal Model](../../architecture/identity-workspace-model.md)
- [Parity Matrix](../../architecture/parity-matrix.md)
- [Canonical Contract Registry](../../architecture/canonical-contract-registry.md)

## Agent Rule { #agent-rule }

```markdown
## Source of Truth Order
- Resolve conflicts in this order:
    1. `docs/reference/data-formats/*`, `docs/reference/app/frontend/**/*`, `docs/reference/cli/*`
    2. `docs/reference/architecture/*` and migration contract/parity specs
    3. `src/core/sc_core/*`
    4. `backend/`, `frontend/`, `cli/`, `desktop/` adapters
    5. legacy `src/app/` and old script behavior
- Treat legacy behavior as parity evidence, not automatic canonical truth.
- If docs and adapters conflict, prefer docs unless the user explicitly changes the spec.
- If `sc_core` and adapters conflict, fix the adapter first unless the canonical contract is incomplete.
- Record any intentional legacy-only exception in the parity matrix or contract registry.
```
