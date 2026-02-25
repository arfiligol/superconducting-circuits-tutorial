---
aliases:
  - "Guardrails: 主題系統 (Theming)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: 主題系統 (Theming)

本文檔定義了 Design Token 系統、深色模式與 Plotly 主題同步的規範。

## Design Token 系統

所有顏色必須透過 CSS 變數（Design Tokens）定義，存放於 `src/app/styles/theme.css`。

### Token 清單

| Token | Light 值 | Dark 值 | 用途 |
|---|---|---|---|
| `--bg` | slate-50 | slate-900 | 頁面背景 |
| `--surface` | white | slate-800 | 卡片、面板 |
| `--elevated` | slate-100 | slate-700 | Hover 狀態、巢狀表面 |
| `--fg` | slate-900 | slate-200 | 主要文字 |
| `--muted` | slate-500 | slate-400 | 次要文字 |
| `--border` | slate-200 | slate-700 | 分隔線 |
| `--primary` | blue-500 | blue-400 | 按鈕、啟用狀態 |
| `--primary-fg` | white | slate-900 | Primary 上的文字 |
| `--danger` | red-600 | red-400 | 錯誤狀態 |
| `--warning` | amber-500 | amber-400 | 警告狀態 |
| `--success` | emerald-500 | emerald-400 | 成功狀態 |

### 使用方式

```css
/* ✅ 正確：使用 token */
background-color: rgb(var(--surface));
color: rgb(var(--fg));
border: 1px solid rgb(var(--border));

/* ❌ 禁止：硬編碼顏色 */
background-color: white;
color: #0f172a;
background-color: rgb(30, 41, 59);
```

### Semantic Utility Classes

`theme.css` 提供語義化的 utility classes：

| Class | 對應 Token | 用途 |
|---|---|---|
| `.bg-bg` | `--bg` | 頁面背景 |
| `.bg-surface` | `--surface` | 卡片背景 |
| `.bg-elevated` | `--elevated` | Hover / 巢狀元素 |
| `.text-fg` | `--fg` | 主要文字 |
| `.text-muted` | `--muted` | 次要文字 |
| `.border-border` | `--border` | 邊框顏色 |

## Tailwind CSS 使用規則

Tailwind **僅用於佈局**，不可用於顏色。

```python
# ✅ 正確：Tailwind = 佈局
ui.column().classes("w-full flex flex-col gap-4 p-4")

# ✅ 正確：Token class = 顏色
ui.column().classes("bg-surface text-fg border-border")

# ❌ 禁止：Tailwind 顏色
ui.column().classes("bg-white text-black bg-blue-500")
```

## 深色模式

- **預設**：深色模式開啟（`ui.run(dark=True)`）
- **切換**：`ui.dark_mode().toggle()` 在根元素切換 `.dark` class
- **自動**：CSS 變數隨 `.dark` class 自動切換，無需 JavaScript

!!! warning "每個元件都必須支援深色模式"
    新增的 CSS class 或 component 必須定義 `:root` 和 `.dark` 兩組值。

## Plotly 主題同步

Plotly 圖表的背景與字型必須與 App 主題同步。

```python
from core.shared.visualization import get_plotly_layout

# ✅ 正確：透過 theme sync 函式
fig = build_line_chart(record, dark=ui.dark_mode().value)

# ❌ 禁止：硬編碼 Plotly 佈局顏色
fig.update_layout(paper_bgcolor="white", font_color="black")
```

`get_plotly_layout(dark=True)` 回傳：

- `template`: `plotly_dark` / `plotly_white`
- `paper_bgcolor`: 對應 `--surface`
- `plot_bgcolor`: 對應 `--bg`
- `font.color`: 對應 `--fg`
- `font.family`: `Inter, Arial, sans-serif`

---

## Agent Rule { #agent-rule }

```markdown
## Theming
- Use CSS variable tokens: `--bg`, `--surface`, `--elevated`, `--fg`, `--muted`, `--border`, `--primary`.
- Forbidden: hardcoded colors (`bg-white`, `text-black`, `#hex`, `rgb(literal)`).
- Tailwind is layout-only (flex, p-4, gap-2). Colors = CSS variables.
- Dark mode: default ON. Toggle flips `.dark` on root, CSS variables auto-switch.
- Plotly theme sync: always pass `dark=ui.dark_mode().value` to figure builders.
- New CSS classes must define both `:root` and `.dark` values.
```
