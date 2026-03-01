---
aliases:
  - Schematic Netlist 模擬流程
  - Preview to Simulation
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
status: draft
owner: docs-team
audience: user
scope: 以 WebUI Simulation 頁面為主，教會使用者正確理解 Port、Source、Mode 與 Simulation Result Views
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# 從 Preview 到 Simulation：設定 Sources、Ports、Modes 並讀懂結果

本篇要解決最常見的混淆：

> 為什麼電路有 `P1`，但不一定有對應的 source？

如果這件事沒有搞懂，你在 `Simulation Setup` 裡幾乎一定會配錯。

## 你將學會什麼

- `Port` 與 `Source` 的差別
- `Source Port` 與 `Source Mode` 的差別
- 如何正確設定單 pump、DC + pump、double pump
- 怎麼閱讀 `Simulation Results` 的不同 view

## 先備條件

- 你已完成前兩篇 Tutorial
- 你至少有一份可成功預覽的 schema

請搭配：

- [Circuit Simulation](../reference/ui/circuit-simulation.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [Simulation Result Views](../explanation/architecture/circuit-simulation/simulation-result-views.md)

---

## Step 1. 先釐清 `Port` 不是 `Source`

### `Port`

- 定義在 `ports`
- 它是電路對外的 network boundary
- 它決定的是：這個電路有哪些可觀測 / 可連接的端口

### `Source`

- 設定在 `/simulation` 的 `Applied Sources`
- 它是你在 hbsolve 中真的施加的 drive

!!! important "最重要的心智模型"
    - `Port` 回答的是：電路有哪些對外端口
    - `Source` 回答的是：你現在打算往哪個端口注入哪種 drive

所以：

- 你可以有 `P1`，但目前不在 `P1` 施加任何 source
- 這是正常的，因為 `P1` 仍可作為觀測與散射矩陣端口

---

## Step 2. 理解 `Source Port` 與 `Source Mode`

### `Source Port`

- 這個 source 加在哪一個實體 port 上
- 對應的是 `ports[*].index`

### `Source Mode`

- 這個 source 屬於哪一個 HB mode
- 例子：
  - `0` = DC
  - `1` = 第一個 pump
  - `1,0` = 第一個 pump（double-pump）
  - `0,1` = 第二個 pump（double-pump）

!!! warning "它們不是同一個維度"
    - `Source Port`：空間位置
    - `Source Mode`：頻率 / 諧波通道

---

## Step 3. 跑一個線性 single-port 範例

使用 `SmokeStableSeriesLC`。

設定：

- `Start Freq (GHz)`: `1`
- `Stop Freq (GHz)`: `5`
- `Points`: `301`
- `Source 1`:
  - `Pump Freq (GHz)`: `5`
  - `Source Port`: `1`
  - `Source Current Ip (A)`: `0`
  - `Source Mode`: `1`

按下 `Run Simulation`。

### 你應該看到

- `Logs` 顯示完成
- `Simulation Results` 預設顯示 `S` 類圖

這是最簡單的「線性小訊號」案例。

---

## Step 4. 理解 `DC + pump` 兩個 source 可以在同一個 port

接著用一個有偏壓與 pump 的案例（例如 `SNAIL` 類型）。

你會看到兩個 sources，例如：

- `Source 1`
  - `Source Port`: `2`
  - `Source Mode`: `0`
- `Source 2`
  - `Source Port`: `2`
  - `Source Mode`: `1`

### 這不是錯誤

它代表：

- 兩個 drive 都加在 `port 2`
- 但它們不是同一種 drive
  - 一個是 DC bias
  - 一個是 pump tone

### 為什麼 `P1` 可能沒有 source

因為：

- `P1` 可以是 signal / readout port
- 你要觀察的是 `P1` 的 response
- 但真正施加的大訊號 source 在 `P2`

這是很多 JPA / SNAIL / flux-driven 結構的正常情況。

---

## Step 5. 理解 double-pump

當你有兩個 pump 時，通常會看到兩個 sources：

- `Source 1`: `Source Mode = 1,0`
- `Source 2`: `Source Mode = 0,1`

這表示：

- 有兩個獨立 pump 軸
- 每個 source 只佔其中一個維度

!!! tip "如何判斷有沒有寫對"
    若你新增第二個 source 後，`Source Mode` 仍只有單一數字而沒有展開成雙維度，通常表示你還沒正確進入 double-pump 模式。

---

## Step 6. 學會切換 Simulation Result Views

完成模擬後，`Simulation Results` 不是只有一種圖。

### 目前常用的 View Family

- `S`
- `Gain`
- `Impedance (Z)`
- `Admittance (Y)`
- `Quantum Efficiency (QE)`
- `Commutation (CM)`
- `Complex Plane`

### 先從這三個開始

#### `S`

最適合先看：

- `Magnitude (dB)`
- `Phase (deg)`

#### `Gain`

適合觀察：

- 放大器的增益趨勢

#### `Impedance (Z)`

適合觀察：

- 端口看到的是高阻抗還是低阻抗

---

## Step 7. 正確使用 selectors

### `Output Port` / `Input Port`

- 決定你在看哪一條 `Sij / Zij / Yij`

### `Output Mode` / `Input Mode`

- 決定你看的是哪個 mode / sideband 通道

### `Z0 (Ohm)`

- 影響從反射量推導 `Z` 或 `Y` 的參考阻抗

!!! note "最實用的起點"
    初學時，先把 `Output Mode` / `Input Mode` 都放在零模態，再切 `Output Port` / `Input Port`，最容易建立直覺。

---

## 常見錯誤

### 1. 認為「幾個 Port 就該有幾個 Source」

錯誤原因：

- 把 network port 與 applied source 混為一談

正確理解：

- 一個 port 可以有 0 個、1 個、或多個 sources

### 2. `Source Port` 寫對了，但 `Source Mode` 寫錯

結果：

- HB solve 的語意錯了
- 得到的不是你以為的 drive 設定

修法：

- 先確認這個 source 是 DC、single-pump 還是 double-pump

---

## 自我驗收

你必須能正確回答以下三題：

1. 為什麼 `SNAIL` 可能有兩個 source 都在 `port 2`？
2. 為什麼 `P1` 可以沒有 source？
3. `Source Mode = 0` 與 `Source Mode = 1` 的差別是什麼？

如果答不出來，不要進入下一篇。

---

## 練習題

找一個內建 example：

- 先只看 `S`
- 再切到 `Gain`
- 再切到 `Z`

你應該能說出：

- 這三個 view 在回答的問題有什麼不同

---

## 下一篇

接著讀：

- [設計自己的電路：從需求到可執行的 Schematic Netlist](designing-custom-circuits.md)
