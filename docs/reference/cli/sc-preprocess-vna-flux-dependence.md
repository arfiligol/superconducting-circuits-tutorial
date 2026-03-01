---
aliases:
- convert-flux-dependence
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: Flux Dependence 轉換指令說明
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# sc preprocess vna flux-dependence

將 VNA 測量的 Flux Dependence TXT 掃描檔案匯入 SQLite Dataset (原 `sc-convert-flux-dependence`)。

此工具會解析 TXT 檔案中的 `Frequency`, `Bias`, `Amplitude`, `Phase` 矩陣。

## Usage

```bash
uv run sc preprocess vna flux-dependence [OPTIONS] [txt ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `txt` | Linköping VNA 格式的 TXT 掃描檔案 | (None) |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dataset-name` | 強制指定 Dataset 名稱 | |
| `--parameter` | 測量參數名稱 (例如 `S11`, `S21`) | `S11` |

## Examples

**基本轉換**
```bash
uv run sc preprocess vna flux-dependence data/raw/measurement/flux_dependence/LJPAL6572_B44D1_FluxDep.txt
```

## Notes

!!! warning "解析限制"
    若資料格式與預期不符，請提供樣本給開發團隊以更新解析器。

<!-- CLI-HELP-START -->

## CLI Help (自動生成)

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生, 請勿手動修改.

```text
Usage: sc-preprocess-vna-flux-dependence [OPTIONS] [TXT]...

 Convert Flux Dependence TXT to SQLite database.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   txt      [TXT]...  Path(s) to Flux Dependence TXT file.                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --dataset-name        TEXT  Override dataset name                                                                    │
│ --tags                TEXT  Comma-separated tags for database record                                                 │
│ --help                      Show this message and exit.                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->
