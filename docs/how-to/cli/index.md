---
aliases:
  - "CLI 操作指南"
  - "CLI How-to"
tags:
  - diataxis/how-to
  - status/stable
  - audience/user
  - topic/cli
owner: team
status: stable
audience: user
scope: "CLI 指令快速索引與常見任務連結"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# CLI 使用總覽

本指南提供 CLI 指令的快速索引，協助您定位到特定的任務指南。

## 常用指令速查

所有指令皆以 `sc` (Superconducting Circuits) 開頭：

```bash
uv run sc <CATEGORY> <COMMAND>
```

| 任務分類 | 指令前綴 | 相關指南 |
|----------|----------|----------|
| **資料庫管理** | `sc db ...` | [Database Management](../manage-db/index.md) |
| **資料匯入** | `sc preprocess ...` | [Ingest HFSS Admittance](../ingest-data/hfss-admittance.md), [Phase](../ingest-data/hfss-phase.md) |
| **分析與擬合** | `sc analysis ...` | [Fit SQUID Models](../fit-model/squid.md) |
| **繪圖與比較** | `sc plot ...` | [CLI Reference: Plotting](../../reference/cli/index.md) |
| **模擬** | `sc sim ...` | [CLI Reference: Simulation](../../reference/cli/sc-simulate-lc.md) |

## 查看說明

您隨時可以使用 `--help` 查看指令用法：

```bash
uv run sc --help
uv run sc analysis fit lc-squid --help
uv run sc plot admittance --help
uv run sc plot flux-dependence --help
uv run sc plot different-qubit-structure-frequency-comparison-table --help
```

## 相關參考

- [完整 CLI Reference](../../reference/cli/index.md)
