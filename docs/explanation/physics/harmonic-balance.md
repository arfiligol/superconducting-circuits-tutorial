---
aliases:
  - "Harmonic Balance 方法"
tags:
  - diataxis/explanation
  - status/draft
  - topic/physics
---

# Harmonic Balance 方法

Harmonic Balance 是求解非線性電路穩態響應的數值方法。

## 基本概念

對於含有非線性元件（如 Josephson Junction）的電路，時域分析非常耗時。Harmonic Balance 的核心思想是：

1. **假設**：信號可以用有限個諧波表示
2. **轉換**：將非線性方程轉到頻域
3. **求解**：平衡各諧波分量

## 為什麼使用它？

| 方法 | 優點 | 缺點 |
|------|------|------|
| 時域分析 | 直觀 | 非線性電路慢 |
| Harmonic Balance | 穩態快 | 需選諧波數 |

## 在 JosephsonCircuits.jl 中

```julia
sol = hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs)
```

- `Nmodulationharmonics`：調變諧波數
- `Npumpharmonics`：Pump 諧波數

!!! warning "諧波數選擇"
    諧波數越大，計算越精確但越慢。建議從小的值開始（如 10），逐步增加直到結果收斂。

## 延伸閱讀

- [JosephsonCircuits.jl 文件](https://github.com/QICKLab/JosephsonCircuits.jl)
