---
aliases:
  - Component Guidelines
  - 元件規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/ui-ux
status: stable
owner: docs-team
audience: contributor
scope: frontend component 選型、表單、dialog 與資料表格規範。
version: v2.1.0
last_updated: 2026-03-14
updated_by: docs-team
---

# Component Guidelines

元件規範的目標是讓 frontend 在資料密集與互動密集情境下仍保持一致。

!!! info "How to read this page"
    先決定元件屬於 primitive、feature-local 還是 app-wide layout，再看 interaction 與 data browser 規則。這頁重點是 component boundary，不是完整 design system token 表。

## Component Sources

| 類型 | 來源 |
| --- | --- |
| 基礎 UI primitives | `@/components/ui/*`（shadcn/ui） |
| feature-specific UI | `frontend/src/features/<feature>/components/*` |
| app-wide layout | `frontend/src/components/layout/*` |

## Interaction Rules

- 優先使用 `@/components/ui` 的 Button、Input、Select、Dialog、Tabs、Table 等封裝
- 禁止使用 `alert()`、`confirm()`、`prompt()`
- 表單要搭配 Label、validation、error state
- destructive action 必須有確認流程
- 所有可點擊 icon 必須提供明確 hover state；至少要有 cursor feedback 與可見的 hover 樣式變化
- data-dense table 必須支援 sorting、filtering、pagination 或明確的 virtualization 策略

!!! warning "Confirmation rule"
    destructive action 不能退化成 browser-native `confirm()`。產品互動必須保留一致的語意、樣式與 error handling surface。

## Data Browser Contract

- 列表先載入 summary rows
- 詳細 payload 僅在 row selection 或 detail panel 時抓取
- 不要因為單純切頁就重抓大型 payload

## Agent Rule { #agent-rule }

```markdown
## Component Guidelines
- Prefer components from `@/components/ui/` for interactive primitives.
- Put feature-specific UI in `frontend/src/features/<feature>/components/`.
- Do not use `alert()`, `confirm()`, or `prompt()` for product interactions.
- Destructive actions require an explicit confirmation flow.
- Forms need labels, validation, and visible error states.
- Clickable icons must provide a clear hover state, including pointer feedback and visible hover styling.
- Data-dense tables must support sorting, filtering, and pagination or a clear virtualization strategy.
- Load summary rows first; fetch heavy detail payload only on explicit detail interaction.
```
