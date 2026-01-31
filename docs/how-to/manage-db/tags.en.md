---
aliases:
  - "Manage Tags"
  - "Manage Tags (sc-db)"
tags:
  - diataxis/how-to
  - status/stable
  - topic/cli
  - topic/database
status: stable
owner: docs-team
audience: user
scope: "Manage tags with sc-db"
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Manage Tags (sc-db)

Use `sc-db tag` to list, create, rename, and delete tags for datasets.

## Usage

```bash
uv run sc-db tag list
```

## Examples

### List tags

```bash
uv run sc-db tag list
```

### Create a tag

```bash
uv run sc-db tag create "NewTag"
```

### Rename a tag

```bash
uv run sc-db tag update "OldTag" "RenamedTag"
```

### Delete a tag

```bash
uv run sc-db tag delete "RenamedTag"
```

## Notes / Warnings

!!! warning "Deletion removes associations"
    Deleting a tag also removes its dataset associations. Confirm downstream workflows no longer rely on it.

## CLI Help (Auto-generated)

See the `CLI Help` section in [CLI Reference: sc-db tag](../../reference/cli/sc-db-tag.md).
