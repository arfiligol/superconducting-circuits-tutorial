---
aliases:
- Schema Editor
- Circuit Netlist Editor
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /schemas/{id} 頁面的 source-form 編輯、展開預覽與驗證回饋契約
version: v0.2.0
last_updated: 2026-03-06
updated_by: codex
---

# Schema Editor

本頁描述 `/schemas/{id}` 的正式 UI 契約。

## Page Sections

1. `Circuit Definition`
2. `Expanded Netlist Preview`
3. `Component & Unit Reference`

## Circuit Definition

- 編輯格式：Circuit Netlist v0.3（Generator-enabled, Component-first）
- 必填欄位：`name`, `components`, `topology`
- 可選欄位：`parameters`
- 允許 `repeat`、`symbols`、`series` 與受限模板插值

!!! info "Editor 不是腳本執行器"
    不支援任意 Python、巢狀 `repeat`、任意函式呼叫。

### Format / Save 契約

- `Format` 只格式化 source form，不會展開 `repeat`
- `Save Schema` 只儲存 source form，不會儲存展開結果

### Formatting 行為契約

- `Format` 按鈕與快捷鍵必須走同一 formatter pipeline
- 格式化成功後，需以單一 editor state transaction 回寫
- 格式化失敗不得覆蓋原始內容，必須顯示可讀錯誤訊息
- 格式化動作不得隱式觸發 schema migration 或 repeat 展開

!!! note "分類邊界"
    格式化「為何存在」屬於 Explanation，
    本頁只記錄可被測試與驗證的 UI 契約。

### Formatting Failure Strategy

- formatter 初始化失敗：保留 editor 內容，顯示失敗訊息，允許繼續編輯
- 單次 format error：保留原文，不得提交部分覆寫結果
- formatter unavailable 狀態不得改變 `Save Schema` 的 source-form 持久化語意

## Expanded Netlist Preview

`Expanded Netlist Preview` 是唯讀編譯視圖：

- 顯示 expanded `components`
- 顯示 expanded `topology`
- 有 `parameters` 時顯示 expanded `parameters`

!!! important "SoT 邊界"
    Source of Truth 永遠是 `Circuit Definition`（可含 `repeat`）。
    Expanded preview 僅供除錯與執行前確認，不寫回 DB。

## Validation Feedback

必須提供 parse / validation / expansion 三層錯誤回饋，至少涵蓋：

- `components` 缺 `unit`
- `default` / `value_ref` 規則違反
- `value_ref` 無對應 parameter
- node token 不是數字字串
- ground 非 `"0"`
- 展開後引用不一致（例如 `K*` 參照不存在電感）

## Simulation Handoff

`/simulation` 的 `Netlist Configuration` 必須使用同一條 expansion pipeline，
並顯示與本頁 preview 一致的 expanded netlist。

## Related

- [Schema Editor Formatting](../../explanation/architecture/design-decisions/schema-editor-formatting.md)
- [Circuit Netlist Schema](../data-formats/circuit-netlist.md)
- [Circuit Simulation](circuit-simulation.md)
