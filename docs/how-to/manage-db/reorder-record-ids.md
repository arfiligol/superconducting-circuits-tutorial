---
aliases:
  - "重排 Record IDs"
  - "Reorder Record IDs (sc-db)"
tags:
  - diataxis/how-to
  - status/stable
  - topic/cli
  - topic/database
status: stable
owner: docs-team
audience: user
scope: "使用 sc-db 自動重排 Record IDs"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# 重排 Record IDs (sc-db)

當資料被刪除或需要整理 ID 連續性時，可使用 `auto-reorder` 對指定 model 進行自動重排。

## Usage

```bash
uv run sc db <model> auto-reorder
```

## Examples

### Dataset Records

```bash
uv run sc db dataset-record auto-reorder
```

### Data Records

```bash
uv run sc db data-record auto-reorder
```

### Derived Parameters

```bash
uv run sc db derived-parameter auto-reorder
```

### Tags

```bash
uv run sc db tag auto-reorder
```

## Notes / Warnings

!!! warning "不可重複 ID"
    `auto-reorder` 會檢查是否產生重複 ID，若偵測到衝突會直接中止並回報錯誤。

## CLI Help（自動生成）

請參考各 model 的 CLI Reference：

- [sc-db dataset-record](../../reference/cli/sc-db-dataset-record.md)
- [sc-db data-record](../../reference/cli/sc-db-data-record.md)
- [sc-db derived-parameter](../../reference/cli/sc-db-derived-parameter.md)
- [sc-db tag](../../reference/cli/sc-db-tag.md)
