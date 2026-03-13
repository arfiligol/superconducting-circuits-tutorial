---
aliases:
  - "sc circuit-definition 指令參考"
  - "sc circuit-definition CLI Reference"
tags:
  - diataxis/reference
  - audience/user
  - sot/true
  - topic/cli
  - topic/circuit-definition
status: stable
owner: docs-team
audience: user
scope: "`sc circuit-definition` 檢查本地 netlist draft 與已持久化 definition 的指令。"
version: v0.2.0
last_updated: 2026-03-13
updated_by: team
title: sc circuit-definition
---

# sc circuit-definition

用 `sc_core` 檢查 canonical circuit-definition source，或操作 backend 中已持久化的 definition catalog。

!!! info "Command Role"
    這組命令一半對應 `sc_core` canonical inspection，一半對應 backend persisted definition authority。
    因此它同時連到 [Python Core](../core/python-core.md) 與 [Backend / Circuit Definitions](../app/backend/circuit-definitions.md)。

!!! warning "Critical Mutation Rules"
    - `inspect` 必須在 `SOURCE_FILE` 與 `--definition-id` 之間二選一。
    - `delete` 必須加 `--yes` 才會執行。

## Command Map

=== "Browse"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `list` | persisted definition catalog | `--search`, `--sort-by`, `--sort-order` |

=== "Inspect"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `inspect` | 本地 source inspection 或 persisted definition detail | `SOURCE_FILE` 或 `--definition-id` |

=== "Persist"

    | Subcommand | Focus | Key inputs |
    |---|---|---|
    | `create` | 將本地 source 持久化為 definition | `SOURCE_FILE`, `--name` |
    | `update` | 更新 persisted definition | `DEFINITION_ID`, `SOURCE_FILE`, `--name` |
    | `delete` | 刪除 persisted definition | `DEFINITION_ID`, `--yes` |

## Shared Option

| Option | Values | Notes |
|---|---|---|
| `--output` | `text`, `json` | 所有 subcommands 皆支援 |

## Browse Filters

| Option | Values | Default |
|---|---|---|
| `--search` | case-insensitive name substring | `None` |
| `--sort-by` | `created_at`, `name`, `element_count` | `created_at` |
| `--sort-order` | `asc`, `desc` | `desc` |

!!! example "Common Usage"
    ```bash
    uv run sc circuit-definition list --search LC
    uv run sc circuit-definition inspect ./drafts/demo.yaml
    uv run sc circuit-definition inspect --definition-id 18
    uv run sc circuit-definition create ./drafts/demo.yaml --name "Demo LC"
    uv run sc circuit-definition update 18 ./drafts/demo.yaml --name "Demo LC v2"
    uv run sc circuit-definition delete 18 --yes
    ```

## Authority Pairing

| Concern | Authority |
|---|---|
| canonical inspection / preview artifact semantics | [Core / Python Core](../core/python-core.md) |
| persisted definition catalog / CRUD | [Backend / Circuit Definitions](../app/backend/circuit-definitions.md) |

## Related

- [CLI Options](index.md)
- [Python Core](../core/python-core.md)
- [Backend / Circuit Definitions](../app/backend/circuit-definitions.md)
