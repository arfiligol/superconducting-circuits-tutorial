---
aliases:
  - Accessibility
  - 無障礙設計
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: frontend a11y、語意化 HTML、鍵盤操作與 ARIA 規範。
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Accessibility

## Core Rules

- 使用語意化 HTML
- 互動元素必須可鍵盤操作
- icon-only button 必須有 `aria-label`
- 表單欄位必須有 label 與錯誤訊息
- 文字與背景對比度需符合 WCAG AA

## Agent Rule { #agent-rule }

```markdown
## Accessibility
- Use semantic HTML.
- Interactive elements must be keyboard accessible.
- Icon-only buttons require `aria-label`.
- Form fields require labels and visible error messages.
- Maintain WCAG AA contrast for text and critical UI states.
- Do not use clickable `div` elements when a button or link is the correct semantic choice.
```
