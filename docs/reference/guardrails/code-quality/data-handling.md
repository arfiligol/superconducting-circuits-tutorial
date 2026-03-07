---
aliases:
  - "Data Handling Rules"
  - "數據處理規範"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "數據處理規範：原始數據唯讀、metadata DB / TraceStore 分工、Unit of Work、Zarr backend 邊界"
version: v2.0.0
last_updated: 2026-03-08
updated_by: codex
---

# Data Handling

數據處理與儲存規範。

## Directory Structure

```text
data/
├── raw/                        # 原始數據 (唯讀)
│   ├── measurement/
│   ├── circuit_simulation/
│   └── layout_simulation/
├── trace_store/               # Zarr TraceStore（local backend）
└── database.db                # metadata DB（SQLite；未來可換 PostgreSQL）
```

## Rules

### 1. Raw Data is Read-Only

`data/raw/` 下的所有檔案視為不可變：

- 不修改原始檔案
- 不刪除原始檔案
- ingest / import / simulation / post-processing 的輸出不得回寫到 raw tree

### 2. Metadata vs Numeric Payload

資料責任分工必須明確：

- **Metadata DB**
  - `DesignRecord`
  - `TraceRecord`
  - `TraceBatchRecord`
  - `AnalysisRunRecord`
  - `DerivedParameterRecord`
- **TraceStore**
  - trace numeric payload
  - axes arrays
  - sweep ND arrays

!!! important "No large numeric payload in metadata DB"
    大型 trace values 不應作為主要 payload 存入 SQLite/PostgreSQL JSON/BLOB。
    metadata DB 負責索引、lineage、setup、查詢；numeric payload 應進入 `Zarr` TraceStore。

### 3. Use Path / Store Helpers

不得硬編碼 DB 或 TraceStore 路徑。

- metadata DB path 必須由 persistence helper 提供
- TraceStore backend（local / S3-compatible）必須透過抽象層決定

### 4. Database Access (Unit of Work)

所有 metadata DB 存取必須透過 Unit of Work：

```python
from core.shared.persistence import get_unit_of_work

with get_unit_of_work() as uow:
    design = uow.designs.get_by_name("PF6FQ_Q0")
    uow.traces.add(new_trace)
    uow.commit()
```

### 5. TraceStore Access

Trace numeric payload 的讀寫必須經由 TraceStore abstraction，而不是 UI/CLI 直接碰 backend 細節。

允許的 backend 方向：

- local filesystem `Zarr`
- S3-compatible `Zarr`（例如 MinIO / S3 endpoint）

`TraceStoreRef` 必須維持 backend-owned locator contract：

- `backend`：`local_zarr` / `s3_zarr`
- `store_key`：backend-neutral store object key
- `store_uri`：可保留為相容/debug locator，但視為 opaque，不可由 UI/app layer 解析 local layout
- `group_path` / `array_path`：TraceStore 內部群組與 array 定位

### 6. Canonical Trace Contract

- `TraceRecord` 的 canonical 單位是 **one logical observable over axes**
- 可為 1D / 2D / ND
- sweep point 不應自動視為一筆 canonical trace record
- point/slice level materialization 僅可作 projection / cache / export 契約

### 7. Output Locations

| 類型 | 目標位置 |
|------|----------|
| metadata records | metadata DB |
| trace numeric payload | TraceStore (`Zarr`) |
| reports / exports | `data/processed/reports/` 或明確 export path |

## Related

- [Design / Trace Schema](../../data-formats/dataset-record.md)
- [Raw Data Layout](../../data-formats/raw-data-layout.md)
- [Data Storage](../../../explanation/architecture/data-storage.md)

---

## Agent Rule { #agent-rule }

```markdown
## Data Handling
- **Immutable**: `data/raw/` is READ-ONLY.
- **Storage split**:
    - metadata goes to the metadata DB
    - numeric trace payload goes to the TraceStore (`Zarr`)
- **Paths**: NEVER hardcode metadata DB or TraceStore paths/backends.
- **Database**:
    - MUST use Unit of Work for metadata DB operations.
    - NEVER access Session directly in CLI/UI code.
    - MUST call `uow.commit()` explicitly.
- **TraceStore**:
    - MUST go through a TraceStore abstraction.
    - MUST support local `Zarr` as the baseline direction.
    - MUST keep S3-compatible `Zarr` as an extension-safe target.
- **Canonical trace contract**:
    - `TraceRecord` is one logical observable over axes.
    - ND traces are allowed and preferred over point-fragmented canonical storage.
    - point/slice materialization is projection/cache/export, not the only SoT.
- **Flow**:
    - Raw -> Import/Simulation/Post-Processing -> metadata DB + TraceStore -> Characterization / Reports
- **Legacy**:
    - Do not create new JSON-only numeric pipelines.
    - Do not treat SQLite/PostgreSQL JSON/BLOB as the long-term primary numeric trace store.
```
