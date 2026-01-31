---
aliases:
  - "如何參與貢獻 (Contributing)"
tags:
  - diataxis/how-to
  - status/draft
---

# 如何參與貢獻 (Contributing)

感謝您有興趣參與 **超導電路教學** 專案的開發！

本指南將協助您建立開發環境並了解我們的協作流程。我們採用 **Fork & Pull Request** 的模式進行協作。

## 1. 環境建置

我們使用 `uv` 進行依賴管理。

### 前置需求
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### 安裝步驟

1.  **Fork 專案**：
    在 GitHub 專案頁面上點擊 "Fork"，將專案複製到您自己的帳號下。

2.  **Clone 您的 Fork**：
    將 `<YOUR_USERNAME>` 替換為您的 GitHub 帳號：
    ```bash
    git clone https://github.com/<YOUR_USERNAME>/superconducting-circuits-tutorial.git
    cd superconducting-circuits-tutorial
    ```

3.  **同步依賴 (Sync dependencies)**：
    這會自動建立 `.venv` 虛擬環境並安裝所有套件（包含開發工具）。
    ```bash
    uv sync
    ```

4.  **啟動虛擬環境**：
    ```bash
    source .venv/bin/activate
    ```

## 2. 開發流程 (Workflow)

### 執行測試
我們使用 `pytest` 確保功能正常。
```bash
uv run pytest
```

### 預覽文件
我們使用 `mkdocs` 搭配 `material` 主題。
```bash
uv run mkdocs serve
```
啟動後請訪問 `http://localhost:8000` 查看效果。

> 需要更多客製化？請參考 [MkDocs 官方文檔](https://www.mkdocs.org/)。

### 提交變更 (Pull Request)

1.  **建立分支 (Branch)**：
    ```bash
    git checkout -b feature/my-new-feature
    ```
2.  **提交變更 (Commit)**：
    我們建議遵循 Conventional Commits 規範 (e.g., `feat:`, `fix:`, `docs:`)。
    ```bash
    git commit -m "feat: 新增某個功能"
    ```
3.  **推送至 Fork (Push)**：
    ```bash
    git push origin feature/my-new-feature
    ```
4.  **發起 Pull Request**：
    回到原始專案頁面，點擊 "Compare & pull request" 提交您的變更。

### 提交前檢查 (Pre-commit Checks)
在提交 Pull Request 之前，請確保：

1.  **Typing**: 通過型別檢查（我們使用 Python 3.12+ 語法）。
2.  **Formatting**: 程式碼已格式化（遵循 PEP 8，透過 Ruff 檢查）。
3.  **Tests**: 所有測試皆通過。

> 詳細的程式碼品質規範請參考 [Code Style Guardrails](../reference/guardrails/code-quality/code-style.md)。

## 3. 開發規範 (Guardrails)

所有開發規範統一放在 **[Guardrails](../reference/guardrails/index.md)** 區塊。

!!! tip "AI 助手設定"
    如果您使用 AI 輔助工具（如 Cursor, Windsurf），請前往各規範頁面，複製底部的 **[#agent-rule](../reference/guardrails/index.md)** 區塊貼入您的 System Prompt。

### 快速連結

| 類別 | 規範 | Agent Rule |
|---|---|---|
| **專案基礎** | [專案概述](../reference/guardrails/project-basics/project-overview.md) | [#agent-rule](../reference/guardrails/project-basics/project-overview.md#agent-rule) |
| | [技術堆疊](../reference/guardrails/project-basics/tech-stack.md) | [#agent-rule](../reference/guardrails/project-basics/tech-stack.md#agent-rule) |
| | [目錄結構](../reference/guardrails/project-basics/folder-structure.md) | [#agent-rule](../reference/guardrails/project-basics/folder-structure.md#agent-rule) |
| **執行驗證** | [執行指令](../reference/guardrails/execution-verification/build-commands.md) | [#agent-rule](../reference/guardrails/execution-verification/build-commands.md#agent-rule) |
| | [Linting](../reference/guardrails/execution-verification/linting.md) | [#agent-rule](../reference/guardrails/execution-verification/linting.md#agent-rule) |
| | [測試](../reference/guardrails/execution-verification/testing.md) | [#agent-rule](../reference/guardrails/execution-verification/testing.md#agent-rule) |
| **程式品質** | [程式碼風格](../reference/guardrails/code-quality/code-style.md) | [#agent-rule](../reference/guardrails/code-quality/code-style.md#agent-rule) |
| | [類型檢查](../reference/guardrails/code-quality/type-checking.md) | [#agent-rule](../reference/guardrails/code-quality/type-checking.md#agent-rule) |
| | [腳本撰寫](../reference/guardrails/code-quality/script-authoring.md) | [#agent-rule](../reference/guardrails/code-quality/script-authoring.md#agent-rule) |
| **文件設計** | [文件設計](../reference/guardrails/documentation-design/documentation.md) | [#agent-rule](../reference/guardrails/documentation-design/documentation.md#agent-rule) |
| | [Standards](../reference/guardrails/documentation-design/standards.md) | [#agent-rule](../reference/guardrails/documentation-design/standards.md#agent-rule) |
| | [Style](../reference/guardrails/documentation-design/style.md) | [#agent-rule](../reference/guardrails/documentation-design/style.md#agent-rule) |
| | [Maintenance](../reference/guardrails/documentation-design/maintenance.md) | [#agent-rule](../reference/guardrails/documentation-design/maintenance.md#agent-rule) |
| | [電路繪圖](./contributing/circuit-diagrams.md) | [#agent-rule](./contributing/circuit-diagrams.md#agent-rule) |
| | [CLI 文件自動生成](./contributing/cli-docs-automation.md) | [#agent-rule](./contributing/cli-docs-automation.md#agent-rule) |
