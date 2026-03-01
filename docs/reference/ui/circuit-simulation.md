---
aliases:
- Circuit Simulation UI
- 電路模擬介面
tags:
- diataxis/reference
- audience/team
- topic/ui
- topic/simulation
status: draft
owner: docs-team
audience: team
scope: Circuit Simulation 頁面的控制項、輸入欄位、Saved Setup 與 Simulation Result 視圖規格
version: v0.1.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Circuit Simulation

本頁描述 `/simulation` 的 UI 組成與目前行為，作為操作與實作對齊的 reference。

## Page Sections

頁面目前依序包含：

1. `Active Schema`
2. `Live Preview`
3. `Simulation Setup`
4. `Simulation Log`
5. `Simulation Results`

## Active Schema

- 用途：切換目前要模擬的 `Circuit Schema`
- 行為：
  - 切換後，`Live Preview` 與 `Simulation Setup` 一起切換
  - 會重新載入該 schema 的 saved setup 與內建 example setup（若存在）

## Live Preview

- 顯示目前 active schema 的電路圖
- 支援：
  - `+`
  - `-`
  - `Reset`
  - 滾輪平移
  - `Ctrl/Cmd + 滾輪` 縮放
  - 拖曳平移
- 目前縮放語意：
  - `100%` = 完整顯示整個電路
  - 最大放大 = `2000%`

## Simulation Setup

### Sweep

- `Start Freq (GHz)`
- `Stop Freq (GHz)`
- `Points`

### Harmonics

- `Nmodulation Harmonics`
- `Npump Harmonics`

### Sources

每個 source card 目前包含：

- `Pump Freq (GHz)`
- `Source Port`
- `Source Current Ip (A)`

支援：

- `Add Source`
- 刪除 source（至少保留一個）

### Advanced hbsolve Options

- `Include DC`
- `Enable 3-Wave Mixing`
- `Enable 4-Wave Mixing`
- `Max Intermod Order (-1 = Inf)`
- `Max Iterations`
- `f_tol`
- `Line Search Switch Tol`
- `alpha_min`

## Saved Setup

- `Saved Setup` 下拉選單：切換當前 schema 的已存設定
- `Save`：將目前 Simulation Setup 存成一筆 saved setup

!!! note "Storage"
    Saved setup 目前存於使用者端 storage（`app.storage.user`），不是資料庫表。

### Built-in Example Setup

對 `JosephsonCircuits Examples: ...` 類型的 schema，系統會自動提供一筆：

- `Official Example`

這筆 setup 會在該 schema 第一次載入時自動被選取。

## Simulation Results

Result card 提供多視圖切換，而不是固定單一圖。

### View Family

- `S`
- `Gain`
- `Impedance (Z)`
- `Admittance (Y)`
- `Complex Plane`

### Shared Controls

- `Metric`
- `Trace`
- `Output Port`
- `Input Port`
- `Z0 (Ohm)`

### Current Selector Behavior

!!! warning "目前仍是 single-port result"
    目前 Julia bridge 只回傳 `S11`。因此：

    - `Output Port` / `Input Port` 目前固定為 `1`
    - `Z11` / `Y11` 由 `S11` 與 `Z0` 推導
    - `Gain` 目前是由 `S11` 推導的 return gain

### S Family

- `Trace`: `S11`
- `Metric`:
  - `Magnitude (linear)`
  - `Magnitude (dB)`
  - `Phase (deg)`
  - `Real`
  - `Imaginary`

### Gain Family

- `Trace`: `Return Gain from S11`
- `Metric`:
  - `Gain (dB)`
  - `Gain (linear)`

### Impedance / Admittance Families

- `Trace`:
  - `Z11`
  - `Y11`
- `Metric`:
  - `Real`
  - `Imag`
  - `Magnitude`
- `Z0 (Ohm)` 可調整 reference impedance

### Complex Plane

- `Metric`: `Trajectory`
- `Trace`:
  - `S11`
  - `Z11`
  - `Y11`

## Save Results to Dataset

目前儲存結果時，會寫入：

- `S11` real
- `S11` imaginary

資料型別為 `s_params`，軸為 `frequency (GHz)`。

## Current Limitations

- 尚未支援 multi-port `Sij`
- 尚未支援原生 `Zij` / `Yij` matrix
- 尚未支援 idlers / `QE` / `CM` diagnostics

這些能力的 UI 外殼已預留，但需要 Julia bridge 先回傳更多資料欄位。
