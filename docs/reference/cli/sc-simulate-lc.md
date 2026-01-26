---
aliases:
  - "sc-simulate-lc"
tags:
  - diataxis/reference
  - status/draft
  - topic/cli
---

---
aliases:
  - "sc-simulate-lc"
  - "LC 共振器模擬指令"
tags:
  - topic/cli
  - topic/simulation
status: stable
owner: docs-team
audience: user
scope: "sc-simulate-lc CLI 指令參考"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# sc-simulate-lc

模擬 LC 共振器並計算 S11 參數。

## Synopsis

```bash
sc-simulate-lc -L <inductance> -C <capacitance> [options]
```

## Description

使用 JosephsonCircuits.jl 的 Harmonic Balance 方法模擬簡單 LC 共振器的頻率響應。計算指定頻率範圍內的 S11 散射參數。

## Options

| 選項 | 說明 | 預設值 |
|------|------|--------|
| `-L`, `--inductance` | 電感值 (nH) | **必填** |
| `-C`, `--capacitance` | 電容值 (pF) | **必填** |
| `--start` | 起始頻率 (GHz) | `0.1` |
| `--stop` | 終止頻率 (GHz) | `10.0` |
| `--points` | 頻率點數 | `100` |
| `--output`, `-o` | 輸出 JSON 檔案路徑 | 無（僅印出摘要） |
| `--help` | 顯示說明 | - |

## Examples

### 基本用法

```bash
# 模擬 L=10nH, C=1pF 的共振器
uv run sc-simulate-lc -L 10 -C 1
```

### 指定頻率範圍

```bash
# 0.5 - 3 GHz，50 個點
uv run sc-simulate-lc -L 10 -C 1 --start 0.5 --stop 3 --points 50
```

### 輸出到檔案

```bash
# 儲存結果為 JSON
uv run sc-simulate-lc -L 10 -C 1 -o data/processed/lc_result.json
```

## Output

### 標準輸出

```
Simulating LC resonator: L=10.0 nH, C=1.0 pF
Frequency range: 0.1 - 5.0 GHz (100 points)

Expected resonance: 1.592 GHz
Simulation complete: 100 points
Resonance found at: X.XXX GHz
```

### JSON 輸出格式

```json
{
  "metadata": {
    "inductance_nh": 10.0,
    "capacitance_pf": 1.0,
    "expected_resonance_ghz": 1.592
  },
  "results": {
    "frequencies_ghz": [0.1, 0.15, ...],
    "s11_real": [-0.98, -0.97, ...],
    "s11_imag": [0.01, 0.02, ...]
  }
}
```

## Notes

- 首次執行時會自動安裝 Julia 和 JosephsonCircuits.jl（可能需要數分鐘）
- 後續執行會使用快取，啟動時間約 10-30 秒
- 共振頻率由 S11 振幅最小值判定

## See Also

- [LC 共振器模擬教學](../../how-to/simulation/lc-resonator.md)
- [Python API 詳解](../../how-to/simulation/python-api.md)
- [Harmonic Balance 說明](../../explanation/physics/harmonic-balance.md)
