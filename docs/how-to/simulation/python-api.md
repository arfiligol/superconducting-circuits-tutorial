---
aliases:
  - "Python API 詳解"
tags:
  - diataxis/how-to
  - status/draft
  - topic/simulation
---

---
aliases:
  - "Python Simulation API"
  - "Python 模擬 API"
tags:
  - topic/simulation
  - topic/python
  - topic/api
status: stable
owner: docs-team
audience: user
scope: "Python 模擬 API 使用指南"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Python API 詳解

本教學說明如何在 Python 腳本中使用模擬 API 進行電路模擬。

## 前置需求

1. **uv 環境已安裝**：`uv sync`
2. **Julia 依賴**：首次執行時會自動透過 `juliapkg` 安裝 JosephsonCircuits.jl

## 基本使用

### 匯入模組

```python
from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import (
    FrequencyRange,
    SimulationResult,
    CircuitDefinition,
    ComponentValue,
)
```

### 初始化模擬器

```python
# 模擬器會在首次呼叫時延遲初始化 Julia 環境
simulator = JuliaSimulator()
```

!!! note
    首次初始化可能需要數十秒，因為需要載入 Julia 和 JosephsonCircuits.jl。

## LC 共振器模擬

最簡單的模擬方式：

```python
from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import FrequencyRange

simulator = JuliaSimulator()

# 定義頻率範圍
freq_range = FrequencyRange(
    start_ghz=0.1,
    stop_ghz=5.0,
    points=100
)

# 執行 LC 模擬
result = simulator.run_lc_simulation(
    inductance_nh=10.0,   # 電感 (nH)
    capacitance_pf=1.0,   # 電容 (pF)
    freq_range=freq_range
)
```

## 結果處理

`SimulationResult` 包含以下屬性：

```python
# 頻率陣列 (GHz)
frequencies = result.frequencies_ghz  # List[float]

# S11 參數
s11_real = result.s11_real  # List[float]
s11_imag = result.s11_imag  # List[float]

# 計算振幅和相位
import numpy as np

s11_complex = np.array(s11_real) + 1j * np.array(s11_imag)
s11_mag = np.abs(s11_complex)
s11_phase = np.angle(s11_complex)

# 找到共振頻率（S11 最小值）
resonance_idx = np.argmin(s11_mag)
resonance_freq = frequencies[resonance_idx]
print(f"共振頻率: {resonance_freq:.3f} GHz")
```

## 自定義電路

對於更複雜的電路拓撲，使用 `run_hbsolve` 方法：

```python
from core.simulation.domain.circuit import (
    CircuitDefinition,
    ComponentValue,
    FrequencyRange,
    SimulationConfig,
)

# 定義電路元件
components = [
    ComponentValue(name="L1", value=10.0, unit="nH"),
    ComponentValue(name="C1", value=1.0, unit="pF"),
    ComponentValue(name="R50", value=50.0, unit="Ohm"),
]

# 定義拓撲 (name, node1, node2, value_key)
topology = [
    ("P1", "1", "0", 1),       # Port
    ("R50", "1", "0", "R50"),  # 端接阻抗
    ("L1", "1", "2", "L1"),    # 電感
    ("C1", "2", "0", "C1"),    # 電容
]

# 建立電路定義
circuit = CircuitDefinition(
    name="Custom LC Resonator",
    topology=topology,
    components=components
)

# 頻率範圍
freq_range = FrequencyRange(start_ghz=0.1, stop_ghz=5.0, points=100)

# 模擬設定（使用預設值）
config = SimulationConfig()

# 執行模擬
result = simulator.run_hbsolve(circuit, freq_range, config)
```

## 支援的單位

`ComponentValue` 支援以下單位：

| 類型 | 支援單位 |
|------|----------|
| 電感 | `H`, `mH`, `uH`, `nH`, `pH` |
| 電容 | `F`, `mF`, `uF`, `nF`, `pF`, `fF` |
| 電阻 | `Ohm`, `kOhm`, `MOhm` |

## 錯誤處理

```python
try:
    result = simulator.run_lc_simulation(
        inductance_nh=10.0,
        capacitance_pf=1.0,
        freq_range=freq_range
    )
except ImportError as e:
    print("juliacall 未安裝，請執行: uv add juliacall")
except Exception as e:
    print(f"模擬錯誤: {e}")
```

## 相關資源

- [LC 共振器模擬](lc-resonator.md) - 入門教學
- [原生 Julia 模擬](native-julia.md) - 進階技巧
- [擴充 Julia 函數](../extend/extend-julia-functions.md) - 新增模擬類型
