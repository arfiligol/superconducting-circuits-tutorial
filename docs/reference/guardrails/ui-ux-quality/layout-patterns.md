---
aliases:
  - "Guardrails: 佈局規範 (Layout Patterns)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: 佈局規範 (Layout Patterns)

本文檔定義了頁面結構、Shell 架構與響應式佈局的規範。

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
with ui.column().classes("app-card w-full p-4"):
    ui.label("區塊標題").classes("app-section-title mb-4")
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
with ui.row().classes("w-full gap-6 flex-wrap lg:flex-nowrap"):
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
| 內距 | `p-4 md:p-8` | 行動端 / 桌面端 |
| 元素間距 | `gap-6` | 統一間距 |

## 導航管理

新增頁面時需更新 `src/app/layout.py` 中的 Left Drawer：

```python
# layout.py — Left Drawer 內
ui.button(
    "New Page",
    icon="icon_name",
    on_click=lambda: ui.navigate.to("/new-page"),
).classes("w-full justify-start").props("flat no-caps")
```

---

## Agent Rule { #agent-rule }

```markdown
## Layout Patterns
- Shell Principle: all pages MUST render inside `app_shell(content_builder)`.
- Card pattern: wrap content sections in `.app-card` containers.
- Section title: use `.app-section-title` for headings inside cards.
- Responsive: use `lg:` Tailwind prefix for desktop; stack on mobile.
- Max width: content area is `max-w-7xl mx-auto`.
- Navigation: add new pages to the left drawer in `layout.py`.
- Forbidden: standalone pages outside `app_shell()`.
```
