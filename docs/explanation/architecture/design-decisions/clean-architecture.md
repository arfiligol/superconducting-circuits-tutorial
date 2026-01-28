---
aliases:
  - "Clean Architecture"
  - "分層架構"
tags:
  - diataxis/explanation
  - status/stable
  - topic/architecture
  - topic/cli
  - topic/database
status: stable
owner: docs-team
audience: team
scope: "Clean Architecture 分層與依賴方向說明"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Clean Architecture

本專案採用 **Clean Architecture**，將 CLI、服務、持久化分層，確保核心邏輯可重用且易於測試。

## 分層與責任

### Interface / CLI Layer

- 職責：參數解析、輸出呈現。
- 例：`src/scripts/database/manage_db.py`
- 原則：不放業務邏輯，只呼叫 Service。

### Application / Service Layer

- 職責：業務流程與用例協調。
- 例：`src/core/analysis/application/services/dataset_management.py`
- 原則：回傳 DTO 而非 ORM，避免耦合。

### Persistence Layer

- 職責：資料庫交易與資料存取。
- 例：`SqliteUnitOfWork` + `DatasetRepository`
- 原則：交易在 Unit of Work 管控，Repository 負責查詢與寫入。

## 依賴方向

依賴**只能往內**：

```
CLI → Service → Persistence
```

核心邏輯不能依賴 CLI 或資料庫細節，避免 UI/DB 改動導致業務邏輯被牽動。

## 資料與刪除策略

- Dataset 與 DataRecord 透過 ORM 設定 **cascade**，刪除 Dataset 會連帶移除其 DataRecords。
- Tags 屬於共用標籤，不應與 Dataset 形成父子刪除關係。

## Related

- [Schema Design](schema-design.md) - 資料結構設計
- [Database CLI Reference](../../../reference/cli/sc-db.md) - CLI 指令
