---
aliases:
  - "LC 共振器模擬"
tags:
  - diataxis/how-to
  - status/draft
  - topic/simulation
---

---
aliases:
  - "LC Resonator Simulation"
  - "LC 共振器模擬"
tags:
  - topic/simulation
  - diataxis/tutorial
status: stable
owner: docs-team
audience: user
scope: "LC 共振器模擬入門教學"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# LC 共振器模擬

本教學介紹如何模擬簡單的 LC 共振器，並分析其 S 參數響應。

## 背景

LC 共振器是超導電路中最基本的元件。其共振頻率由電感 (L) 和電容 (C) 決定：

$$
f_0 = \frac{1}{2\pi\sqrt{LC}}
$$

例如，L = 10 nH 和 C = 1 pF 的共振器，其共振頻率約為 1.59 GHz。

## 方法 A：Python CLI（推薦）

最簡單的方式是使用 CLI 工具 `sc-simulate-lc`：

```bash
# 模擬 L=10nH, C=1pF 的 LC 共振器
# 頻率範圍：0.1 - 5 GHz，100 個點
uv run sc-simulate-lc -L 10 -C 1 --start 0.1 --stop 5 --points 100
```

**預期輸出**：

```
Simulating LC resonator: L=10.0 nH, C=1.0 pF
Frequency range: 0.1 - 5.0 GHz (100 points)

Expected resonance: 1.592 GHz
Simulation complete: 100 points
Resonance found at: X.XXX GHz
```

### 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `-L` | 電感 (nH) | 必填 |
| `-C` | 電容 (pF) | 必填 |
| `--start` | 起始頻率 (GHz) | 0.1 |
| `--stop` | 終止頻率 (GHz) | 10.0 |
| `--points` | 頻率點數 | 100 |
| `--output` | 輸出 JSON 檔案 | 無 |

## 方法 B：Python API

若需要在 Python 腳本中進行更複雜的操作：

```python
from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import FrequencyRange

# 初始化模擬器
simulator = JuliaSimulator()

# 定義頻率範圍
freq_range = FrequencyRange(
    start_ghz=0.1,
    stop_ghz=5.0,
    points=100
)

# 執行模擬
result = simulator.run_lc_simulation(
    inductance_nh=10.0,
    capacitance_pf=1.0,
    freq_range=freq_range
)

# 存取結果
print(f"頻率點: {len(result.frequencies_ghz)}")
print(f"S11 資料: {result.s11_real[:5]}...")  # 前 5 個點
```

詳細 API 說明請參考 [Python API 詳解](python-api.md)。

## 方法 C：原生 Julia

對於熟悉 Julia 的使用者，可以直接使用 JosephsonCircuits.jl：

```julia
using JosephsonCircuits

# 單位
nH, pF, GHz = 1e-9, 1e-12, 1e9

# 定義電路
@variables L C R50
circuit = [
    ("P1", "1", "0", 1),       # Port 1
    ("R50", "1", "0", R50),    # 50Ω 阻抗
    ("L", "1", "2", L),        # 電感
    ("C", "2", "0", C),        # 電容
]

circuitdefs = Dict(
    L => 10nH,
    C => 1pF,
    R50 => 50.0,
)

# 頻率掃描
frequencies = range(0.1, 5, length=100) .* GHz
ws = 2π .* frequencies

# 執行 Harmonic Balance
wp = (2π * 5GHz,)
sources = [(mode=(1,), port=1, current=0.0)]
sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)

# 提取 S11
S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)
```

詳細說明請參考 [原生 Julia 模擬](native-julia.md)。

## 結果解讀

模擬結果包含 S11 參數：

- **S11 振幅**：在共振頻率處出現最小值（深谷）
- **S11 相位**：在共振處發生急劇變化

## 下一步

- [Python API 詳解](python-api.md) - 自定義電路拓撲
- [原生 Julia 模擬](native-julia.md) - 進階模擬技巧
- [CLI Reference](../../reference/cli/sc-simulate-lc.md) - 完整參數說明
