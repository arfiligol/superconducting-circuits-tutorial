---
aliases:
  - "Guardrails: 元件規範 (Component Guidelines)"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails: 元件規範 (Component Guidelines)

本文檔定義了 NiceGUI 元件的使用規則與禁止項目。

## 核心原則

所有 UI 互動元素必須使用 **NiceGUI 內建元件**。禁止使用原生 HTML 元素或瀏覽器原生對話框。

## 允許的元件

### 資料顯示

| 元件 | 用途 | 範例 |
|---|---|---|
| `ui.table` | 資料表格（支援排序、選擇） | 記錄列表 |
| `ui.plotly` | 互動式圖表 | 頻率響應圖、熱力圖 |
| `ui.label` | 文字顯示 | 標題、說明文字 |
| `ui.html` | **僅限靜態內容** | 格式化文字、圖示 |

### 互動控制

| 元件 | 用途 | 範例 |
|---|---|---|
| `ui.button` | 動作按鈕 | 導航、觸發操作 |
| `ui.select` | 下拉選單 | 資料集篩選 |
| `ui.input` | 文字輸入 | 搜尋框 |
| `ui.switch` | 開關 | 深色模式切換 |
| `ui.slider` | 滑桿 | 數值範圍選擇 |

### 佈局

| 元件 | 用途 |
|---|---|
| `ui.column` | 垂直排列 |
| `ui.row` | 水平排列 |
| `ui.card` | 卡片容器（但建議用 `.app-card` class） |
| `ui.separator` | 分隔線 |
| `ui.space` | 彈性空間 |

### 回饋與對話

| 元件 | 用途 |
|---|---|
| `ui.notify` | 快顯通知 (Toast) |
| `ui.dialog` | 對話視窗 |
| `ui.spinner` | 載入指示器 |

## 禁止項目

### ❌ `ui.aggrid`

已知 NiceGUI 內部的 AG Grid JavaScript 封裝存在相容性問題（`TypeError: Cannot read properties of undefined (reading 'withPart')`）。

**替代方案**：使用 `ui.table`，搭配 `rowClick` 事件處理。

```python
# ✅ 正確
grid = ui.table(columns=cols, rows=data, row_key="id")
grid.on("rowClick", handle_click)

# ❌ 禁止
grid = ui.aggrid(options, theme="balham-dark")
```

### ❌ 瀏覽器原生對話框

禁止使用 `alert()`、`confirm()`、`prompt()`。

```python
# ✅ 正確
ui.notify("操作成功", type="positive")

with ui.dialog() as dialog, ui.card():
    ui.label("確認要刪除嗎？")
    ui.button("確認", on_click=lambda: dialog.close())

# ❌ 禁止
ui.run_javascript("alert('操作成功')")
```

### ❌ 原生 HTML 互動元素

禁止透過 `ui.html()` 建立互動控制項。

```python
# ✅ 正確
ui.button("Submit").classes("app-btn-primary")

# ❌ 禁止
ui.html('<button class="app-btn-primary">Submit</button>')
```

### ❌ 行內硬編碼顏色

禁止在 `.style()` 中使用硬編碼顏色值。

```python
# ✅ 正確
ui.label("標題").classes("text-fg")

# ❌ 禁止
ui.label("標題").style("color: white;")
```

## 樣式應用方式

使用 `.classes()` 和 `.props()` 方法套用樣式，不使用 `.style()` 設定顏色。

```python
# ✅ 推薦模式
ui.button("Action", icon="add") \
    .classes("app-btn-primary") \
    .props("flat no-caps")
```

---

## Agent Rule { #agent-rule }

```markdown
## Component Guidelines
- Use NiceGUI components: `ui.table`, `ui.button`, `ui.label`, `ui.select`, `ui.plotly`.
- Forbidden: `ui.aggrid` (known JS compatibility errors); use `ui.table` instead.
- Forbidden: raw HTML for interactive controls (`ui.html('<button>')` etc.).
- Forbidden: `alert()`, `confirm()`, `prompt()` — use `ui.notify()` or `ui.dialog()`.
- Plotly: always render via `ui.plotly(fig)`, never via iframe or raw HTML.
- Style with `.classes()` and `.props()` — never `.style()` with literal colors.
```
