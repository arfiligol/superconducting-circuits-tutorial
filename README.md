# Superconducting Circuits Tutorial

使用 [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) 學習超導電路模擬的教學專案。

## 📚 文件網站

👉 **[線上教學文件](https://arfiligol.github.io/superconducting-circuits-tutorial/)**

## 🚀 快速開始

### 1. 安裝環境

```bash
git clone https://github.com/arfiligol/superconducting-circuits-tutorial.git
cd superconducting-circuits-tutorial
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

### 2. 執行範例

```bash
julia --project=. examples/01_simple_lc/lc_resonator.jl
```

### 3. 本地預覽文件

```bash
pip install mkdocs-material mkdocs-glightbox
mkdocs serve
```

## 📁 專案結構

```
superconducting-circuits-tutorial/
├── docs/          # MkDocs 教學文件
├── examples/      # 可執行的 Julia 範例
├── sandbox/       # 實驗區 (不進版控)
└── src/           # 共用工具 (ili_plot 等)
```

## 🎯 適合誰？

- 想學習超導量子電路模擬的研究生
- 需要使用 JosephsonCircuits.jl 的研究人員
- 對 JPA 和 Qubit 模擬有興趣的人

## 📖 教學主題

| 主題 | 說明 |
|------|------|
| LC 共振器 | 基本電路模型 |
| 參數掃描 | 單/多維度掃描技術 |
| Harmonic Balance | 核心模擬方法 |
| S/Z/Y 參數 | 網路參數分析 |

## 🛠️ 工具

- `src/plotting.jl` — PlotlyJS 繪圖封裝 (`ili_plot`)

## 📜 License

MIT
