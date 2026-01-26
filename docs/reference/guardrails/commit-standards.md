---
aliases:
  - "Commit Standards"
  - "提交規範"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "Commit 時機、粒度、格式規範"
version: v1.0.0
last_updated: 2026-01-27
updated_by: docs-team
---

# Commit Standards

規範 **何時** 以及 **如何** 提交程式碼。

## 何時應該 Commit

1. **單一邏輯單元完成** - 一個 feature、一個 bugfix、一個 refactor
2. **通過所有檢查** - `uv run pre-commit run --all-files` 通過
3. **可獨立 revert** - 這個 commit 可以單獨撤銷而不破壞其他功能

## 何時不應該 Commit

1. **半途而廢** - 編譯不過、型別錯誤、測試失敗
2. **混合變更** - 同時修 bug + 加 feature + 改格式
3. **WIP 狀態** - 功能未完成 (除非明確標註 `WIP:`)

## Commit 粒度

| 類型 | 粒度 | 範例 |
|------|------|------|
| `feat:` | 一個完整功能 | `feat: add SQLite persistence layer` |
| `fix:` | 一個 bug 修復 | `fix: handle empty dataset in fit` |
| `docs:` | 一份文件更新 | `docs: add logging guardrails` |
| `refactor:` | 一個重構步驟 | `refactor: extract repositories` |
| `style:` | 格式修正 | `style: apply ruff formatting` |
| `test:` | 測試新增/修改 | `test: add unit tests for UoW` |
| `chore:` | 維護任務 | `chore: update dependencies` |

## Commit Message 格式

```
<type>: <短描述>

[可選：詳細說明]

[可選：Closes #issue]
```

**範例：**

```
feat: add colored logging with Rich

- Created core/shared/logging.py setup function
- Updated tech-stack.md with Rich dependency
- Added logging.md guardrails

Closes #42
```

---

## Agent Rule { #agent-rule }

```markdown
## Commit Standards
- **When to Commit**:
    - Single logical unit complete (one feature, one fix, one refactor).
    - All checks pass: `uv run pre-commit run --all-files`.
    - Independently revertable.
- **When NOT to Commit**:
    - Code doesn't compile/type-check.
    - Mixed changes (bug fix + feature + formatting).
    - Incomplete work (unless `WIP:` prefix).
- **Commit Format**: `<type>: <description>`
    - Types: `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`.
- **Before Commit**: ALWAYS run `uv run pre-commit run --all-files`.
```
