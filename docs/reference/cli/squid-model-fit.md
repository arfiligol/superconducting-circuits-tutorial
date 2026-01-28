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
last_updated: 2026-01-12
updated_by: docs-team
---

# squid-model-fit

執行 SQUID LC 模型擬合分析。此工具支援三種擬合模式：不含串聯電感 (No Ls)、含串聯電感 (With Ls)、以及固定電容 (Fixed C)。

## Commands

- `squid-model-fit`: 不含串聯電感 ($L_s = 0$)
- `squid-model-with-Ls-fit`: 含串聯電感 ($L_s$ 為擬合參數)
- `squid-model-with-Ls-fixed-C-fit`: 含串聯電感且固定有效電容

## Usage

```bash
uv run squid-model-fit [OPTIONS] [components ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `components` | `data/preprocessed/` 下的組件 ID 或 JSON 路徑 | 內建預設清單 |

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

**基本擬合 (No Ls)**
```bash
uv run squid-model-fit LJPAL658_v1
```

**含串聯電感擬合，並指定 $L_s$ 上限**
```bash
uv run squid-model-with-Ls-fit --ls-max 0.2 LJPAL658_v1
```

**固定電容擬合 (C=1.45pF)**
```bash
uv run squid-model-with-Ls-fixed-C-fit --fixed-c 1.45 LJPAL658_v1
```

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: sc-fit-squid [OPTIONS] [COMPONENTS]...                                  
                                                                                
 Batch analysis of admittance datasets.                                         
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   components      [COMPONENTS]...  Component IDs matching preprocessed       │
│                                    JSONs.                                    │
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



