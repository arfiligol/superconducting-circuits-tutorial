---
aliases:
  - "Guardrails: UI/UX 品質"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: UI/UX 品質

本專案的 NiceGUI 應用程式 (`src/app/`) 遵循統一的 UI 品質標準，確保視覺一致性與可維護性。

!!! important "Source of Truth"
    所有 UI 元件、配色、佈局必須遵守以下子規範。

## 技術堆疊

| 層級 | 工具 | 說明 |
|---|---|---|
| 框架 | **NiceGUI** | Python 原生 UI 框架，底層為 Quasar/Vue |
| 樣式 | **CSS Variables** (Design Tokens) | `theme.css` — `--bg`, `--surface`, `--fg` 等 |
| 佈局 | **Tailwind CSS** | 僅用於佈局 (`flex`, `p-4`, `gap-2`) — **禁止**用於顏色 |
| 元件 | **NiceGUI 內建** | `ui.table`, `ui.plotly`, `ui.label`, `ui.button` |
| 視覺化 | **Plotly** | 透過 `plotly_theme.py` 與應用主題同步 |
| 深色模式 | **`ui.dark_mode()`** | `.dark` class 切換 CSS 變數 |

## 子規範

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [主題系統](./theming.md) | Design Token、深色模式、Plotly 主題同步 | [#agent-rule](./theming.md#agent-rule) |
| [元件規範](./component-guidelines.md) | NiceGUI 元件使用規則、禁止項目、資料密集表格契約 | [#agent-rule](./component-guidelines.md#agent-rule) |
| [佈局規範](./layout-patterns.md) | Shell 架構、Card 排版、響應式規則、Large Data Explorer | [#agent-rule](./layout-patterns.md#agent-rule) |

---

## Agent Rule { #agent-rule }

```markdown
## UI/UX Quality
- **Framework**: NiceGUI (`src/app/`). All pages inside `app_shell()`.
- **Styling**: CSS Variables (design tokens) for colors. Tailwind for layout only.
- **Dark Mode**: Default ON. `.dark` class toggles CSS variables.
- **Vis**: Plotly via `ui.plotly(fig)`, theme-synced via `get_plotly_layout(dark)`.
- **Forbidden**: hardcoded colors, `ui.aggrid`, `alert()`/`confirm()`, raw HTML controls.
- Sub-rules: Theming, Component Guidelines, Layout Patterns.
```
