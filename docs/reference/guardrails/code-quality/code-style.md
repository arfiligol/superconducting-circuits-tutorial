---
aliases:
  - Code Style
  - 程式碼風格
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Python 與 TypeScript 的共同程式風格與實作原則。
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Code Style

本專案的風格規則以「可讀、可改、可測」為優先。
若某個實作讓 UI、API、CLI 其中一層看起來方便，卻讓共享規則變得分散或難以驗證，則視為不合格。

## Cross-Language Principles

- 優先小 diff，避免無關重構
- 一個函式只做一件事
- 明確命名，不用模糊縮寫
- 避免把業務邏輯塞進 route handler、React component 或 CLI command
- 重複邏輯先抽到共享層，再擴增呼叫點

## Python Rules

- 使用現代語法：`list[str]`、`str | None`
- 依照 Ruff 規範維持 import 與格式一致
- 在科學計算情境中，必要時可在名稱中保留單位，例如 `frequency_hz`
- `core/` 與 service 層禁止 `print()`

## TypeScript Rules

- 使用 TypeScript strict mode
- 禁止無理由的 `any`
- component props、service 回傳值、schema parse 結果都要有明確型別
- React component 應保持 presentation-focused，資料抓取與 mutation 邏輯集中在 hooks / services

## Refactoring Rule

- 先做能被驗證的小步修改
- 先修正結構問題，再考慮抽象化
- 若抽象只服務單一使用點且沒有減少複雜度，先不要抽

## Agent Rule { #agent-rule }

```markdown
## Code Style
- **Standard**:
    - Python uses Ruff + modern Python syntax
    - TypeScript uses strict typing and consistent formatting
- **Naming**:
    - variables use clear nouns
    - functions use clear verb phrases
    - scientific names may include units when that removes ambiguity
- **Boundaries**:
    - do not put business workflow logic inside route handlers, React components, or CLI commands
    - shared logic belongs in services or `src/core/`
- **Refactoring**: prefer small, atomic changes
- **Complexity**: keep functions focused; split code when one function starts handling multiple responsibilities
```
