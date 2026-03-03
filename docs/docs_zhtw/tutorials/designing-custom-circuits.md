---
aliases:
- 設計自己的電路
- Designing Custom Circuits
status: draft
owner: docs-team
last_updated: 2026-03-02
updated_by: docs-team
---

# 設計自己的電路

現在的產品重心是：穩定地把需求轉成可模擬的 **Circuit Netlist**。

## 設計順序

1. 先寫需求描述
2. 先列出元件實例（`components`）
3. 決定哪些元件用固定值 `default`
4. 只有在需要 sweep 或共用可調值時，再加入 `parameters`
5. 列出節點編號（只用數字字串，地端固定 `0`）
6. 判斷哪些 row 該維持顯式寫法，哪些應該改用 `repeat`
7. 再進入 `/simulation` 設定 sources 與掃頻

## 範例 A：顯式寫法（短電路）

```python
{
    "name": "FloatingBranch",
    "components": [
        {"name": "R1", "default": 50.0, "unit": "Ohm"},
        {"name": "Lq", "default": 10.0, "unit": "nH"},
        {"name": "Cq", "default": 1.0, "unit": "pF"},
        {"name": "Cg", "default": 0.1, "unit": "pF"},
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "R1"),
        ("Lq", "1", "2", "Lq"),
        ("Cq", "1", "2", "Cq"),
        ("Cg", "2", "0", "Cg"),
    ],
}
```

## 範例 B：生成寫法（長鏈，固定值）

```python
{
    "name": "RepeatedLadder",
    "components": [
        {"name": "Rleft", "default": 50.0, "unit": "Ohm"},
        {"name": "Rright", "default": 50.0, "unit": "Ohm"},
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 1, "step": 1},
                    "n2": {"base": 2, "step": 1}
                },
                "emit": [
                    {"name": "L${n}_${n2}", "default": 80e-12, "unit": "H"},
                    {"name": "C${n2}_0", "default": 40e-15, "unit": "F"}
                ]
            }
        }
    ],
    "topology": [
        ("P1", "1", "0", 1),
        ("R1", "1", "0", "Rleft"),
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 1, "step": 1},
                    "n2": {"base": 2, "step": 1}
                },
                "emit": [
                    ("L${n}_${n2}", "${n}", "${n2}", "L${n}_${n2}"),
                    ("C${n2}_0", "${n2}", "0", "C${n2}_0")
                ]
            }
        },
        ("R5", "5", "0", "Rright"),
        ("P2", "5", "0", 2),
    ],
}
```

## 範例 C：生成寫法（可 Sweep 值）

```python
{
    "name": "TunableLadder",
    "parameters": [
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "series": {
                    "csh": {"base": 40e-15, "step": 5e-15}
                },
                "emit": [
                    {"name": "Csh${index}", "default": "${csh}", "unit": "F"}
                ]
            }
        }
    ],
    "components": [
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 2, "step": 1}
                },
                "emit": [
                    {"name": "C${n}_0", "value_ref": "Csh${index}", "unit": "F"}
                ]
            }
        }
    ],
    "topology": [
        {
            "repeat": {
                "count": 4,
                "index": "cell",
                "symbols": {
                    "n": {"base": 2, "step": 1}
                },
                "emit": [
                    ("C${n}_0", "${n}", "0", "C${n}_0")
                ]
            }
        }
    ],
}
```

## 什麼時候該改用 `repeat`

!!! tip "判斷規則"
    如果你只是反覆複製同一組 component / topology row，且每次只改名稱尾碼、節點編號或線性數值，就應該改用 `repeat`。

如果每一段都不一樣，就維持顯式寫法。

## 什麼時候該加入 `parameters`

!!! note "只有在這些情況才需要"
    - 你要在 Simulation UI 做 sweep
    - 多個元件要共用同一個可調值
    - repeated cells 要各自有獨立可調值

若沒有這些需求，直接用 `components.default` 最簡單。

## 不要做的事

!!! danger "不要把 Editor 當腳本環境"
    - 不要期待能寫任意 `for`
    - 不要期待能寫 `if`
    - 不要把 source / pump / hbsolve 參數寫進 netlist

這些都不屬於目前的 Code Editor 語法範圍。

## 自我驗收

你完成本篇後，應該能回答：

- 哪些電路應該維持顯式 row
- 哪些電路應該拆成 prelude / repeat body / epilogue
- 哪些值應該直接放在 `components.default`
- 哪些值應該升級成 `parameters + value_ref`

## Related

- [重複電路段落與 `repeat`](../repeating-circuit-sections.md)
- [Circuit Netlist Format](../reference/data-formats/circuit-netlist.md)
