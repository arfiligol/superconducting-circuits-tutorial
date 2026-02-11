---
aliases:
- sc-plot-resonance-map
tags:
- audience/team
status: draft
owner: docs-team
audience: team
scope: 依 Qubit Structure 繪製 Resonance Frequency 二維圖
version: v0.1.0
last_updated: 2026-02-11
updated_by: docs-team
---

# sc plot different-qubit-structure-frequency-comparison-table

依據資料庫中的 `analysis_result / f_resonance` 記錄，繪製「Qubit x Structure」的 Resonance Frequency 比較表（預設）。

## Usage

```bash
uv run sc plot different-qubit-structure-frequency-comparison-table [OPTIONS]
```

## Options

| Option | Description | Default |
|---|---|---|
| `--dataset`, `-d` | 以 Dataset 名稱或 ID 篩選（可重複） | 全部 |
| `--mode` | 指定 mode 標籤 | `Mode 1` |
| `--l-jun-nh` | 指定目標 `L_jun (nH)`，每格取最近點 | 未指定 |
| `--aggregate` | 未指定 `--l-jun-nh` 時聚合方式：`first`/`mean`/`min`/`max` | `first` |
| `--render` | 輸出樣式：`table` 或 `heatmap` | `table` |
| `--show` / `--no-show` | 是否直接開啟瀏覽器預覽 | `--show` |
| `--save-html` / `--no-save-html` | 是否輸出 HTML | `--no-save-html` |
| `--output`, `-o` | HTML 輸出路徑 | 自動產生 |
| `--png-output` | 輸出 PNG（需 `kaleido`） | 未指定 |

## Examples

**預設 Comparison Table（直接瀏覽器預覽）**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table
```

**指定 mode 與目標 L_jun**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table --mode "Mode 1" --l-jun-nh 0.1
```

**改成 2D Heatmap**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table --render heatmap
```

**儲存 Table 為 HTML**
```bash
uv run sc plot different-qubit-structure-frequency-comparison-table --render table --save-html
```

## Alias

相容舊命令：
```bash
uv run sc plot resonance-map
```
