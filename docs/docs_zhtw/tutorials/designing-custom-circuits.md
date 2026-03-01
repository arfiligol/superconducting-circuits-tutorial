---
aliases:
  - 設計自己的電路
  - Designing Custom Circuits
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
  - topic/visualization
status: draft
owner: docs-team
audience: user
scope: 從需求描述出發，設計可預覽、可模擬、可迭代的自訂 Schematic Netlist
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# 設計自己的電路：從需求到可執行的 Schematic Netlist

本篇是整個系列的最終目標。

當你做完這篇後，你應該可以：

> 根據自己的需求，在 WebUI Code Editor 中自行寫出一份新的 `Schematic Netlist`，並能判斷該如何讓 Preview 與 Simulation 都往正確方向收斂。

## 你將學會什麼

- 從需求文字拆出 `ports / instances / nodes / roles`
- 用正確順序設計 schema，而不是邊試邊猜
- 當圖不對時，知道該改哪一層

## 先備條件

- 你已完成前三篇 Tutorial
- 你已能正確解釋 `Port / Source / Mode`
- 你已知道 `series`、`shunt`、`parallel branch` 的差別

建議同時開著這些頁面：

- [Schematic Netlist Core](../reference/architecture/schematic-netlist-core.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [LayoutPlan 與 Renderer 邊界](../explanation/architecture/circuit-simulation/layout-plan-and-renderer-boundaries.md)

---

## Step 1. 先用自然語言描述需求

不要一開始就寫 JSON。

先把需求寫成一句話：

> 我想要一個單埠 readout line，左側有 50 Ohm port，右側接一個 qubit-like branch，並帶一個對地耦合電容。

這一句話已經暗示了：

- 幾個 port
- 哪條是 signal path
- 哪些是 shunt
- 哪些是同一對節點的 branch

---

## Step 2. 抽出節點

先寫出你需要的節點，而不是先寫元件。

例如：

- `1`：drive / readout node
- `2`：floating island
- `gnd`：ground reference

!!! tip "節點命名建議"
    初學時可以先用 `1`, `2`, `3`。若電路越來越複雜，再改成 `n_drive`, `n_island`, `n_pump` 這種語意名稱。

---

## Step 3. 定義 ports

根據需求，先決定有哪些外部端口：

```python
"ports": [
    {
        "id": "P1",
        "node": "1",
        "ground": "gnd",
        "index": 1,
        "role": "signal",
        "side": "left",
    }
]
```

如果你的需求裡有：

- readout port
- pump port
- flux / bias port

那就應該先在這一層定義清楚。

---

## Step 4. 列出 instances

現在才開始列元件。

### 例：一個 qubit-like branch

```python
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
]
```

這樣寫的意義是：

- `Lq` 與 `Cq` 在同一對節點上，形成平行 branch
- `Cg` 是 node `2` 對地支路

---

## Step 5. 選擇 `layout.profile`

這一步不是可有可無。

### 建議規則

- 基本 LC / readout line：`generic`
- qubit / floating island：`qubit_readout`
- amplifier core：`jpa`
- ladder / transmission line：`jtwpa`

如果你不確定，先從 `generic` 開始，再看圖是否明顯不符合你的結構語意。

---

## Step 6. 進入「觀察 → 修正」迴圈

把 schema 貼到 WebUI Code Editor 後，請按這個順序修：

1. `Format`
2. 看 `Live Preview`
3. 若圖不對，先改結構，不先改數值
4. 結構穩定後，再進 `/simulation`

### 若圖不對，請按這個優先序檢查

1. `pins` 是否真的反映你要的節點關係
2. `role` 是否過於模糊
3. `layout.profile` 是否不適合
4. 是否碰到目前 renderer 的邊界

!!! warning "不要先做的事"
    當 Preview 結構不對時，不要先去亂調參數值。數值通常不會修正錯誤的結構語意。

---

## Step 7. 何時算是「目前系統做不到」

這個系列的目標不是讓你以為系統無所不能，而是讓你知道邊界。

### 可以透過 schema 修正的問題

- series / shunt 寫反
- 同一對節點的 branch 沒有成組
- role 不清楚
- profile 用錯

### 暫時不是單靠 schema 就能完美解決的問題

- 非常複雜的多層交叉結構
- 需要高度客製化的幾何位置
- 你想要的是論文級手工排版，而不是穩定工程圖

這種情況下，你仍應該先讓 schema 語意正確，再決定是否需要進一步優化 renderer。

---

## 三個練習題

### 練習 A：Readout Resonator

需求：

- 一個 `signal` port
- 一個 50 Ohm 終端
- 一個 series `L`
- 一個對地 `C`

目標：

- 這應該是你現在最穩定、最容易成功的類型

### 練習 B：Floating Qubit with Coupling Cap

需求：

- 一個 readout / drive port
- 一個 `1` 到 `2` 的並聯 branch（`Lq + Cq`）
- 一個 `2` 對地小電容

目標：

- 能明確看出 floating island

### 練習 C：簡化版 JPA Core

需求：

- 一個 signal port
- 一個 shunt termination
- 一個中心 nonlinear core（`josephson_junction`）
- 一個 coupling capacitor

目標：

- 學會什麼時候應該切 `profile = "jpa"`

---

## 最終驗收

你完成本系列後，必須能做到以下四件事：

1. 自己寫出一個單埠 readout resonator
2. 自己寫出一個帶 parallel branch 的 qubit-like 結構
3. 正確配置一個 `DC + pump` 的 simulation setup
4. 當 Preview 不理想時，知道應該先改 schema 結構，而不是盲目改數值

若這四件事做不到，請回到前面三篇重新走一次。

---

## Related

- [Schematic Netlist 入門](schematic-netlist-getting-started.md)
- [理解 Live Preview：讓 Schemdraw 畫出你預期的結構](schematic-netlist-live-preview.md)
- [從 Preview 到 Simulation：設定 Sources、Ports、Modes 並讀懂結果](schematic-netlist-simulation.md)
