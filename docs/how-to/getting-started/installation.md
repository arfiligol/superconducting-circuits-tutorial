---
aliases:
  - "安裝環境"
tags:
  - diataxis/how-to
  - status/draft
  - topic/getting-started
---

# 安裝環境

本教學結合了 **Python** (數據分析/CLI) 與 **Julia** (核心模擬) 兩種語言。

為了簡化環境管理，我們推薦使用現代化的管理工具：**uv** 與 **juliaup**。

## 1. 安裝基礎工具

在開始之前，請檢查您的系統是否已具備必要工具。

### 快速檢查 (Checkpoint)

打開終端機 (Terminal)，輸入以下指令確認版本：

```bash
julia --version  # 需 >= 1.9 (推薦 1.10+)
uv --version     # 需 >= 0.4.0
git --version    # 需安裝
```

!!! tip "提示"
    如果您已安裝上述工具且版本符合要求，可直接跳至 [步驟 2：下載專案](#2)。
    **不需要** 預先安裝 Python，`uv` 會自動為此專案管理獨立且正確的 Python 版本。

### 安裝 Julia (`juliaup`)

推薦使用官方版本管理器 `juliaup`，它能自動處理路徑並方便切換版本。

- **macOS / Linux**:
  ```bash
  curl -fsSL https://install.julialang.org | sh
  ```
- **Windows**:
  在 Microsoft Store 搜尋 "Julia" 並安裝 App。

### 安裝 uv

`uv` 是一個極速的 Python 套件與專案管理器。

- **macOS / Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

---

## 2. 下載專案

將專案 Clone 到本地端：

```bash
git clone https://github.com/arfiligol/superconducting-circuits-tutorial.git
cd superconducting-circuits-tutorial
```

---

## 3. 設定環境

### Python 環境 (自動化)

本專案使用 `uv` 管理 Python 環境。執行 `sync` 指令，`uv` 會自動下載正確的 Python 版本 (例如 3.12) 並安裝所有依賴套件。

```bash
uv sync
```

### Julia 環境

安裝 Julia 依賴套件 (核心模擬引擎)：

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

這會安裝包括 `JosephsonCircuits.jl`, `PlotlyJS.jl` 等核心套件。

---

## 4. 驗證安裝

完成上述步驟後，請執行以下指令確認一切運作正常。

**驗證 Python CLI 工具**：
```bash
uv run sc analysis fit lc-squid --help
```
*應顯示幫助訊息 (Help Message)*

**驗證 Julia 模擬核心**：
```bash
julia --project=. -e 'using JosephsonCircuits; println("✅ Julia Core Ready!")'
```
*應顯示 "✅ Julia Core Ready!"*

---

## 下一步

現在您的環境已設置完畢！

👉 [第一次模擬](first-simulation.md)
