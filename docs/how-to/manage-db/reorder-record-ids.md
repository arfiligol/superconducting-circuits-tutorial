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
last_updated: 2026-02-10
updated_by: docs-team
---

# 重排 Record IDs (sc-db)

當資料被刪除或需要整理 ID 連續性時，可使用 `auto-reorder` 對指定 model 進行自動重排。
支援兩種排序策略：

- `--sort-by id`：依目前 ID 順序重排（預設）
- `--sort-by name`：依名稱重排（Dataset 依 `name`；DataRecord 依 Dataset 名稱 + 記錄識別欄位）

## Usage

```bash
uv run sc-db <model> auto-reorder [--sort-by id|name]
```

## Examples

### Dataset Records

```bash
uv run sc-db dataset-record auto-reorder
```

```bash
uv run sc-db dataset-record auto-reorder --sort-by name
```

### Data Records

```bash
uv run sc-db data-record auto-reorder
```

```bash
uv run sc-db data-record auto-reorder --sort-by name
```

### Derived Parameters

```bash
uv run sc-db derived-parameter auto-reorder
```

### Tags

```bash
uv run sc-db tag auto-reorder
```

## Notes / Warnings

!!! warning "不可重複 ID"
    `auto-reorder` 會檢查是否產生重複 ID，若偵測到衝突會直接中止並回報錯誤。

## CLI Help（自動生成）

請參考各 model 的 CLI Reference：

- [CLI Reference](../../reference/cli/index.md)
