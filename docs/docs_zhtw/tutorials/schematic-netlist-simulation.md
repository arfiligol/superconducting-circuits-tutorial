---
aliases:
- 從 Netlist 到 Simulation
- Netlist to Simulation
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# 從 Netlist 到 Simulation

本篇專注在 `/simulation` 頁：理解 `Port`、`Applied Sources`、`HB Mode`，並讀懂結果圖。

!!! note "先分清兩種視角"
    在進入 Simulation 前，請先建立這個心智模型：

    - Schema Editor 的 `Circuit Definition`：原始 Source Form（可含 `repeat`）
    - Schema Editor 的 `Expanded Netlist Preview`：展開後結果
    - Simulation 的 `Netlist Configuration`：同一條 expansion pipeline 的展開後結果

## 核心心智模型

!!! important "Port 不是 Source"
    - `P1`、`P2` 是電路的 network ports
    - `Applied Sources` 是你這次 hbsolve 真正施加的 drive

所以：

- 電路有兩個 ports，不代表一定有兩個 sources
- 同一個 port 也可以掛多個 sources

## `Source Port` vs `Source Mode`

!!! note "兩者不同"
    - `Source Port`：施加在哪個實體 port
    - `Source Mode`：屬於哪個 HB mode（例如 `0`=DC、`1`=第一個 pump）

### 常見對應

- `0` → `mode=(0,)`
- `1` → `mode=(1,)`
- `1, 0` → `mode=(1, 0)`
- `0, 1` → `mode=(0, 1)`

## `Netlist Configuration` 在看什麼

!!! info "重要"
    `/simulation` 裡的 `Netlist Configuration` 不是單純重印你在 Editor 看到的字。

它的目標行為是：

- 一定顯示展開後的 `components`
- 一定顯示展開後的 `topology`
- 若 schema 使用了 `parameters`，也顯示展開後的 `parameters`

也就是：你看到的是最終送進模擬器的正規化 netlist。

!!! important "它不是儲存格式"
    `Netlist Configuration` 是唯讀的編譯結果視圖。  
    DB 內儲存的仍然是原始 `Circuit Definition`。

這對除錯特別重要，因為你可以直接檢查：

- `repeat` 是否展開成你預期的元件名稱
- 元件名稱是否和 topology 引用一致
- 節點編號是否正確
- 哪些值是 fixed，哪些值是可 sweep parameter

## 基本操作

1. 在頂部選擇 active schema
2. 檢查 `Netlist Configuration`
3. 設定 sweep range
4. 設定 `Applied Sources`
5. 按 `Run Simulation`
6. 在 `Simulation Results` 切換 `S / Gain / Z / Y / QE / CM`

## 常見錯誤

!!! warning "`Source Mode` 不等於 netlist 拓樸"
    `Source Mode` 不寫在 Code Editor 裡。
    它屬於 Simulation Setup，不屬於 netlist。

!!! warning "`repeat` 的錯不在 Simulation Setup"
    如果 `repeat` 展開本身有問題，應先回到 Schema Editor 修正 netlist，而不是先改 Source 設定。

## 自我驗收

你完成本篇後，應該能回答：

- 為什麼 `P1` 可以存在，但沒有任何 Applied Source
- 為什麼同一個 port 可以同時掛 `0`（DC）與 `1`（pump）
- 為什麼 `Netlist Configuration` 對除錯 `repeat` 特別重要
