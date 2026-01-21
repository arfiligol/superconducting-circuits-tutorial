# 第一次模擬

讓我們執行第一個超導電路模擬！

## 目標

模擬一個簡單的 LC 共振器，觀察其 S11 響應。

## 電路結構

```
     ┌───┐
Port─┤ L ├─┬─ GND
     └───┘ │
           C
           │
          GND
```

## 程式碼

```julia title="examples/01_simple_lc/lc_resonator.jl"
using JosephsonCircuits

# 定義單位
const nH = 1e-9
const pF = 1e-12
const GHz = 1e9

# 定義電路拓撲
@variables L C R50

circuit = [
    ("P1", "1", "0", 1),      # Port 1
    ("R50", "1", "0", R50),   # 50Ω 阻抗
    ("L", "1", "2", L),       # 電感
    ("C", "2", "0", C),       # 電容
]

# 電路參數
circuitdefs = Dict(
    L => 10nH,
    C => 1pF,
    R50 => 50,
)

# 頻率範圍
ws = 2π * (0.1:0.01:10) * GHz
wp = (2π * 5.0GHz,)
sources = [(mode=(1,), port=1, current=0.0)]

# 執行模擬
sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)

# 提取 S11
S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)
```

## 結果

模擬會得到 S11 參數，顯示 LC 共振器的頻率響應。共振頻率約為：

$$f_0 = \frac{1}{2\pi\sqrt{LC}} \approx 1.59 \text{ GHz}$$

## 下一步

- 👉 [理解 hbsolve](understanding-hbsolve.md) — 深入了解模擬函式
- 👉 [LC 共振器教學](../tutorials/lc-resonator.md) — 更詳細的範例
