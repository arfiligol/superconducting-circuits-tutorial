---
aliases:
- sc-analysis-resonance-fit
- resonance-fit-scattering
tags:
- audience/team
- diataxis/reference
status: stable
owner: docs-team
audience: team
scope: S 參數共振擬合 CLI 指令參考
version: v0.1.0
last_updated: 2026-02-23
updated_by: docs-team
---

# sc analysis resonance-fit

對資料庫中的 S 參數 Dataset 執行共振頻率 ($f_r$) 與品質因子 ($Q$) 萃取。

支援三種擬合模型，涵蓋從單一共振腔到多模態耦合系統的完整分析流程。

## Subcommands

| Subcommand | 說明 |
|------------|------|
| `scattering` | 對 S 參數（如 S21, S11）執行共振擬合 |

!!! tip "尋找 Admittance (Y 參數) 萃取？"
    如果你需要用 Im(Y)=0 零交叉法萃取共振頻率，請使用 [`sc analysis resonance-extract`](sc-analysis-resonance-extract.md)。

---

## scattering

### Usage

```bash
uv run sc analysis resonance-fit scattering [OPTIONS] DATASET_IDENTIFIER
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `DATASET_IDENTIFIER` | Dataset 名稱或 ID | ✅ |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--parameter, -p` | 要擬合的 S 參數 (`S21`, `S11` 等) | `S21` |
| `--model, -m` | 擬合模型 (`notch`, `transmission`, `vf`) | `notch` |
| `--resonators, -r` | 物理共振結構數量（僅限 `vf` 模型） | `1` |
| `--f-min` | 擬合頻率下界 (GHz) | 無 (使用全頻段) |
| `--f-max` | 擬合頻率上界 (GHz) | 無 (使用全頻段) |
| `--bias-index, -b` | $L_{jun}$ 偏壓切片索引 | `0` |

---

## Models

### `--model notch` (Default)

**適用場景**：Hanger / Notch 型共振腔（共振腔側向耦合到一條 Feedline）。

**特徵**：$S_{21}$ 在共振頻率附近出現一個明顯的 **Dip (凹陷)**。

**數學模型** (CPZM + Baseline)：

$$
\tilde S_{21}(f) = a e^{i\alpha} e^{-2\pi i f \tau} \left( 1 - \frac{Q_l/Q_c^*}{1 + 2i Q_l \frac{f - f_r}{f_r}} \right)
$$

**萃取參數**：$f_r$, $Q_l$, $Q_c$, $Q_i$, $\tau$ (electrical delay)

**範例**：

```bash
uv run sc analysis resonance-fit scattering My_Dataset \
  --parameter S21 --model notch --f-min 6.0 --f-max 7.0
```

**參考文獻**：Probst et al. (2015), Deng et al. (2013), Khalil et al. (2012)

---

### `--model transmission`

**適用場景**：Transmission / Inline 型共振腔（如帶有 Purcell Filter 的獨立傳輸峰）。

**特徵**：$S_{21}$ 在共振頻率附近出現一個明顯的 **Peak (凸起)**。

**數學模型** (Lorentzian Transmission Peak)：

$$
S_{21}^{(T)}(f) = a e^{i\alpha} e^{-2\pi i f \tau} \cdot \frac{1}{1 + 2i Q_l \frac{f - f_r}{f_r}}
$$

**萃取參數**：$f_r$, $Q_l$, $Q_c$, $Q_i$, $\tau$

**範例**：

```bash
uv run sc analysis resonance-fit scattering PF6FQ_Q1_Readout \
  --parameter S21 --model transmission --f-min 5.0 --f-max 7.0
```

---

### `--model vf` (Vector Fitting)

**適用場景**：多模態耦合系統（如 Purcell Filter + 多個 Readout Resonator），或任何在寬頻譜上同時存在多個 Peak 與 Dip 的複雜結構。

