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

使用 LC 模型模擬共振器並計算 S11。此指令會呼叫 Julia 模擬後端。

## Usage

```bash
uv run sc-simulate-lc --inductance 10 --capacitance 1 --start 0.1 --stop 10
```

## Related

- [LC Resonator Tutorial](../../tutorials/lc-resonator.md)

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

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


