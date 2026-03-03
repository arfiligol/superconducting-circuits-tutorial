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

1.  **Master 區塊 (列表/表格)**：
    *   在大螢幕上佔據 **45%** 寬度 (`lg:w-[45%]`)。
    *   應設計為可獨立操作，不依賴 Detail 區塊的狀態。

2.  **Detail 區塊 (圖表/詳細資訊)**：
    *   在大螢幕上佔據剩餘的 **55%** 寬度 (`lg:w-[55%]`)。
    *   狀態應根據 Master 區塊的選擇進行連動更新。

3.  **間距**：
    *   Master 與 Detail 之間使用 `gap-6` 分隔。(24px)

4.  **App Card (模組容器)**：
    *   套用 `.app-card` 樣式。
    *   預設使用內部間距 `p-6`（24px）以保持舒適的呼吸空間。
    *   模組標題應置於頂部，套用 `.app-section-title` 與下方 `mb-4` 間隔。
5.  **頁面內距**：內容區域使用 `px-4 py-3` (水平 16px，垂直 12px)
6.  **禁止**：`p-8` (32px) 或更大的間距值用於 Card 或內容區域

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
with ui.column().classes("app-card w-full p-6"):
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
    # Master (45%)
    with ui.column().classes("app-card w-full lg:w-[45%] p-6"):
        ui.label("Item List").classes("app-section-title mb-4")
        # DataTable / List...

    # Detail (55%)
    with ui.column().classes("w-full lg:w-[55%] flex flex-col gap-6"):
        with ui.column().classes("app-card w-full p-6"):
            ui.label("Item Details").classes("app-section-title mb-4")
            # Charts / Params...
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

### Result Family Explorer（結果族檢視）

適用於單一結果批次具有多個 trace family（如 `S / Y / Z / QE`）的情境。

```
┌──────────────────────────────────────────────┐
│ Tabs (family)          Shared controls       │
├──────────────────────────────────────────────┤
│ Add Trace                                       │
├──────────────────────────────────────────────┤
│ Trace Card 1                                    │
├──────────────────────────────────────────────┤
│ Trace Card 2                                    │
├──────────────────────────────────────────────┤
│ Shared Plot (overlay traces)                    │
└──────────────────────────────────────────────┘
```

規則：

1. Tabs 控制資料 family，不應導致重跑 solver。
2. 共享控制項（如 metric / reference value）應集中在 tabs 同列或鄰近列。
3. 每條 trace 的選擇器應封裝成獨立 card，可新增 / 刪除。
4. 所有 trace card 應共同驅動同一張圖，而不是各自產生一張圖。
5. Result View 屬於 quick-inspect / compare surface，可與正式分析頁面重疊，不必強迫移除。

### Large Data Explorer（大量資料探索）

適用於資料筆數可達數千～數萬的頁面（例如 Raw Data / Characterization Trace Selection）。

```
┌──────────────────────────────────────────────┐
│ Filters + Sort + Page Controls               │
├──────────────────────────────────────────────┤
│ Summary Table (current page only)            │
├──────────────────────────────────────────────┤
│ Detail/Plot Panel (selected row only)        │
└──────────────────────────────────────────────┘
```

規則：

1. 控制列（過濾/排序/分頁）應放在表格上方，並固定為同一操作區塊。
2. 表格僅渲染當前頁資料；禁止整批資料一次渲染。
3. 詳細資訊或圖表只在 row selection 後載入，不應在列表刷新時全量重算。
4. 若頁面採 Master-Detail，Master 應維持 `lg:w-[45%]` 左右、Detail 維持 `lg:w-[55%]` 左右，避免單側過寬空白。
5. 任何「全選」預設都需要風險控制（例如 sideband traces 應提供 Base traces quick select）。

## 內容區域規格

| 屬性 | 值 | 說明 |
|---|---|---|
| 最大寬度 | `w-full` | 允許完整利用螢幕寬度 |
| 內距 | `px-4 py-3` | 水平 16px / 垂直 12px |
| 元素間距 | `gap-6` | 區塊間 24px |

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
- Spacing:
    *   Use 8pt grid system.
    *   Card internal padding is `p-6` for spacious feel.
    *   Block gaps are `gap-6`.
    *   Title margins are `mb-4`.
    *   DO NOT use arbitrary margins like `mt-3` or `px-5`.
- Content area: `w-full px-4 py-3`, `gap-6`. Forbidden: `max-w-*` on app_shell, allow full width.
- Nav drawer: width=220, buttons with `dense` prop.
- Master/Detail proportions: tables should usually be `w-[45%]`, visualizations `w-[55%]`.
- Responsive: use `lg:` Tailwind prefix for desktop; stack on mobile.
- Navigation: add new pages to the left drawer in `layout.py`.
- Result Family Explorer: when one result bundle has multiple trace families, prefer tabs + shared controls + trace cards + one shared plot. Changing selectors inside this explorer must not trigger a rerun by itself.
- Large Data Explorer: for record-heavy pages, keep controls above table, render current page only, and load detail payload lazily by row selection.
- Forbidden: standalone pages outside `app_shell()`.
```
