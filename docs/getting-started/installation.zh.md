# 安裝環境

本教學使用 Julia 語言和 JosephsonCircuits.jl 套件。

## 前置需求

- Julia 1.9 或更新版本
- Git（用於版本控制）

## 安裝 Julia

### macOS

使用 Homebrew：

```bash
brew install julia
```

### Windows / Linux

從 [Julia 官網](https://julialang.org/downloads/) 下載安裝程式。

## 下載專案

```bash
git clone https://github.com/arfiligol/superconducting-circuits-tutorial.git
cd superconducting-circuits-tutorial
```

## 安裝相依套件

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

這會根據 `Project.toml` 安裝所有需要的套件，包括：

- **JosephsonCircuits.jl** — 核心模擬引擎
- **PlotlyJS** — 互動式繪圖
- **CSV / DataFrames** — 數據處理

## 驗證安裝

```bash
julia --project=. -e 'using JosephsonCircuits; println("安裝成功！")'
```

## 下一步

👉 [第一次模擬](first-simulation.md)
