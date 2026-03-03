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
last_updated: 2026-03-03
updated_by: docs-team
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
