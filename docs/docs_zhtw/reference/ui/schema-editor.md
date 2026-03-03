---
aliases:
- Schema Editor
- Circuit Netlist Editor
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# Schema Editor

本頁描述下一輪 `/schemas/{id}` 的目標 UI 契約。

!!! warning "文件先行"
    本頁描述的是下一輪程式碼遷移後的目標行為。
    在程式碼完成前，現行 App 仍可能只支援較簡化的 netlist 子集。

## Page Sections

1. `Circuit Definition`
2. `Expanded Netlist Preview`
3. `Component & Unit Reference`

## Circuit Definition

### Editor Model

- 輸入格式：**Circuit Netlist v0.3（Generator-enabled, Component-first）**
- 必要欄位：`name`, `components`, `topology`
- 可選欄位：`parameters`
- 允許文字風格：Python literal（含 tuple、尾逗號）

### Supported Block Items

- `components`：顯式 row 或 `repeat`
- `topology`：顯式 tuple 或 `repeat`
- `parameters`：顯式 row 或 `repeat`（進階可選）

!!! info "Editor 不是腳本執行器"
    Editor 會接受 `repeat`、`symbols`、`series` 與受限模板插值，但不會執行任意 Python。

### Format

- `Format` 會透過 Ruff WebAssembly（`@astral-sh/ruff-wasm`）整理目前輸入
- `Format` 不會展開 `repeat`
- `Format` 不會改寫成其他等價結構

### Save Schema

- `Save Schema` 會保存目前 editor 內的文字
- `Save Schema` 不會自動展開 `repeat`
- `Save Schema` 不會替你插入隱藏欄位

## Expanded Netlist Preview

`Expanded Netlist Preview` 是 **編譯結果預覽**，不是新的 Source of Truth。

它的目標行為是：

- 顯示 `repeat` 展開後的最終 netlist
- 使用與 Simulation 前完全相同的 expansion pipeline
- 保持唯讀，不可直接編輯

!!! important "Source vs Compiled"
    - `Circuit Definition`：你實際編輯與儲存的原始定義（可包含 `repeat`）
    - `Expanded Netlist Preview`：系統展開後、實際會送進模擬器的結果

### 顯示內容

- 一定顯示展開後的 `components`
- 一定顯示展開後的 `topology`
- 若使用了 `parameters`，也顯示展開後的 `parameters`

### 用途

- 檢查 `repeat` 是否正確展開
- 檢查節點編號、元件名稱、`K*` 參照是否一致
- 在進入 Simulation 前就先看到最終輸入長什麼樣

!!! note "儲存規則"
    DB 仍然只儲存原始 `Circuit Definition`。
    `Expanded Netlist Preview` 只是唯讀的編譯結果視圖，不會被當成正式儲存格式。

## 驗證回饋

### Parse 錯誤

- 語法不合法
- tuple 括號不完整
- `repeat` block 結構破損

### Validation 錯誤

- 缺少必要欄位（`name`, `components`, `topology`）
- `components` / `topology` / `parameters` row 型別不正確
- component 缺少 `unit`
- component 同時缺少或同時擁有 `default` / `value_ref`
- `value_ref` 找不到對應 parameter
- 節點不是數字字串
- 使用了 `gnd` 而不是 `0`
- 使用了不支援的模板表達式

### Expansion 錯誤

- `repeat` 的模板展開後產生不合法 row
- `K*` 參照到不存在的電感名稱
- `components` 生成名稱與 `topology` 引用不一致

!!! tip "建議的寫法"
    若電路包含第一段 / 中段 / 最後一段的邊界差異，請：

    1. 手寫 prelude
    2. 用 `repeat` 表達中段
    3. 手寫 epilogue

    不要嘗試把條件邏輯塞進 `repeat`。

## 與 Simulation 的銜接

- Simulation UI 會在執行前展開可出現的 `repeat`
- `Netlist Configuration` 應顯示**與 `Expanded Netlist Preview` 相同 expansion pipeline 的結果**
- Source / pump / harmonics 仍由 Simulation Setup 編輯

!!! note "Live Preview"
    Live Preview 目前維持停用，不在 Schema Editor 顯示。
