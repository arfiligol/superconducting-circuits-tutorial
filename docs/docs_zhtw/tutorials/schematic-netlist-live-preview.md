---
aliases:
  - 理解 Live Preview
  - Schematic Netlist Live Preview Tutorial
tags:
  - diataxis/tutorial
  - audience/user
  - topic/visualization
  - topic/simulation
status: draft
owner: docs-team
audience: user
scope: 理解 WebUI Live Preview 的可預測寫法，讓 Schemdraw 更接近你預期的結構
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# 理解 Live Preview：讓 Schemdraw 畫出你預期的結構

本篇的重點不是再學新語法，而是學會：

> 你該怎麼寫 `Schematic Netlist`，`Live Preview` 才會穩定、可預測、可讀。

如果你只會把元件接起來，但不知道如何讓 Preview 表達你的意圖，後面做 qubit、JPA、JTWPA 時會非常痛苦。

## 你將學會什麼

- 怎麼分辨 `series path` 與 `shunt branch`
- 為什麼「同一對節點的兩個元件」應該被視為平行支路
- `role` 與 `layout.profile` 為什麼會影響圖
- 哪些寫法會讓圖變怪

## 先備條件

- 你已完成 [Schematic Netlist 入門](schematic-netlist-getting-started.md)
- 你已經成功跑過一次最小 LC 模擬

若你要看設計原因，請查：

- [Schematic Netlist Live Preview](../explanation/architecture/design-decisions/circuit-schema-live-preview.md)
- [LayoutPlan 與 Renderer 邊界](../explanation/architecture/circuit-simulation/layout-plan-and-renderer-boundaries.md)

---

## Step 1. 先建立心智模型

目前的 `Live Preview` 並不是「把網路圖自動畫得最好看」。

它的流程是：

1. 解析你的 `Schematic Netlist`
2. 驗證欄位與引用
3. 建立 `CircuitIR`
4. 建立 `LayoutPlan`
5. 用 `Schemdraw` 按順序畫出來

!!! warning "這代表什麼"
    `Schemdraw` 不會替你理解電路語意。你必須用正確的結構、正確的 `pins`、正確的 `role`，讓系統有足夠語意去排版。

---

## Step 2. 學會辨識 series 與 shunt

### Case A：Series 元件

```python
{
    "id": "L1",
    "kind": "inductor",
    "pins": ["1", "2"],
    "value_ref": "L_main",
    "role": "signal",
}
```

這代表：

- `L1` 連接兩個非 ground 節點
- 在視覺上，它會傾向落在主幹上

### Case B：Shunt 元件

```python
{
    "id": "C1",
    "kind": "capacitor",
    "pins": ["2", "gnd"],
    "value_ref": "C_main",
    "role": "shunt",
}
```

這代表：

- `C1` 一端接訊號節點，一端接地
- 在視覺上，它會傾向垂直落地

!!! tip "快速判斷"
    - 非 ground 到非 ground：通常是 series path
    - 非 ground 到 ground：通常是 shunt branch

---

## Step 3. 寫出第一個「可預測」的並聯支路

把你在上一課的電路改成這樣：

```python
{
    "schema_version": "0.1",
    "name": "ParallelBranchDemo",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
        "L_q": {"default": 10.0, "unit": "nH"},
        "C_q": {"default": 1.0, "unit": "pF"},
        "C_g": {"default": 0.1, "unit": "pF"},
    },
    "ports": [
        {
            "id": "P1",
            "node": "1",
            "ground": "gnd",
            "index": 1,
            "role": "signal",
            "side": "left",
        }
    ],
    "instances": [
        {
            "id": "R1",
            "kind": "resistor",
            "pins": ["1", "gnd"],
            "value_ref": "R_port",
            "role": "termination",
        },
        {
            "id": "Lq",
            "kind": "inductor",
            "pins": ["1", "2"],
            "value_ref": "L_q",
            "role": "qubit_branch",
        },
        {
            "id": "Cq",
            "kind": "capacitor",
            "pins": ["1", "2"],
            "value_ref": "C_q",
            "role": "qubit_branch",
        },
        {
            "id": "Cg",
            "kind": "capacitor",
            "pins": ["2", "gnd"],
            "value_ref": "C_g",
            "role": "shunt",
        },
    ],
    "layout": {"direction": "lr", "profile": "qubit_readout"},
}
```

### 你要觀察什麼

- `Lq` 與 `Cq` 是不是都連在同一對節點 `1` 和 `2`
- `Cg` 是否仍是 node `2` 對地支路

### 為什麼這樣寫比較穩定

- `Lq` 與 `Cq` 屬於同一對節點，系統比較容易把它們視為同一組 branch
- `profile = "qubit_readout"` 明確告訴 preview：這不是單純的 generic LC ladder

---

## Step 4. 刻意做錯一次，理解 Preview 為什麼會怪

把 `Cq` 改成：

```python
{
    "id": "Cq",
    "kind": "capacitor",
    "pins": ["2", "gnd"],
    "value_ref": "C_q",
    "role": "shunt",
}
```

此時你就把原本「1 到 2 的並聯支路」，改成了「2 對地支路」。

### 你應該看到的變化

- 圖會明顯不是同一種結構
- `Lq` 不再和 `Cq` 構成同一組 branch

!!! important "這正是本篇的核心"
    Preview 並不是幫你猜「你心裡想的是什麼」。它只會根據你寫出的節點關係與語意做合理推導。

---

## Step 5. 學會使用 `layout.profile`

目前最重要的 profile 有：

- `generic`
- `qubit_readout`
- `jpa`
- `jtwpa`

### 什麼時候先用 `generic`

- 單純 LC
- 基本 readout line
- 還沒出現明確領域語意時

### 什麼時候用 `qubit_readout`

- 有 floating island
- 有 qubit branch
- 有 readout port 與 coupling 元件同時存在

### 什麼時候用 `jpa`

- 有明顯 nonlinear core
- signal path 與 pump/bias path 並存

### 什麼時候用 `jtwpa`

- 有重複 cell
- 你要的是 ladder / transmission-line 結構

---

## 常見錯誤

### 1. 圖合法，但不是你想像的結構

原因：

- `pins` 的節點關係寫錯
- `role` 太模糊
- `profile` 沒選對

修法：

- 先回到節點關係檢查
- 再調整 `role`
- 最後才改 `profile`

### 2. 只改名稱，不改結構

原因：

- 把元件命名成 `L_q`、`C_q` 並不等於系統知道它是 qubit branch

修法：

- 真正影響 Preview 的是：`kind`、`pins`、`role`、`layout`

---

## 自我驗收

請自行寫一個電路，滿足：

1. 一個 `signal` port
2. 一個 `termination` 電阻
3. 一組 `1` 到 `2` 的並聯支路（`L` + `C`）
4. 一個 `2` 對地電容

如果你可以在不看答案的情況下做到，而且能預測 Preview 大致長相，本篇就算通過。

---

## 練習題

試著把 `layout.profile` 在 `generic` 與 `qubit_readout` 間切換，觀察圖的差異。

你應該能回答：

- 為什麼同一份 netlist，在不同 profile 下，圖會有不同的「可讀性」

---

## 下一篇

接著讀：

- [從 Preview 到 Simulation：設定 Sources、Ports、Modes 並讀懂結果](schematic-netlist-simulation.md)
