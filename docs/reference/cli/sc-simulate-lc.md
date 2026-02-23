---
aliases:
  - "sc-simulate-lc 指令參考"
  - "sc-simulate-lc CLI Reference"
tags:
  - diataxis/reference
  - status/draft
  - audience/user
  - topic/cli
owner: I-LI CHIU
---

# sc-simulate-lc

使用 LC 模型模擬共振器並計算 S11，適合快速驗證參數趨勢。

## Usage

```bash
uv run sc-simulate-lc --inductance 10 --capacitance 1 --start 0.1 --stop 10
```

## Arguments

| Argument | Description | Default |
|---|---|---|
| - | 無 | - |

## Options

| Option | Description | Default |
|---|---|---|
| `--inductance`, `-L` | Inductance (nH) | `10` |
| `--capacitance`, `-C` | Capacitance (pF) | `1` |
| `--start` | Start frequency (GHz) | `0.1` |
| `--stop` | Stop frequency (GHz) | `10` |
| `--points`, `-n` | Number of points | `1000` |
| `--output`, `-o` | Output JSON path | - |

## Examples

**基本模擬**
```bash
uv run sc-simulate-lc --inductance 8 --capacitance 1.2
```

**輸出結果為 JSON**
```bash
uv run sc-simulate-lc --output data/processed/reports/lc.json
```

## Notes

!!! note "Julia 後端"
    本指令會呼叫 Julia 模擬後端，首次執行可能需要較久初始化時間。

<!-- CLI-HELP-START -->

## CLI Help (自動生成)

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生, 請勿手動修改.

```text
Usage: sc-simulate-lc [OPTIONS]

 Simulate an LC resonator and compute S11.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --inductance   -L      FLOAT    Inductance in nH (default: 10)               │
│                                 [default: 10.0]                              │
│ --capacitance  -C      FLOAT    Capacitance in pF (default: 1)               │
│                                 [default: 1.0]                               │
│ --start                FLOAT    Start frequency in GHz (default: 0.1)        │
│                                 [default: 0.1]                               │
│ --stop                 FLOAT    Stop frequency in GHz (default: 10)          │
│                                 [default: 10.0]                              │
│ --points       -n      INTEGER  Number of frequency points (default: 1000)   │
│                                 [default: 1000]                              │
│ --output       -o      TEXT     Output JSON file path (optional)             │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->

