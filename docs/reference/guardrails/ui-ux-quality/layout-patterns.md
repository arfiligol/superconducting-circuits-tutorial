---
aliases:
  - "Guardrails: 佈局規範 (Layout Patterns)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: 佈局規範 (Layout Patterns)

本文檔定義了頁面結構、Shell 架構、間距系統與響應式佈局的規範。

## 間距系統 (Spacing Scale)

本專案採用 **8pt 網格系統**，所有間距值必須為 4 的倍數。

!!! important "資料密集型 Dashboard"
    本應用屬於資料密集型 Dashboard，應採用 **Compact Density**（緊湊密度），
    優先使用較小的間距值以最大化資料呈現空間。

### 間距 Token

| Token | 值 | 用途 |
|---|---|---|
| `gap-1` | 4px | 最小間距 — 同一群組內元素 |
| `gap-2` / `p-2` | 8px | 緊湊間距 — 標籤與內容之間 |
| `gap-3` / `p-3` | 12px | **預設 Card 內距** — 資料卡片 |
| `gap-4` / `p-4` | 16px | **預設區塊間距** — Master-Detail、模組卡片 |
| `gap-6` / `p-6` | 24px | 大間距 — 僅用於頁面級別的分區 |

### 規則

1. **Card 內距**：資料卡片使用 `p-3` (12px)，Dashboard 概覽卡片使用 `p-4` (16px)
2. **區塊間距**：Master-Detail 之間使用 `gap-4` (16px)
3. **標題與內容**：Section title 下方使用 `mb-2` (8px)
4. **頁面內距**：內容區域使用 `px-4 py-3` (水平 16px，垂直 12px)
5. **禁止**：`p-8` (32px) 或更大的間距值用於 Card 或內容區域

### 導航密度

| 屬性 | 值 | 說明 |
|---|---|---|
| Drawer 寬度 | 220px | 比預設 300px 更緊湊 |
| Nav 按鈕 | `dense` prop | 降低行高至 ~32px |
| Nav 內距 | `px-1` | 減少左右留白 |
| 區段標籤間距 | `mb-1` | 緊湊的區段分隔 |

### 表格密度

| 屬性 | 值 | 說明 |
|---|---|---|
| 表格 | `dense` prop | 行高 ~36px（預設 ~48px） |
| 欄位間距 | 16px 最小 | 確保欄位間有足夠分隔 |

## Shell 原則

所有頁面**必須**在 `app_shell()` 內渲染。

```python
from app.layout import app_shell

@ui.page("/my-page")
def my_page():
    def content():
        ui.label("Page Content")

    app_shell(content)()  # ← 所有頁面都走這個 pattern
```

`app_shell` 提供：

- **Header**：標題列（含深色模式切換）
- **Left Drawer**：導航選單
- **Content Area**：主要內容區域（`max-w-7xl mx-auto`）

!!! warning "禁止獨立頁面"
    不可建立不經過 `app_shell()` 的頁面。新頁面需同步更新 `layout.py` 的導航選單。

## Card 排版

內容區塊使用 `.app-card` 包裹，搭配 `.app-section-title` 標題。

```python
with ui.column().classes("app-card w-full p-3"):
    ui.label("區塊標題").classes("app-section-title mb-2")
    # 區塊內容
```

### Card 規格

| 屬性 | 值 |
|---|---|
| 背景 | `rgb(var(--surface))` |
| 邊框 | `1px solid rgb(var(--border))` |
| 圓角 | `0.75rem` (12px) |
| 陰影 | `0 1px 2px 0 rgb(15 23 42 / 0.08)` |

## 響應式規則

使用 Tailwind 的 `lg:` 前綴區分桌面與行動裝置。

```python
# Master-Detail 佈局
with ui.row().classes("w-full gap-4 flex-wrap lg:flex-nowrap"):
    # Master：在行動裝置上佔滿寬度
    with ui.column().classes("w-full lg:w-[45%]"):
        ...

    # Detail：在行動裝置上堆疊在下方
    with ui.column().classes("w-full lg:w-[55%]"):
        ...
```

### 斷點

| 斷點 | 寬度 | 行為 |
|---|---|---|
| 預設 | < 1024px | 單欄堆疊 |
| `lg:` | ≥ 1024px | 多欄並排 |

## 頁面佈局模式

### Master-Detail（資料瀏覽）

左側為資料列表，右側為詳細預覽。

```
┌─────────────┬──────────────────────┐
│  Table      │  Visualization       │
│  (45%)      │  (55%)               │
│             ├──────────────────────┤
│             │  Derived Parameters  │
└─────────────┴──────────────────────┘
```

### Dashboard（儀表板）

統計卡片 + 模組連結的網格佈局。

```
┌──────────┬──────────┬──────────┐
│  Stat 1  │  Stat 2  │  Stat 3  │
├──────────┴──────────┴──────────┤
│  Module Cards (grid)           │
└────────────────────────────────┘
```

## 內容區域規格

| 屬性 | 值 | 說明 |
|---|---|---|
| 最大寬度 | `max-w-7xl` (80rem) | 防止過寬 |
| 水平置中 | `mx-auto` | 居中對齊 |
| 內距 | `px-4 py-3` | 水平 16px / 垂直 12px |
| 元素間距 | `gap-4` | 區塊間 16px |

## 導航管理

新增頁面時需更新 `src/app/layout.py` 中的 Left Drawer：

```python
# layout.py — Left Drawer 內
ui.button(
    "New Page",
    icon="icon_name",
    on_click=lambda: ui.navigate.to("/new-page"),
).classes("w-full justify-start").props("flat no-caps dense")
```

---

## Agent Rule { #agent-rule }

```markdown
## Layout Patterns
- Shell Principle: all pages MUST render inside `app_shell(content_builder)`.
- 8pt Grid: all spacing in multiples of 4px. Use compact density for data-dense views.
- Card data: `p-3` (12px). Dashboard overview: `p-4` (16px). Section title: `mb-2`.
- Content area: `px-4 py-3`, `gap-4`. Forbidden: `p-8` or larger on cards/content.
- Nav drawer: width=220, buttons with `dense` prop.
- Tables: use `dense` prop for compact row height (~36px).
- Responsive: use `lg:` Tailwind prefix for desktop; stack on mobile.
- Max width: content area is `max-w-7xl mx-auto`.
- Navigation: add new pages to the left drawer in `layout.py`.
- Forbidden: standalone pages outside `app_shell()`.
```
