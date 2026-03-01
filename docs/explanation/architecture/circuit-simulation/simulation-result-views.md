---
aliases:
- Simulation Result Views
- 模擬結果視圖
tags:
- diataxis/explanation
- audience/team
- topic/architecture
- topic/simulation
status: draft
owner: docs-team
audience: team
scope: Circuit Simulation Result 的多視圖契約、控制項與單埠 S11 衍生路徑
version: v0.1.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Simulation Result Views

Circuit Simulation Result 不應只顯示單一圖表。即使目前 Julia bridge 仍以單埠 `S11` 為主，UI 仍需要提供一個可擴充的多視圖框架，讓使用者可以切換觀察角度，而不是被綁死在單一 `|S11|` 圖。

!!! info "設計來源"
    [JosephsonCircuits.jl README](https://github.com/kpobrien/JosephsonCircuits.jl) 的 examples 不只展示單條曲線。實務上會反覆查看 gain、phase、idler 相關 trace、quantum efficiency 與 commutation-relation error。這代表 Result UI 必須先有「view family + selector」的骨架，後續才能自然擴充。

## Current Contract

目前 Python ↔ Julia bridge 只回傳：

- `S11` 的 `real`
- `S11` 的 `imag`

因此目前所有多視圖都以這條單一複數 trace 為基礎展開。

!!! note "這不是最終矩陣能力"
    目前還不是完整的 `S/Y/Z` matrix viewer。現在的目標是先把 **single-trace result exploration** 做正確，並把控制項定義成未來可直接升級到矩陣模型。

## View Families

目前 UI 定義五個 view families：

| Family | 目前資料來源 | 用途 |
|---|---|---|
| `S` | 原始 `S11` | 直接看 scattering 響應 |
| `Gain` | 由 `S11` 導出 | 反射型放大器的 return gain 檢查 |
| `Impedance (Z)` | `S11` + `Z0` | 看輸入阻抗、匹配、共振附近的虛實部 |
| `Admittance (Y)` | `S11` + `Z0` | 看導納、與既有 Y-parameter 分析鏈接軌 |
| `Complex Plane` | `S11` / `Z11` / `Y11` | 直接看複數軌跡 |

## Per-Family Selectors

### S

- `Trace`: 目前固定 `S11`
- `Output Port`: 目前固定 `1`
- `Input Port`: 目前固定 `1`
- `Metric`:
  - `Magnitude (linear)`
  - `Magnitude (dB)`
  - `Phase (deg)`
  - `Real`
  - `Imaginary`

### Gain

- `Trace`: 目前固定 `Return Gain from S11`
- `Output Port`: 目前固定 `1`
- `Input Port`: 目前固定 `1`
- `Metric`:
  - `Gain (dB)`
  - `Gain (linear)`

!!! tip "目前定義"
    目前的 Gain 是 single-port reflection case，直接由 `S11` 導出：`|S11|^2` 與其 dB 表示。未來若 bridge 回傳多埠 `Sij`，再擴充 forward / reverse gain 與指定 port pair。

### Impedance (Z)

- `Trace`: 目前固定 `Z11`
- `Metric`:
  - `Real(Z)`
  - `Imag(Z)`
  - `|Z|`
- `Z0 (Ohm)`:
  - 使用者可指定 reference impedance
  - 由 `Zin = Z0 * (1 + S11) / (1 - S11)` 導出

### Admittance (Y)

- `Trace`: 目前固定 `Y11`
- `Metric`:
  - `Real(Y)`
  - `Imag(Y)`
  - `|Y|`
- `Z0 (Ohm)`:
  - 與 Z family 共用
  - 由 `Yin = 1 / Zin` 導出

### Complex Plane

- `Metric`: 目前固定 `Trajectory`
- `Trace`:
  - `S11`
  - `Z11`
  - `Y11`

!!! note "用途"
    Complex Plane 不是要取代 Smith Chart，而是先提供一個低成本、可立即驗證複數軌跡是否合理的檢查面。

## Why This Shape

這個 UI 形狀刻意把控制項拆成：

1. `View Family`
2. `Metric`
3. `Trace`
4. `Port selectors`
5. `Z0`

原因是未來若 bridge 升級到完整矩陣或更多 diagnostics，只需要：

- 擴增可用 trace 清單（例如 `S21`, `S12`, `Z21`, `Y21`）
- 解鎖 port selectors
- 新增新的 family（例如 `QE`, `CM Error`, `All Idlers`）

而不需要重做整個 Result Card 的互動模式。

## Deferred Scope

下列項目在 README examples 中確實常見，但目前 Julia bridge 尚未回傳，因此 **不在本輪 UI 內**：

- multi-port `Sij` / `Zij` / `Yij`
- all idlers / sideband families
- quantum efficiency (`QE`)
- commutation relation diagnostics (`CM`)

!!! warning "延後不是忽略"
    這些功能已被納入 selector contract 的預留空間；等 bridge 能回傳更多資料，優先順序會是：
    `multi-port S` → `derived Z/Y matrix views` → `QE / CM / idler diagnostics`

## Related

- [Circuit Simulation](index.md)
- [Circuit Schema Live Preview](../design-decisions/circuit-schema-live-preview.md)