**特徵**：一次擬合整段頻譜，自動萃取所有物理共振點。不區分 Peak 或 Dip。

**數學模型** (Pole-Residue Rational Approximation)：

$$
S_{21}(s) \approx \sum_{k=1}^{N_{poles}} \frac{R_k}{s - p_k} + d + s \cdot e, \quad s = 2\pi i f
$$

**演算法**：Sanathanan–Koerner 迭代極點重定位，由 `scikit-rf.VectorFitting` 實作 ([Gustavsen & Semlyen, 1999](https://doi.org/10.1109/61.772353))。

**物理映射**：

| 數學極點 | 物理意義 |
|----------|----------|
| 一對複數共軛極點 ($p = -\sigma \pm j\omega$) | 一個物理共振腔 |
| $\omega / (2\pi)$ | 共振頻率 $f_r$ |
| $\omega / (2\sigma)$ | 負載品質因子 $Q_l$ |
| 實數極點 ($\text{Im}(p) = 0$) | 背景基線 (非物理共振) |

**`--resonators N`**：指定物理共振結構數量。系統自動配置 $2N$ 個複數極點 + 額外的背景實數極點。

!!! tip "我該填多少？"
    如果你的電路是 1 個 Purcell Filter + 5 個 Readout Resonator，就填 `--resonators 6`。

**萃取參數**：多組 $f_{r,k}$, $Q_{l,k}$（以 `Resonator 0`, `Resonator 1`, ... 列出）

**範例**：

```bash
# 單一共振結構
uv run sc analysis resonance-fit scattering PF6FQ_Q1_Readout \
  --parameter S21 --model vf --resonators 1 --f-min 5.0 --f-max 7.0

# 多共振結構：1 Purcell + 5 Readout Resonators
uv run sc analysis resonance-fit scattering My_FullChip_S21 \
  --parameter S21 --model vf --resonators 6
```

---

## Output

### Console

擬合完成後，萃取的參數會即時顯示於終端機：

**`notch` / `transmission` 模型**：
```
Extracted Parameters:
  Resonance Frequency (fr): 6.257850 GHz
  Loaded Q (Ql)         : 23.63
  Internal Q (Qi)       : 60.64
  Coupling Q (Qc)       : 38.72
  Elec. Delay (tau)     : 0.2972 ns
  Model Cost            : 2.1538e+01
```

**`vf` 模型**：
```
Extracted Parameters:
  Resonator 0: fr = 6.252769 GHz, Ql = 23.63
  Resonator 1: fr = 7.413200 GHz, Ql = 152.80
  Model Cost            : 1.1379e-04
```

### Database

所有萃取的參數會自動以 `DerivedParameter` 寫入資料庫：

| 參數名稱 | Method | 說明 |
|----------|--------|------|
| `fr_ghz` | `complex_notch_fit_S21` | Notch 模型的共振頻率 |
| `fr_ghz` | `transmission_fit_S21` | Transmission 模型的共振頻率 |
| `fr_ghz_0`, `fr_ghz_1`, ... | `vector_fit_S21` | VF 模型的各共振頻率 |
| `Ql`, `Qc`, `Qi` | (同上) | 品質因子 |
| `electrical_delay` | (同上) | 電氣延遲 (ns) |

### Visualization

擬合結束後，自動開啟一個互動式 Plotly 圖表：

- **藍色散點**：原始資料 $|S_{21}|$ (dB)
- **紅色實線**：擬合模型曲線
- **綠色虛線**：萃取的共振頻率 $f_r$ 位置

---

## Related

- [S 參數共振頻率萃取理論](../../notebooks/s-parameter-resonance-fit-theory.md)：完整的數學推導與參考文獻
- [SQUID Model Fit](sc-fit-squid.md)：Admittance 擬合 (LC-SQUID 模型)
- [Ingest HFSS Data](../../how-to/ingest-data/index.md)：資料匯入指南
