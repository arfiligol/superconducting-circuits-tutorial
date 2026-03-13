---
aliases:
- Reference
- 技術參考
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/documentation
status: draft
owner: docs-team
audience: team
scope: 技術規格索引，涵蓋 architecture、app、CLI、core、data formats 與開發規範
version: v0.6.0
last_updated: 2026-03-14
updated_by: team
---

# Reference

本區是平台的規格表。

凡是寫在 `Reference` 的定義，都是程式碼、CLI、UI、backend 與核心能力需要對齊的 SoT。

## Categories

| 類別 | 核心聚焦 |
|---|---|
| [Architecture Reference](architecture/index.md) | cross-layer registry、owner boundary 與 parity 對齊 |
| [App / Shared](app/shared/index.md) | workspace collaboration、auth、task runtime、audit logging 等 app-shared semantics |
| [App / Frontend](app/frontend/index.md) | shared shell、definition pages、research workflows |
| [App / Backend](app/backend/index.md) | frontend 與 shared app model 依賴的 backend authority surfaces |
| [CLI Options](cli/index.md) | standalone-first CLI、local runtime 與 command surface |
| [Core](core/index.md) | Python core、Julia wrapper、Julia core 與 Julia plotting |
| [Data Formats](data-formats/index.md) | 數據格式、record schema 與 canonical payload rules |
| [Guardrails](guardrails/index.md) | workspace 開發規範、文件規範與執行驗證規則 |
| [Contributors](contributors.md) | 貢獻者名錄與文件引用依據 |

## Related

- [Explanation](../explanation/index.md) - 核心概念
- [How-to Guides](../how-to/index.md) - 操作指南
