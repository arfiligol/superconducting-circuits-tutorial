---
aliases:
  - Schematic Netlist 入門
  - Schematic Netlist Getting Started
tags:
  - diataxis/tutorial
  - audience/user
  - topic/simulation
  - topic/visualization
status: draft
owner: docs-team
audience: user
scope: 從零開始在 WebUI Code Editor 寫出第一個可預覽、可模擬的 Schematic Netlist
version: v1.0.0
last_updated: 2026-03-02
updated_by: docs-team
---

# Schematic Netlist 入門

本教學的目標只有一個：

> 讓你第一次在 WebUI Code Editor 中寫出一份合法的 `Schematic Netlist`，並成功看到 `Live Preview` 與 `Simulation` 結果。

完成本篇後，你應該能自己重打一個單埠 LC 電路，而不是只會複製貼上。

!!! tip "成功標準"
    完成本篇後，你必須能解釋：
    - `ports` 是什麼
    - `instances` 是什麼
    - 為什麼 `value_ref` 不能亂寫

## 你將學會什麼

- 在 `/schemas/new` 使用 WebUI Code Editor
- 寫出一份最小可用的 `Schematic Netlist v0.1`
- 用 `Format` 整理格式，並用 `Save Schema` 存檔
- 切到 `/simulation` 跑第一次模擬

## 先備條件

- App 已能正常開啟
- 你知道怎麼進入 `Schemas` 與 `Simulation` 頁面
- 你不需要先理解 JPA / JTWPA；本篇只用最小 LC 電路

如果你想先看正式欄位定義，請查：

- [Schematic Netlist Core](../reference/architecture/schematic-netlist-core.md)
- [Schematic Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Schema Editor](../reference/ui/schema-editor.md)

---

## Step 1. 建立第一份 Schematic Netlist

進入 `/schemas/new`，把編輯器內容改成以下版本：

```python
{
    "schema_version": "0.1",
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
        "L_main": {"default": 10.0, "unit": "nH"},
        "C_main": {"default": 1.0, "unit": "pF"},
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
            "id": "L1",
            "kind": "inductor",
            "pins": ["1", "2"],
            "value_ref": "L_main",
            "role": "signal",
        },
        {
            "id": "C1",
            "kind": "capacitor",
            "pins": ["2", "gnd"],
            "value_ref": "C_main",
            "role": "shunt",
        },
    ],
    "layout": {"direction": "lr", "profile": "generic"},
}
```

!!! note "為什麼這份範例穩定"
    這是最小成功路徑：
    - 一個 `signal` port
    - 一個對地終端電阻
    - 一個串聯電感
    - 一個對地電容

---

## Step 2. 逐欄位理解它在做什麼

### `schema_version`

- 目前固定為 `"0.1"`
- 缺少這個欄位，Validation 會失敗

### `parameters`

- 這是可被 `instances[*].value_ref` 引用的參數表
- 每個參數至少要有：
  - `default`
  - `unit`

### `ports`

- `ports` 定義的是電路的**對外介面**，不是元件本體
- `P1` 代表第一個模擬 port
- `node` 是訊號端
- `ground` 是參考地

### `instances`

- 每一個元件都寫在 `instances`
- `kind` 決定元件類型
- `pins` 決定它接在哪兩個節點上
- `value_ref` 必須指向 `parameters` 裡真的存在的鍵

### `layout`

- `direction = "lr"`：預設由左到右畫主幹
- `profile = "generic"`：先用通用規則，不做特化 profile

---

## Step 3. 按 Format

按下 `Format`。

你應該觀察到：

- 程式碼縮排被整理
- 欄位順序保持穩定
- `Live Preview` 仍然存在，沒有變成錯誤狀態

!!! tip "目前系統的使用習慣"
    - `Format`：整理你的編輯器內容
    - `Save Schema`：保存你目前編輯器中的文字
    - 也就是說，若你喜歡現在的格式，先 `Format` 再 `Save` 是最穩的流程

---

## Step 4. 檢查 Live Preview

此時右側 `Live Preview` 應該能看到：

- 左側一個 `P1`
- 同節點的對地 `R1`
- 一個往右的 `L1`
- 最右側對地的 `C1`

如果你沒有看到這個結構，先不要往下。

### 若看到 `Invalid Circuit Definition`

先檢查：

1. `schema_version` 是否存在
2. `value_ref` 是否真的存在於 `parameters`
3. `pins` 是否都是字串陣列，且長度為 2
4. 是否不小心少了括號或引號

---

## Step 5. 按 Save Schema

按下 `Save Schema`。

成功後：

- 這份 schema 會有固定 ID
- 之後可從 `/schemas/{id}` 再次開啟

### 存檔後再次打開時，你應該看到什麼

- 名稱仍是 `SmokeStableSeriesLC`
- 內容仍是你剛剛保存的格式
- `Live Preview` 會立即恢復

這代表你已經完成了最小可用 schema 的建立。

---

## Step 6. 切到 Simulation 跑第一次模擬

進入 `/simulation`，選擇剛剛的 schema。

保持預設設定即可：

- `Start Freq (GHz)`: `1`
- `Stop Freq (GHz)`: `5`
- `Points`: `301`
- `Source 1`:
  - `Pump Freq (GHz)`: `5`
  - `Source Port`: `1`
  - `Source Current Ip (A)`: `0`
  - `Source Mode`: `1`

按下 `Run Simulation`。

### 預期結果

- `Logs` 出現成功訊息
- `Simulation Results` 出現至少一張 `S11` 圖

!!! note "為什麼 `Ip = 0` 也能跑"
    這代表你現在在跑的是線性小訊號情境。它是學習流程的最佳起點。

---

## 常見錯誤

### 1. `value_ref` 寫錯

現象：

- `Live Preview` 失敗
- 或 `Save Schema` 提示欄位錯誤

原因：

- `instances[*].value_ref` 指到不存在的參數

修法：

- 回到 `parameters` 檢查鍵名是否一致

### 2. 把 `ports` 寫進 `instances`

現象：

- Validation 失敗
- Preview 結構怪異

原因：

- `ports` 與 `instances` 是不同概念

修法：

- `P1` 這類對外 port 一律寫在 `ports`

### 3. `pins` 寫成不是 2 個節點

現象：

- Validation 失敗

修法：

- `v0.1` 目前只支援 2-pin 元件

---

## 自我驗收

請不要複製貼上，自己重打一份以下變形版本：

- 把 `L_main` 改成 `5.0 nH`
- 把 `C_main` 改成 `0.5 pF`
- 名稱改成 `SmokeStableSeriesLC_v2`

如果你能完成以下三件事，就代表本篇成功：

1. 成功保存
2. `Live Preview` 結構仍正確
3. `/simulation` 能成功跑完

---

## 練習題

把 `R1` 拿掉，再按 `Run Simulation`，觀察會發生什麼。

你應該能回答：

- 為什麼系統會報錯
- 為什麼 port 對地電阻在這個教學中是必要的

---

## 下一篇

接著讀：

- [理解 Live Preview：讓 Schemdraw 畫出你預期的結構](schematic-netlist-live-preview.md)

那一篇會教你怎麼寫，Preview 才不會「語法合法但圖很怪」。
