---
aliases:
  - "sc-db CLI Reference"
  - "sc-db 指令參考"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
  - topic/database
owner: I-LI CHIU
---

# sc-db

`sc-db` manages Datasets in the project SQLite database (`data/database.db`). This page documents the CLI specification and outputs.

## Basic Usage

```bash
uv run sc-db <subcommand> [args]
```

## Subcommands

| Subcommand | Purpose | Key Output |
| --- | --- | --- |
| `list` | List all Datasets | Table (ID, Name, Origin, Created At, Tags) |
| `info <identifier>` | Show one Dataset | Origin, Tags, Data Records, Sweep Parameters, Source Files |
| `delete <identifier>` | Delete a Dataset | Interactive confirmation (y/N) |

## Identifier Rules

`<identifier>` can be:

- **ID** (number)
- **Name** (string)

!!! tip "Recommendation"
    If Names may duplicate, use the ID to avoid deleting the wrong Dataset.

## list

List all Datasets.

```bash
uv run sc-db list
```

**Output Columns**

- `ID`: Dataset unique identifier
- `Name`: Dataset name
- `Origin`: Import source (e.g., `measurement`)
- `Created At`: Creation time
- `Tags`: Tags (or `-` if empty)

**Example Output**

```text
All Datasets (3)
┏━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━┓
┃ ID ┃ Name               ┃ Origin      ┃ Created At       ┃ Tags ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━┩
│  3 │ DummyFlux          │ measurement │ 2026-01-28 06:03 │ -    │
│  2 │ Checkpoint3_Single │ measurement │ 2026-01-28 06:01 │ -    │
│  1 │ Checkpoint3_Test   │ measurement │ 2026-01-28 06:01 │ -    │
└────┴────────────────────┴─────────────┴──────────────────┴──────┘
```

## info

Show detailed information for a Dataset.

```bash
uv run sc-db info <identifier>
```

**Output Fields**

- `Origin`
- `Tags`
- `Data Records` (count)
- `Sweep Parameters`
- `Source Files`

**Example Output**

```text
Dataset Details: PF6FQ_Q0_Readout
ID: 4
Origin: measurement
Data Records: 1
Sweep Parameters:
  - L_jun_nH: 0.5
Source Files:
  - .../PF6FQ_Q0_Readout_Im_Y11.csv
```

## delete

Delete a Dataset (and its associated DataRecords).

```bash
uv run sc-db delete <identifier>
```

!!! warning "Warning"
    This operation is irreversible and deletes all DataRecords linked to the Dataset.

**Interactive Confirmation**

- Default is **No** (type `y` to confirm)

## Related

- [How-to: Manage Datasets with sc-db](../../how-to/database/manage-datasets.md)
- [Dataset Record](../data-formats/dataset-record.md)
