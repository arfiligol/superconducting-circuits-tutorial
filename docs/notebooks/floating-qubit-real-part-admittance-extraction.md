---
aliases:
  - "提取 Floating Qubit 看出去的 Real Part Admittance"
  - "Floating Qubit Real Part Admittance Extraction"
tags:
  - diataxis/reference
  - status/draft
---

# 提取 Floating Qubit 看出去的 Real Part Admittance

!!! note "研究筆記（工作中）"
    本頁先記錄目前在 WebUI 可操作且可重現的流程，作為後續 Qubit `T1` 分析前置。
    內容仍是中間版本，尚未定稿。

## 目標

針對 Floating Qubit，提取 differential port 看進去的 `Re(Y_in)`，並可控制是否保留其他 port（例如 readout/drive port）的 shunt termination 影響。

## 問題定義（目前採用）

給定經過模擬與 post-processing 後的多埠導納矩陣 `Y(omega)`，目標是得到單埠等效：

- 目標埠：`dm`（由 Port 1/2 經 Coordinate Transformation 得到）
- 其餘埠：可視需求以 Kron reduction 消除
- `Re(Y_in)`：用於後續 loss / `T1` 估算的關鍵量

## 目前建議流程（UI）

### A. 想保留 Port 3 shunt 對 `dm` 的影響

1. `Port Termination Compensation` 只選 Port 1、Port 2（不要選 Port 3）
2. `Post Processing` 的 `Input Y Source` 選 `PTC Y`
3. 加入 `Coordinate Transformation`（1,2 -> cm/dm）
4. 加入 `Kron Reduction`，最後只保留 `dm`
5. 在 Post-Processed Result View 讀 `Y_dm_dm` 的實部（`Real(Y)`）

### B. 想移除全部 port shunt 再觀察 intrinsic

1. `Port Termination Compensation` 選全部目標 ports
2. `Input Y Source` 選 `PTC Y`
3. 同樣做 CT + Kron，最後取 `Re(Y_dm_dm)`

!!! warning "語意提醒"
    `Simulation Result View` 的 `S` 是 raw solver-native `S`，不套 PTC。
    `Y/Z` 才有 `Raw` / `PTC` 切換。

## 數學表達（後續延伸）

若要在「保留其他埠負載」條件下算單埠輸入導納，可在 `Y` 域用 Schur complement：

```text
Y_in = Y_ii - Y_i,o * (Y_o,o + Y_L)^(-1) * Y_o,i
```

- `i`：目標埠（這裡通常是 `dm`）
- `o`：其餘埠
- `Y_L`：其餘埠外接負載導納（例如 50 Ohm 對應 1/50 S）

## 與 HFSS 比對（目前約定）

Post-Processed Result View 會標示 `HFSS Comparable` 狀態。
通常需同時滿足：

1. PTC 啟用
2. `Input Y Source = PTC Y`
3. 有 Coordinate Transformation step

!!! note "目前限制"
    `HFSS Comparable` 標記目前主要反映流程條件，尚未嚴格驗證「哪些 ports 被補償」是否完全符合你的比對意圖。

## 待補強項目

- [ ] 明確定義 differential normalization（例如 `v_dm` 的縮放）
- [ ] 明確定義 HFSS 對齊用 `Zref`/port reference 規則
- [ ] 在 UI 提供直接計算 `Y_in`（含負載條件）的小工具
- [ ] 將 `Re(Y_in)` 到 `T1` 的連結寫成可重用分析流程（Characterization）
