---
aliases:
  - "Linting & Formatting Guardrails"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Linting & Formatting Guardrails

我們採用業界標準工具來強制執行代碼品質與風格。

## 工具選擇 (Toolchain)

### 1. Ruff (Linting & Formatting)
[Ruff](https://docs.astral.sh/ruff/) 是一個用 Rust 編寫的極速 Python Linter 與 Formatter。

- **為什麼選擇它？**：
    - **速度**：比傳統工具 (Flake8, Black) 快 10-100 倍。
    - **整合性**：單一工具取代了 Flake8 (lint), Black (format), isort (import sorting), pyupgrade (syntax modernization)。
    - **標準化**：已成為 Python 群的新標準 (採用者包含 Pandas, FastAPI, SciPy)。

### 2. Pre-commit (Automation)
[Pre-commit](https://pre-commit.com/) 是一個 Git hook 管理框架。

- **為什麼選擇它？**：
    - **強制性**：在 `git commit` 時自動執行檢查，防止不合規的代碼進入版控。
    - **一致性**：確保所有開發者使用相同版本的檢查工具。

### 3. BasedPyright (Type Checking)
[BasedPyright](https://github.com/DetachHead/basedpyright) 是 Microsoft Pyright 的增強版。

- **為什麼選擇它？**：
    - **相容性**：標準 Pylance 是 VS Code 專用擴充。BasedPyright 提供了跨編輯器與 Agentic 環境 (如 Antigravity) 一致的 CLI 體驗。
    - **嚴格性**：提供比標準 Pyright 更嚴格的預設值，強迫處理 `None` 與 `Any`。

## 設定與使用 (Usage)

### 首次設定
開發者 Clone 專案後，必須安裝 git hooks：
```bash
uv run pre-commit install
```

### 日常開發
Git Commit 時會自動觸發檢查。如果失敗，工具會自動修復 (如格式化) 或報錯。
您也可以手動執行：
```bash
# 執行所有檢查
uv run pre-commit run --all-files

# 僅手動執行 Ruff
uv run ruff check .
uv run ruff format .
```

## 規則設定 (Configuration)
詳見 `pyproject.toml` 中的 `[tool.ruff]` 與 `[tool.basedpyright]` 區塊。

---

## Agent Rule { #agent-rule }

```markdown
## Lint / Format Commands
- **Format (Python)**: `uv run ruff format .` (Run first)
- **Lint (Python)**: `uv run ruff check . --fix` (Run second)
- **Type Check**: `uv run basedpyright`
- **Pre-commit**: `uv run pre-commit run --all-files` (Master check)
- **Config Loc**: `pyproject.toml` (`[tool.ruff]`, `[tool.basedpyright]`).
- **Policy**: No lint errors allowed in `src/`.
```
