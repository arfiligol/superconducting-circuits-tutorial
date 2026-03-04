---
aliases:
- Dashboard UI
- Pipeline Dashboard
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: Pipeline /dashboard 的資料摘要與 Dataset Metadata 單一編輯入口契約
version: v0.1.0
last_updated: 2026-03-04
updated_by: docs-team
---

# Dashboard

本頁定義 `/dashboard` 的正式 UI 契約。

## Page Sections

1. `Dataset Selector`
2. `Dataset Metadata`
3. `Tagged Core Metrics`

## Dataset Metadata Contract

!!! note "Current behavior（2026-03-04）"
    先前 metadata 編輯入口散落於 `/raw-data` 與 `/simulation`。

!!! important "Contract（Single editable entry）"
    `Dataset Metadata` 的唯一可編輯入口在 `/dashboard`。  
    編輯欄位至少包含：
    - `Target Dataset`（或等價 dataset selector）
    - `Device Type`
    - `Capabilities`
    - `Auto Suggest`
    - `Save Metadata`

!!! warning "Cross-page write boundary"
    `/raw-data` 與 `/simulation` 不可再提供 metadata 寫入互動，只能顯示 read-only summary。

!!! note "Source marker"
    使用者透過 Dashboard 儲存後，`source_meta.dataset_profile.source` 應為 `manual_override`。

## UX Feedback Contract

- 儲存中按鈕需 disabled + loading
- 成功/失敗需有 toast 或同等級回饋
- 儲存成功後，當前 session 需立即反映新 profile（不需重啟）

## Related

- [Raw Data Browser](raw-data-browser.md)
- [Circuit Simulation](circuit-simulation.md)
- [Dataset Record Schema](../data-formats/dataset-record.md)
