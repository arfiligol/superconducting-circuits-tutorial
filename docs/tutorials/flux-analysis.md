---
aliases:
- Flux Analysis Workflow
- 磁通分析工作流
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 完整磁通掃描分析流程：原理、操作與解讀
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# Flux Dependence Analysis

本教程將引導你處理 VNA 測量的磁通依賴 (Flux Dependence) 數據。

## 1. Goal & Physics

**目標**：視覺化 JPA 共振頻率隨外加磁通 (Bias Current/Flux) 的變化情形 (Flux Tuning Curve)。

**1. SQUID 調變**

SQUID 的電感 $L_{jun}$ 是磁通 $\Phi$ 的週期函數：

$$ L_{jun}(\Phi) = \frac{\Phi_0}{2\pi I_c |\cos(\pi \Phi/\Phi_0)|} $$

**2. 共振頻率變化**

因為 $f_0 \propto 1/\sqrt{L_{jun}}$，當我們掃描磁通（改變偏壓電流）時，共振頻率會呈現週期性的震盪圖形（通常像拱門形狀）。

> 深入閱讀：[SQUID JPA Basics](../explanation/physics/squid-jpa-basics.md)


## 2. Step-by-Step Analysis

### Step 1: Preprocess

將 VNA 的 TXT 掃描檔匯入資料庫。這通常包含兩個維度：Bias Current (mA) x Frequency (GHz)。

```bash
uv run sc preprocess flux data/raw/measurement/flux_dependence/Biasing_Sweep.txt --dataset-name Meas_JPA_1
```

### Step 2: Full Map Visualization

繪製完整的熱圖 (Heatmap)。

```bash
uv run sc plot flux-dependence Meas_JPA_1
```

**觀察重點**：
- **Periodicity**: 兩個拱門之間的距離對應一個磁通量子 $\Phi_0$。
- **Operating Point**: 通常我們會選擇頻率對磁通變化率 ($\partial f / \partial \Phi$) 較小的區域作為工作點 (Sweet Spot)。

### Step 3: Phase Analysis & Tuning

常常 Amplitude 圖看不太清楚共振點，這時 Phase 圖更重要。

```bash
uv run sc plot flux-dependence --view phase --phase-unit deg --wrap-phase Meas_JPA_1
```

- **為什麼要 Wrap Phase?**
  VNA 測量的相位會隨延遲線長度不斷旋轉。使用 `--wrap-phase` 可以去除電長度 (Electrical Length) 的影響，讓共振點造成的相位突變 ($180^\circ$ jump) 更明顯。
- **物理意義**: 共振點在 Phase 圖上通常表現為顏色劇烈反轉的邊界。

### Step 4: Slicing (Cross-Section)

如果你想看某個特定 Bias 下的 S11 曲線（就像單次 VNA 掃描）：

```bash
uv run sc plot flux-dependence --slice-bias 0.5 Meas_JPA_1
```

程式會額外繪製一張 Bias = 0.5 mA 時的 Amplitude/Phase vs Frequency 線圖。這可以用來提取該工作點的 Q-factor。

## Next Steps

- 如果需要從這些實驗數據反推 $L_s, C$，你需要先將 Bias Current 轉換為 $L_{jun}$，這通常需要先校正磁通週期與 $I_c$。目前此功能尚未完全自動化。
