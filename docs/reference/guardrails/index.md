---
aliases:
  - "Guardrails"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails

開發規範，確保程式碼品質與一致性。

!!! important "Source of Truth"
    此為開發規範的單一真理來源。所有開發者（人類與 AI Agent）必須遵守。

## 如何使用

- **人類**：閱讀各頁面的詳細說明，了解規範的「為什麼」。
- **AI Agent**：點擊各頁面底部的 **[#agent-rule](#)** 錨點，複製程式碼區塊貼入 System Prompt。

## 快速參考

### 專案基礎

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [專案概述](./project-overview.md) | 專案目標、範疇與受眾 | [#agent-rule](./project-overview.md#agent-rule) |
| [技術堆疊](./tech-stack.md) | Python (uv) + Julia (juliaup) | [#agent-rule](./tech-stack.md#agent-rule) |
| [目錄結構](./folder-structure.md) | Clean Architecture 分層 | [#agent-rule](./folder-structure.md#agent-rule) |

### 執行與驗證

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [執行指令](./build-commands.md) | `uv sync`, `mkdocs serve`, 腳本執行 | [#agent-rule](./build-commands.md#agent-rule) |
| [Linting & Formatting](./linting.md) | Ruff, Pre-commit, BasedPyright | [#agent-rule](./linting.md#agent-rule) |
| [測試規範](./testing.md) | Pytest, Julia Pkg.test | [#agent-rule](./testing.md#agent-rule) |
| [CI 品質關卡](./ci-gates.md) | 合併前必通過的檢查 | [#agent-rule](./ci-gates.md#agent-rule) |

### 程式品質 (Code Quality)

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [程式碼風格](./code-style.md) | Clean Code, PEP 8, Type Hints | [#agent-rule](./code-style.md#agent-rule) |
| [類型檢查](./type-checking.md) | BasedPyright 配置 | [#agent-rule](./type-checking.md#agent-rule) |
| [腳本撰寫](./script-authoring.md) | CLI 入口點結構 | [#agent-rule](./script-authoring.md#agent-rule) |
| [資料處理](./data-handling.md) | Path, I/O 規範 | [#agent-rule](./data-handling.md#agent-rule) |

### 文件設計 (Documentation Design)

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [文件撰寫](./documentation.md) | Diataxis, Style Guide | [#agent-rule](./documentation.md#agent-rule) |
| [電路繪圖](../../how-to/contributing/circuit-diagrams.md) | Schemdraw 規範 | [#agent-rule](../../how-to/contributing/circuit-diagrams.md#agent-rule) |

---

## 驗證指令

```bash
# Lint & Format
uv run ruff check . --fix && uv run ruff format .

# Type Check
uv run basedpyright src

# Test
uv run pytest

# Docs
uv run mkdocs build
```
