---
aliases:
  - "Circuit Netlist Schema"
  - "電路 Netlist 規格"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/simulation
status: stable
owner: docs-team
audience: team
scope: "CircuitDefinition Netlist 規格：value_ref、parameters、Sweep 覆寫規則"
version: v1.2.0
last_updated: 2026-03-05
updated_by: codex
---

# Circuit Netlist Schema

`CircuitDefinition` 是 UI Schema Editor 與模擬流程共用的 netlist 格式。

## Structure

- `name: str`
- `parameters: dict[str, ParameterSpec]`
- `topology: list[(element_name, node1, node2, value_ref_or_port_index)]`

其中 `ParameterSpec`：

| Key | Type | Required | 說明 |
|---|---|---|---|
| `default` | `float` | ✅ | 預設數值（非 Sweep 時使用） |
| `unit` | `str` | ✅ | 單位字串 |
| `sweepable` | `bool` | ❌ | 是否可被 Sweep UI 選取（預設 `true`） |

---

## Core Rules (Normative)

1. Port 元件（`P*`）在 topology 第 4 欄使用整數 port index（例如 `1`）。
2. 非 Port 元件在 topology 第 4 欄必須使用 `value_ref: str`（變數名）。
3. 每個非 Port `value_ref` 必須存在於 `parameters`。
4. 每個 `parameters[value_ref]` 必須包含 `default` 與 `unit`。
5. Sweep 只覆寫 `parameters[*].default` 的執行值，不改 topology 結構。
6. `K*` mutual coupling row 的第 2/3 欄必須是 inductor element name（不是 node）。
7. `K*` mutual coupling row 的第 4 欄必須引用一個已存在的 coupling component 名稱。

---

## Topology Item Format

`(element_name, node1, node2, value_ref_or_port_index)`

| Position | Type | 說明 |
|---|---|---|
| `element_name` | `str` | 元件名（用前綴推斷符號） |
| `node1` | `str` | 端點節點 1 |
| `node2` | `str` | 端點節點 2 |
| `value_ref_or_port_index` | `int \| str` | Port 用整數；其餘使用參數引用鍵（例如 `Cc`, `Lj`） |

---

## Component 與 Unit 規則

| Component | Name Prefix | Allowed Units | Example | Notes |
|---|---|---|---|---|
| Port | `P*` | `-` | `("P1", "1", "0", 1)` | Port index 用整數；不需要 `parameters` |
| Resistor | `R*` | `Ohm`, `kOhm`, `MOhm` | `("R1", "1", "0", "R_port")` | 建議每個 Port 有 shunt resistor（常見 `50 Ohm`） |
| Inductor | `L*` | `H`, `mH`, `uH`, `nH`, `pH` | `("L1", "1", "2", "Lj")` | `Lj*` 另作 Josephson Junction |
| Capacitor | `C*` | `F`, `mF`, `uF`, `nF`, `pF`, `fF` | `("C1", "1", "2", "Cc")` | 可多元件共用同一 `value_ref` |
| Josephson Junction | `Lj*` | `H`, `mH`, `uH`, `nH`, `pH` | `("Lj1", "2", "0", "Lj")` | Preview 會以 junction symbol 顯示 |
| Mutual Coupling | `K*` | `-`（建議無因次） | `("K1", "L1", "L2", "Kc")` | 第 2/3 欄是 inductor element name；第 4 欄是 coupling component 參照 |

!!! note "大小寫規則"
    Unit 解析目前支援大小寫不敏感（例如 `ohm` / `Ohm` 皆可），但文件與範例建議使用表格中的 canonical 寫法。

!!! note "Ground node"
    ground token 只有字串 `0`。`gnd` / `GND` 皆不支援。

---

## Minimal Runnable Example

```python
{
    "name": "SmokeStableSeriesLC",
    "parameters": {
        "R_port": {"default": 50.0, "unit": "Ohm"},
        "Lj": {"default": 1000.0, "unit": "pH"},
        "Cc": {"default": 100.0, "unit": "fF"},
        "Cj": {"default": 1000.0, "unit": "fF"}
    },
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R_port"),
        ("C1", "1", "2", "Cc"),
        ("Lj1", "2", "0", "Lj"),
        ("C2", "2", "0", "Cj")
    ]
}
```

---

## Sweep Rules

- Sweep 的設計目標是「覆寫參數值」，不是改 topology。
- 單參數 Sweep：對一個 `value_ref` 建立值序列。
- 多參數 Sweep：對多個 `value_ref` 建立 Cartesian product 或成對掃描。
- 未被 Sweep 覆寫的變數，使用 `parameters[*].default`。

!!! note "Bias/source sweep boundary"
    Source/bias（例如 `sources[1].current_amp`）屬於 `Simulation Setup` 契約，
    不屬於 netlist data format。本文件只規範 netlist 參數層的 sweep 語義。

---

## Live Preview Binding Rule

Live Preview 顯示值時，必須用 topology 的第 4 欄 `value_ref` 查 `parameters[value_ref]`。

例如：

- `("C2", "2", "0", "Cj")` 應顯示 `C2` 與 `Cj` 的 default 值
- 不應使用 `element_name == C2` 去找 `parameters["C2"]`

---

## 常見錯誤對照

| 訊息片段 | 可能原因 | 建議 |
|---|---|---|
| `topology references undefined parameter` | topology 第 4 欄引用了不存在的 `value_ref` | 補上 `parameters[value_ref]` |
| `non-port topology entries must use string value_ref` | 非 Port 元件用了整數或其他非字串 value_ref | 改成參數鍵字串 |
| `parameter default missing` | `parameters[*].default` 遺漏 | 為該參數補預設值 |
| `Ports without resistors detected` | Port 沒有阻抗定義 | 加入對應 `R*` 元件（常見 `R50`） |
| `SingularException` | 拓樸連接或參數組合導致矩陣奇異 | 檢查節點連通性、元件數值與單位 |

## Runtime Contract Snapshot

### Input

- Source-form netlist（Schema Editor 儲存內容）
- 可選 Simulation Setup 覆寫（例如 sweep）

### Output

- Expanded/validated netlist（僅執行期視圖，不回寫 DB）
- 明確 validation failure（可對應到欄位與規則）

### Invariants

1. ground token 只允許字串 `0`
2. `P*` 第 4 欄必須是整數 port index
3. 非 `P*` 第 4 欄必須是參數引用（`value_ref`）
4. `K*` 第 2/3 欄必須是 inductor element 名稱，第 4 欄是 coupling component 引用

### Failure Modes

- undefined parameter reference
- invalid node token / invalid ground token
- `K*` row 參照不存在 inductor/component
- 拓樸造成奇異矩陣（數值層）

## Code Reference Map

- Parser / validator:
  - [`circuit.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/simulation/domain/circuit.py)
- Simulation page expanded preview:
  - [`simulation/__init__.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/simulation/__init__.py)
- Schema editor source/preview binding:
  - [`schema_editor.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/schema_editor.py)

## Runtime Parity Checklist

release 前至少確認：

1. Data Format 規格與 parser 規則一致（`P*` / `K*` / ground token）
2. Schema Editor Expanded Preview 與 Simulation Netlist Configuration 使用同一 expansion pipeline
3. DB 僅保存 source-form，不保存 expanded-form
4. error message 可對應到本頁規範條目，不依賴隱式舊相容路徑

## Related

- [Simulation Python API](../../how-to/simulation/python-api.md)
- [Data Formats Overview](index.md)
