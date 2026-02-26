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
- **切換**：`ui.dark_mode().toggle()` 在根元素切換 `.dark` / `body--dark` class
- **自動**：CSS 變數隨 `.dark` class 自動切換，無需 JavaScript

!!! warning "每個元件都必須支援深色模式"
    新增的 CSS class 或 component 必須定義 `:root` 和 `.dark` 兩組值。

## Dark Mode Toggle 架構

### 核心原則

!!! danger "嚴禁在 Dark Mode 切換時觸發 server-side 重繪"
    **禁止** 在 `ui.dark_mode(on_change=...)` 中呼叫 `content_area.refresh()` 或任何會重建 DOM 的操作。
    這會導致：展開的面板收合、表單狀態丟失、使用者體驗嚴重劣化。

### Quasar 原生元件

NiceGUI 元件基於 Quasar，會自動跟隨 Dark Mode 切換（透過 `body--dark` class）。
不需要額外處理。

### 第三方圖表庫（Plotly 等）

Plotly 等非 Quasar 元件不會自動跟隨主題切換。解決方案是使用 **client-side MutationObserver**，
在 `layout.py` 中注入全域 `<script>`，監聽 `<body>` 的 class 變化並呼叫 `Plotly.relayout()`：

```javascript
// 在 layout.py 中透過 ui.add_head_html() 注入
document.addEventListener('DOMContentLoaded', function() {
  const DARK_LAYOUT  = { template: 'plotly_dark',  paper_bgcolor: '...', ... };
  const LIGHT_LAYOUT = { template: 'plotly_white', paper_bgcolor: '...', ... };

  function relayoutAll() {
    requestAnimationFrame(function() {
      const isDark = document.body.classList.contains('body--dark');
      document.querySelectorAll('.js-plotly-plot').forEach(function(el) {
        Plotly.relayout(el, isDark ? DARK_LAYOUT : LIGHT_LAYOUT);
      });
    });
  }

  new MutationObserver(function(mutations) {
    for (const m of mutations) {
      if (m.attributeName === 'class') { relayoutAll(); return; }
    }
  }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
});
```

此模式的優勢：

- ✅ **零 server round-trip**：完全在瀏覽器端執行
- ✅ **零狀態丟失**：展開的面板、Tab、Toggle 全部保持原狀
- ✅ **即時生效**：切換後 Plotly 圖表背景與文字顏色同步更新

### 初始渲染

圖表初始渲染時，使用 `get_plotly_layout()` 設定初始主題（server-side 僅執行一次）：

```python
from core.shared.visualization import get_plotly_layout

# ✅ 正確：初始渲染時指定主題
is_dark = app.storage.user.get("dark_mode", True)
fig.update_layout(**get_plotly_layout(dark=is_dark))
```

`get_plotly_layout(dark=True)` 回傳：

- `template`: `plotly_dark` / `plotly_white`
- `paper_bgcolor`: 對應 `--surface`
- `plot_bgcolor`: 對應 `--bg`
- `font.color`: 對應 `--fg`
- `font.family`: `Inter, Arial, sans-serif`

!!! tip "新增第三方圖表庫時"
    如果引入其他不支援 Quasar Dark Mode 的圖表庫，
    請在 `layout.py` 的 MutationObserver 腳本中新增對應的 relayout 邏輯。

---

## Agent Rule { #agent-rule }

```markdown
## Theming
- Use CSS variable tokens: `--bg`, `--surface`, `--elevated`, `--fg`, `--muted`, `--border`, `--primary`.
- Forbidden: hardcoded colors (`bg-white`, `text-black`, `#hex`, `rgb(literal)`).
- Tailwind is layout-only (flex, p-4, gap-2). Colors = CSS variables.
- Dark mode: default ON. Toggle flips `.dark` / `body--dark` on root, CSS variables auto-switch.
- CRITICAL: NEVER call `content_area.refresh()` or any server-side re-render on dark mode toggle. This destroys UI state.
- Plotly theme sync uses a client-side MutationObserver in `layout.py` that watches `body--dark` and calls `Plotly.relayout()`. No server round-trip.
- Initial chart render: use `get_plotly_layout(dark=app.storage.user.get("dark_mode", True))`.
- New third-party chart libs must be registered in the MutationObserver script in `layout.py`.
- New CSS classes must define both `:root` and `.dark` values.
```
