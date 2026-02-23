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
| [專案概述](./project-basics/project-overview.md) | 專案目標、範疇與受眾 | [#agent-rule](./project-basics/project-overview.md#agent-rule) |
| [技術堆疊](./project-basics/tech-stack.md) | Python (uv) + Julia (juliaup) | [#agent-rule](./project-basics/tech-stack.md#agent-rule) |
| [目錄結構](./project-basics/folder-structure.md) | Clean Architecture 分層 | [#agent-rule](./project-basics/folder-structure.md#agent-rule) |

### 執行與驗證

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [執行指令](./execution-verification/build-commands.md) | `uv sync`, `uv run --group dev zensical serve -f zensical.yml`, 腳本執行 | [#agent-rule](./execution-verification/build-commands.md#agent-rule) |
| [Linting & Formatting](./execution-verification/linting.md) | Ruff, Pre-commit, BasedPyright | [#agent-rule](./execution-verification/linting.md#agent-rule) |
| [測試規範](./execution-verification/testing.md) | Pytest, Julia Pkg.test | [#agent-rule](./execution-verification/testing.md#agent-rule) |
| [CI 品質關卡](./execution-verification/ci-gates.md) | 合併前必通過的檢查 | [#agent-rule](./execution-verification/ci-gates.md#agent-rule) |

### 程式品質 (Code Quality)

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [程式碼風格](./code-quality/code-style.md) | Clean Code, PEP 8, Type Hints | [#agent-rule](./code-quality/code-style.md#agent-rule) |
| [類型檢查](./code-quality/type-checking.md) | BasedPyright 配置 | [#agent-rule](./code-quality/type-checking.md#agent-rule) |
| [腳本撰寫](./code-quality/script-authoring.md) | CLI 入口點結構 | [#agent-rule](./code-quality/script-authoring.md#agent-rule) |
| [資料處理](./code-quality/data-handling.md) | Path, I/O 規範 | [#agent-rule](./code-quality/data-handling.md#agent-rule) |

### 文件設計 (Documentation Design)

| 規範 | 說明 | Agent Rule |
|---|---|---|
| [文件設計](./documentation-design/documentation.md) | Standards / Style / Maintenance 索引 | [#agent-rule](./documentation-design/documentation.md#agent-rule) |
| [Explanation Physics](./documentation-design/explanation-physics.md) | Explanation/Physics 教學定位與一致性規範 | [#agent-rule](./documentation-design/explanation-physics.md#agent-rule) |
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
uv run --group dev zensical build -f zensical.yml
```
