---
aliases:
- sc-analysis-resonance-extract
tags:
- audience/team
- diataxis/reference
status: stable
owner: docs-team
audience: team
scope: 直接萃取共振頻率 CLI 指令參考（非擬合方法）
version: v0.1.0
last_updated: 2026-02-23
updated_by: docs-team
---

# sc analysis resonance-extract

從資料庫中的 Dataset 直接**萃取 (Extract)** 共振頻率，不經過曲線擬合 (Curve Fitting)。

!!! info "與 `resonance-fit` 的差異"
    | | `resonance-fit` | `resonance-extract` |
    |---|---|---|
    | **方法** | 非線性最小平方法 / Pole-Residue 迭代 | 零交叉 / Peak 偵測 |
    | **輸入** | S-Parameter (Scattering Matrix) | Y-Parameter (Admittance) |
    | **輸出** | $f_r$, $Q_l$, $Q_c$, $Q_i$, $\tau$ | $f_r$ (各 Mode) |
    | **適用場景** | 需要完整的 Q 因子分解 | 快速定位共振頻率、SQUID 前置分析 |

## Subcommands

| Subcommand | 說明 |
|------------|------|
| `admittance` | 用 Im(Y)=0 零交叉法萃取共振頻率 |

---

## admittance

### Usage

```bash
uv run sc analysis resonance-extract admittance [OPTIONS] DATASET_IDENTIFIER
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `DATASET_IDENTIFIER` | Dataset 名稱或 ID | ✅ |

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--bias-index, -b` | $L_{jun}$ 偏壓切片索引（`-1` = 全部切片） | `-1` |

---

## 原理

### Im(Y) = 0 零交叉法

對於一個 LC 共振腔，其導納 (Admittance) 的虛部為：

$$
\text{Im}(Y) = \omega C - \frac{1}{\omega L}
$$

在共振頻率 $f_r = \frac{1}{2\pi\sqrt{LC}}$ 處，$\text{Im}(Y) = 0$。

本工具掃描整個頻率軸，找出所有 $\text{Im}(Y)$ **從正變負（或從負變正）的交叉點**，透過相鄰兩點的線性內插 (Linear Interpolation) 精確定位零交叉的頻率。

!!! note "多模態 (Multi-Mode)"
    如果 Dataset 包含 `L_jun` 偏壓軸（代表不同的 SQUID 磁通偏壓點），系統會自動對每個偏壓值分別執行零交叉搜尋。每個 $L_{jun}$ 值可能找到不同數量的 Mode（零交叉點），回傳為一張表格。

---

## Output

### Console

```
Extraction completed successfully!

         Im(Y)=0 Zero-Crossing Resonances
┏━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ L_jun    ┃ Mode 1      ┃ Mode 2      ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 0.100000 │ 6.257850    │ 18.652100   │
│ 0.200000 │ 5.812340    │ 17.943200   │
│ 0.300000 │ 5.365870    │ 17.234500   │
└──────────┴─────────────┴─────────────┘
```

---

## Examples

**萃取全部偏壓模態**：
```bash
uv run sc analysis resonance-extract admittance LJPAL658_v1
```

**萃取特定偏壓索引**：
```bash
uv run sc analysis resonance-extract admittance LJPAL658_v1 --bias-index 0
```

---

## Related

- [Resonance Fitting (S-Parameter)](sc-analysis-resonance-fit.md)：適用於需要完整 Q 因子的 S 參數分析
- [SQUID Model Fit](sc-fit-squid.md)：使用萃取的模態頻率做後續的 LC-SQUID 參數擬合
- [S 參數共振頻率萃取理論](../../notebooks/s-parameter-resonance-fit-theory.md)：完整的數學推導
