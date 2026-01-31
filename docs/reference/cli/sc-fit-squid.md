---
aliases:
- squid-model-fit
- squid-model-with-Ls-fit
- squid-model-with-Ls-fixed-C-fit
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: SQUID LC 模型擬合指令說明
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# sc analysis fit

執行 SQUID LC 模型擬合分析 (原 `sc-fit-squid`)。

## Commands

- `sc analysis fit lc-squid`: 主要擬合指令。支援標準 Ls 擬合、無 Ls、與固定電容模式。

## Usage

```bash
uv run sc analysis fit lc-squid [OPTIONS] [datasets ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `components` | Dataset 名稱或 ID | 內建預設清單 |

## Options

| Option | Description |
|--------|-------------|
| `--modes` | 指定要擬合的模式 (例如 `'Mode 1' 'Mode 2'`) | All |
| `--title` | 自訂圖表標題 | |
| `--ls-min` | $L_s$ 下限 (nH) | 0.0 |
| `--ls-max` | $L_s$ 上限 (nH) | None |
| `--c-min` | $C$ 下限 (pF) | 0.0 |
| `--c-max` | $C$ 上限 (pF) | None |
| `--fixed-c` | 固定電容值 (pF)。`fixed-c` 模式必填 | None |
| `--matplotlib` | 使用 Matplotlib 渲染 (預設: Plotly) | False |

## Examples

**基本擬合 (預設: With Ls)**
```bash
uv run sc analysis fit lc-squid LJPAL658_v1
```

**無 Ls 擬合**
```bash
uv run sc analysis fit lc-squid --no-ls LJPAL658_v1
```

**含串聯電感擬合，並指定 $L_s$ 上限**
```bash
uv run sc analysis fit lc-squid --ls-max 0.2 LJPAL658_v1
```

**固定電容擬合 (C=1.45pF)**
```bash
uv run sc analysis fit lc-squid --fixed-c 1.45 LJPAL658_v1
```

**指定特定 Modes (使用多次參數)**
```bash
uv run sc analysis fit lc-squid --modes 1 --modes 2 LJPAL658_v1
```

## Notes

!!! note "模式自動偵測"
    - 若未指定 `--fixed-c`，預設會嘗試擬合 $L_s$ (Release 模式)。
    - 若指定 `--fixed-c`，則進入固定電容模式。

!!! info "Legacy Alias"
    舊指令 `sc-fit-squid` 仍保留於 `pyproject.toml` 但建議使用新階層指令。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: sc-fit-squid [OPTIONS] [COMPONENTS]...                                  
                                                                                
 Batch analysis of admittance datasets.                                         
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   components      [COMPONENTS]...  Dataset names or IDs.                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --modes                            TEXT   Modes to fit/plot (e.g. 'Mode 1'). │
│                                           [default: Mode 1]                  │
│ --title                            TEXT   Plot title                         │
│                                           [default: Q0 Mode Fits (by         │
│                                           Admittance)]                       │
│ --ls-min                           FLOAT  [default: 0.0]                     │
│ --ls-max                           FLOAT                                     │
│ --c-min                            FLOAT  [default: 0.0]                     │
│ --c-max                            FLOAT                                     │
│ --fixed-c                          FLOAT                                     │
│ --fit-min                          FLOAT  Fit window min (GHz)               │
│                                           [default: 15.0]                    │
│ --fit-max                          FLOAT  Fit window max (GHz)               │
│                                           [default: 30.0]                    │
│ --matplotlib    --no-matplotlib           Use Matplotlib backend             │
│                                           [default: no-matplotlib]           │
│ --help                                    Show this message and exit.        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->




