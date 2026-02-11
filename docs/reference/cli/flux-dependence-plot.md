---
aliases:
- sc-plot-flux-dependence
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 磁通依賴熱圖繪製指令說明
version: v0.1.0
last_updated: 2026-01-28
updated_by: docs-team
---

# sc plot flux-dependence

繪製磁通依賴 (Flux Dependence) 掃描數據的熱圖 (Heatmap) 與切片圖 (Slice)。

## Usage

```bash
uv run sc plot flux-dependence [OPTIONS] [datasets ...]
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `datasets` | Dataset 名稱或 ID（可多個） | 必填 |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--parameter` | 參數名稱 (例如 `S11`) | `S11` |
| `--view` | 繪製視圖 (`amplitude`, `phase`, `combined`, `all`) | `all` |
| `--phase-unit` | 相位單位 (`rad`, `deg`) | `rad` |
| `--wrap-phase` | 是否將相位包裹在 $\pm\pi$ 或 $\pm 180^\circ$ | False |
| `--slice-frequency` | 擷取特定頻率 (GHz) 的 Bias 切片 | |
| `--slice-bias` | 擷取特定 Bias (mA) 的頻率切片 | |
| `--device` | 自訂圖表中的 Device 標籤 | Dataset 名稱 |
| `--show` / `--no-show` | 是否直接開啟瀏覽器預覽 | `--show` |
| `--save-html` / `--no-save-html` | 是否輸出 HTML | `--no-save-html` |
| `--output`, `-o` | HTML 輸出路徑 | 自動產生 |

## Examples

**繪製所有視圖 (Amplitude + Phase)**
```bash
uv run sc plot flux-dependence LJPAL6572_B44D1
```

**僅繪製相視圖 (Phase)，使用角度顯示**
```bash
uv run sc plot flux-dependence --view phase --phase-unit deg LJPAL6572_B44D1
```

**繪製特定切片**
```bash
uv run sc plot flux-dependence \
    --slice-frequency 6.0 \
    --slice-bias 0.0 \
    LJPAL6572_B44D1
```

## Notes

!!! note "CLI 架構"
    此功能已整合至 `sc plot` 子指令樹，不再使用獨立命令 `flux-dependence-plot`。

!!! warning "目前資料前置條件"
    `sc plot flux-dependence` 需要資料庫中已存在 2D `amplitude/phase` 記錄。
    目前 `sc preprocess flux` 的原始 TXT 解析尚未完成，若沒有既有資料，指令會顯示 `Skip`。

<!-- CLI-HELP-START -->

## CLI Help（自動生成）

!!! note "自動生成"
    此區塊由 `sc-docs-cli` 產生，請勿手動修改。

```text
Usage: sc plot flux-dependence [OPTIONS] DATASETS...

 Plot flux-dependence maps and slices from DB.

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    datasets      DATASETS...  Dataset names or IDs. [required]             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --parameter                               TEXT              Parameter name   │
│                                                             (e.g. S11).      │
│                                                             [default: S11]   │
│ --view                                    [amplitude|phase  View mode.       │
│                                           |combined|all]    [default: all]   │
│ --phase-unit                              [rad|deg]         Phase unit.      │
│                                                             [default: rad]   │
│ --wrap-phase           --no-wrap-phase                      Wrap phase to    │
│                                                             ±pi or ±180°.    │
│                                                             [default:        │
│                                                             no-wrap-phase]   │
│ --slice-frequency                         FLOAT             Slice at         │
│                                                             frequency (GHz). │
│ --slice-bias                              FLOAT             Slice at bias.   │
│ --device                                  TEXT              Custom device    │
│                                                             label in title.  │
│ --show                 --no-show                            Open interactive │
│                                                             preview in       │
│                                                             browser.         │
│                                                             [default: show]  │
│ --save-html            --no-save-html                       Save output as   │
│                                                             HTML.            │
│                                                             [default:        │
│                                                             no-save-html]    │
│ --output           -o                     PATH              Output HTML      │
│                                                             path.            │
│ --help                                                      Show this        │
│                                                             message and      │
│                                                             exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

<!-- CLI-HELP-END -->
