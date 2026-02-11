---
aliases:
  - "CLI Guide"
tags:
  - diataxis/how-to
  - status/stable
  - audience/user
  - topic/cli
owner: team
status: stable
audience: user
scope: "CLI command index and common task links"
version: v1.1.0
last_updated: 2026-01-31
updated_by: team
---

# CLI Overview

This guide provides a quick index of CLI commands to help you find specific task guides.

## Quick Reference

All commands start with `sc` (Superconducting Circuits):

```bash
uv run sc <CATEGORY> <COMMAND>
```

| Category | Command Prefix | Related Guide |
|----------|----------------|---------------|
| **Database** | `sc db ...` | [Database Management](../manage-db/index.md) |
| **Ingestion** | `sc preprocess ...` | [Ingest HFSS Data](../ingest-data/hfss.md) |
| **Analysis** | `sc analysis ...` | [Fit SQUID Models](../fit-model/squid.md) |
| **Plotting & Comparison** | `sc plot ...` | [CLI Reference: Plotting](../../reference/cli/index.en.md) |
| **Simulation** | `sc sim ...` | [CLI Reference: Simulation](../../reference/cli/sc-simulate-lc.en.md) |

## Getting Help

You can always use `--help` to view command usage:

```bash
uv run sc --help
uv run sc analysis fit lc-squid --help
uv run sc plot admittance --help
uv run sc plot flux-dependence --help
uv run sc plot different-qubit-structure-frequency-comparison-table --help
```

## See Also

- [Full CLI Reference](../../reference/cli/index.md)
