---
aliases:
  - Theming
  - 主題規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: frontend theme system、semantic tokens 與 dark mode 規範。
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Theming

主題系統必須為 Next.js frontend 服務，而不是把顏色散落在 component 內。

## Theme Management

- 使用 `next-themes`
- root layout 提供 `ThemeProvider`
- 提供 light / dark / system 三種模式

## Semantic Tokens

樣式應優先使用語意化 token，例如：

- `background`
- `foreground`
- `card`
- `muted`
- `border`
- `primary`
- `destructive`

禁止直接把 `bg-white`、`text-black`、硬編碼 hex 當成產品語意。

## Rules

- Tailwind 可用於佈局與語意 class，不要用來散布硬編碼色彩決策
- 新元件必須在 light / dark 下都可讀
- 圖表主題需跟隨目前 theme
- 任何 theme 切換不可造成表單或選取狀態重置

## Agent Rule { #agent-rule }

```markdown
## Theming
- Use `next-themes` for theme management.
- Provide `light`, `dark`, and `system` modes.
- Prefer semantic tokens such as `background`, `foreground`, `card`, `muted`, `border`, and `primary`.
- Do not hardcode product colors with raw utility choices like `bg-white`, `text-black`, or literal hex values unless there is a documented exception.
- Every component must remain readable in both light and dark themes.
- Chart styling must follow the active theme.
- Theme switching must not trigger avoidable state loss.
```
