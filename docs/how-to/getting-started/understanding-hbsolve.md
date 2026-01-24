# 理解 hbsolve

`hbsolve` 是 JosephsonCircuits.jl 的核心函式，使用 **Harmonic Balance** 方法求解非線性電路。

## 函式簽名

```julia
hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs; kwargs...)
```

## 參數說明

| 參數 | 類型 | 說明 |
|------|------|------|
| `ws` | `Vector` | 信號頻率 (rad/s) |
| `wp` | `Tuple` | Pump 頻率 (rad/s) |
| `sources` | `Vector` | 源定義 |
| `Nmodulationharmonics` | `Tuple` | 調變諧波數 |
| `Npumpharmonics` | `Tuple` | Pump 諧波數 |
| `circuit` | `Vector` | 電路網表 |
| `circuitdefs` | `Dict` | 參數值 |

## 電路網表格式

```julia
circuit = [
    ("元件名", "節點+", "節點-", 符號或數值),
    ...
]
```

常見元件：

- `"P1"` — Port（端口）
- `"R"` — 電阻
- `"L"` — 電感
- `"C"` — 電容
- `"LJ"` — Josephson Junction（約瑟夫森結）

## 返回值

`hbsolve` 返回一個 solution 物件，包含：

```julia
sol.linearized.S  # S 參數函式
sol.linearized.Z  # Z 矩陣
sol.linearized.w  # 頻率向量
```

### 提取 S11

```julia
S11 = sol.linearized.S(
    outputmode=(0,),
    outputport=1,
    inputmode=(0,),
    inputport=1,
    freqindex=:
)
```

## 實用技巧

!!! tip "效能優化"
    減少 `Npumpharmonics` 和 `Nmodulationharmonics` 可以加快計算速度，但可能影響精度。

!!! note "使用 returnZ"
    加上 `returnZ=true` 可以同時取得阻抗矩陣，方便計算導納。
