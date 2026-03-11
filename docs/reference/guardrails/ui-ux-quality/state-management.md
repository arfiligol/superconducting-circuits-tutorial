---
aliases:
  - State Management
  - 狀態管理
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: frontend server/client/form state 的策略。
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# State Management

## State Categories

| 類型 | 工具 | 用途 |
| --- | --- | --- |
| Server State | SWR | API 讀取、cache、revalidation |
| Client UI State | React Context 或局部 state | shell 狀態、選取狀態、暫時 UI 狀態 |
| Form State | React Hook Form + Zod | 表單驗證與提交 |
| URL State | route params / search params | 可分享、可重播的頁面狀態 |

## Rules

- component 內不要直接散落 `fetch`
- API 讀取應集中在 hooks / services
- mutation 應明確處理 loading、success、error
- 可以由 URL 表示的狀態，不要藏在 global context

## Agent Rule { #agent-rule }

```markdown
## State Management
- Use SWR for server state.
- Use React Hook Form + Zod for form state.
- Use Context or local state for UI-only state.
- Use route params or search params for shareable page state.
- Do not scatter direct `fetch` calls across components.
- Keep read and mutation logic in hooks or services with explicit loading/error handling.
```
