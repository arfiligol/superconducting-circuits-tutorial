---
aliases:
- Circuit Netlist 入門
- Circuit Netlist Getting Started
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# Circuit Netlist 入門

本篇的目標很單純：第一次在 WebUI 中寫出一份最小可用的 **Circuit Netlist**，並成功完成模擬。

!!! tip "成功標準"
    完成本篇後，你應該能自己重打一個單埠 LC 電路，而不是只會複製貼上。

## 最小可用範例（顯式寫法）

```python
{
    "name": "SmokeStableSeriesLC",
    "components": [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "L1", "default": 10.0, "unit": "nH"},
        {"name": "C1", "default": 1.0, "unit": "pF"},
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R1"),
        ("L1", "1", "2", "L1"),
        ("C1", "2", "0", "C1"),
    ],
}
```

## 逐欄位理解

### `components`

- 元件實例宣告，也是主要作者介面
- 每筆至少需要：`name`, `unit`
- 值來源二選一：
  - `default`：固定值
  - `value_ref`：引用可 sweep 參數

### `topology`

- 實際連線結構
- 最簡單的情況下，每筆都是四元 tuple：`(element, node1, node2, value_ref)`
- 一般元件的 `value_ref` 要指向 `components[*].name`
- `P*` 項目代表 port，最後一欄要用整數 port index

### `parameters`（先不用）

- 這一篇先不需要 `parameters`
- 只有在你要做 sweep 或共用可調值時，才需要引入

!!! note "節點規則"
    - 節點只能是數字字串
    - `0` 是唯一地端
    - 不接受 `gnd`

## 操作流程

1. 進入 `/schemas/new`
2. 貼上上面的 netlist
3. 按 `Format`
4. 按 `Save Schema`
5. 前往 `/simulation` 選擇這份 schema
6. 用預設 sweep 跑一次模擬

## 你現在先不用學的東西

!!! info "下一篇才會教"
    這一篇只教顯式寫法。

    若你遇到長鏈、重複 cell、JTWPA 這類需要大量重複 row 的情況，請到下一篇學 `repeat`。

## 常見錯誤

!!! warning "最常見"
    `components[*]` 必須有可解值。

- 缺少 `default` 且缺少 `value_ref`：錯
- `default` 和 `value_ref` 同時存在：也錯

!!! warning "另一個常見錯誤"
    `topology` 的最後一欄對一般元件要引用 component name，而不是數值或 parameter name。

- `("L1", "1", "2", "L1")`：對，因為 `components` 裡有 `L1`
- `("L1", "1", "2", 10.0)`：錯，`topology` 不直接存數值

## 自我驗收

你完成本篇後，應該能不看範例就回答：

- 為什麼 `components` 是主要作者介面
- 為什麼 `P1` 的最後一欄是整數 `1`
- 為什麼一般元件的 topology 最後一欄是 component name

## Related

- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.md)
- [Schema Editor](../reference/ui/schema-editor.md)
- [重複電路段落與 `repeat`](../repeating-circuit-sections.md)
