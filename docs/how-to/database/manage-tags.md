---
aliases:
  - "管理 Tags"
  - "Manage Tags (sc-db)"
tags:
  - diataxis/how-to
  - status/stable
  - topic/cli
  - topic/database
status: stable
owner: docs-team
audience: user
scope: "使用 sc-db 管理 Tags"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# 管理 Tags (sc-db)

當你需要整理或統一資料集標籤時，使用 `sc-db tag` 可以快速新增、改名與刪除 Tags。

## Usage

```bash
uv run sc-db tag list
```

## Examples

### 列出所有 Tags

```bash
uv run sc-db tag list
```

### 新增 Tag

```bash
uv run sc-db tag create "NewTag"
```

### 重新命名 Tag

```bash
uv run sc-db tag update "OldTag" "RenamedTag"
```

### 刪除 Tag

```bash
uv run sc-db tag delete "RenamedTag"
```

## Notes / Warnings

!!! warning "刪除會影響關聯"
    刪除 Tag 會同步移除與 Dataset 的關聯。請先確認下游分析不再依賴該標籤。

## CLI Help（自動生成）

請參考 [CLI Reference: sc-db tag](../../reference/cli/sc-db-tag.md) 的 `CLI Help` 區塊。
