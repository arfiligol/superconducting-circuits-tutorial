# Superconducting Circuits Tutorial

使用 [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) 學習超導電路模擬的教學專案。

## Rewrite Foundation

Rewrite branch 目前同時保留 legacy NiceGUI runtime 與新的 `frontend/`、`backend/`、`desktop/` foundation。
請用獨立入口操作 rewrite stack，不要把 legacy runtime helper 當成 rewrite 啟動方式。

### Rewrite Quick Start

```bash
# Install rewrite workspace dependencies
npm run rewrite:install

# Run rewrite checks from repo root
npm run rewrite:check

# Build rewrite workspaces
npm run rewrite:build

# Start rewrite frontend + backend dev stack
npm run rewrite:dev

# Stop rewrite stack
npm run rewrite:stop
```

### Rewrite Desktop Wrapper

```bash
# Start the rewrite stack first, then wrap the frontend in Electron
DESKTOP_START_URL=http://127.0.0.1:3000 npm run dev --prefix desktop
```

### Legacy Runtime

```bash
# Legacy NiceGUI runtime remains separate
./scripts/dev_start.sh
./scripts/dev_stop.sh
```

## 📚 文件網站

👉 **[線上教學文件](https://arfiligol.github.io/superconducting-circuits-tutorial/)**

## 🚀 快速開始

### 1. 安裝環境

```bash
git clone https://github.com/arfiligol/superconducting-circuits-tutorial.git
cd superconducting-circuits-tutorial

# Python 環境 (使用 uv)
uv sync

# Julia 依賴會在首次執行時自動安裝 (透過 juliapkg)
```

### 2. 本地預覽文件

```bash
# 先產生 zh-TW / en staging tree
./scripts/prepare_docs_locales.sh

# 繁中站
uv run --group dev zensical serve

# 英文站
uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001

# 靜態建置輸出到 docs/site/
./scripts/build_docs_sites.sh
```

## 📁 專案結構

```
superconducting-circuits-tutorial/
├── src/
│   ├── core/                 # 核心邏輯 (Clean Architecture)
│   │   ├── analysis/         # 數據分析 (Fitting, Extraction)
│   │   ├── simulation/       # 電路模擬 (JuliaCall ↔ Julia)
│   │   └── shared/           # 共用工具 (visualization, utils)
│   └── scripts/              # CLI 入口點
├── data/                     # 數據生命週期
│   ├── raw/                  # 原始數據 (HFSS/VNA)
│   └── processed/            # 分析結果
│   └── database.db           # SQLite 資料庫
├── docs/                     # Zensical 教學文件
├── examples/                 # 可執行範例
├── pyproject.toml            # Python 依賴 (uv)
├── juliapkg.json             # Julia 依賴 (JosephsonCircuits.jl)
└── Project.toml              # Julia 專案設定
```

## 🔬 模擬工具 (Simulation)

使用 JosephsonCircuits.jl 進行電路模擬：

```bash
# LC 共振器模擬
uv run sc-simulate-lc -L 10 -C 1 --start 0.1 --stop 5 --points 100
```

| 指令 | 說明 |
|------|------|
| `sc-simulate-lc` | LC 共振器 S 參數模擬 |

## 📊 分析工具 (Analysis)

Python CLI 工具進行數據分析：

```bash
# SQUID 模型擬合
uv run sc analysis fit lc-squid SampleDataset

# Flux 依賴性繪圖
uv run sc plot flux-dependence FluxSweepDataset
```

| 指令 | 說明 |
|------|------|
| `sc analysis fit lc-squid` | SQUID 導納模型擬合 |
| `sc plot admittance` | 導納數據視覺化 (lines/heatmap) |
| `sc plot flux-dependence` | Flux 依賴性分析繪圖 |
| `sc plot different-qubit-structure-frequency-comparison-table` | 不同 Qubit 結構頻率比較表 |

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

## 📜 License

MIT
