# Superconducting Circuits Tutorial

歡迎來到超導電路模擬教學！本站使用 [JosephsonCircuits.jl](https://github.com/QICKLab/JosephsonCircuits.jl) 進行電路模擬。

## 這是什麼？

這是一個結合 **教學** 與 **研究** 的學習資源：

- 🎓 **學習**：維持基礎，深入學習如何使用 JosephsonCircuits.jl 模擬超導電路
- 🔬 **研究**：記錄電路模型行為、套件探索的這筆記
- 💻 **實作**：每個教學都有對應的可執行程式碼

## 適合誰？

- 想要學習超導量子電路模擬的研究生
- 需要使用 JosephsonCircuits.jl 的研究人員
- 對 JPA (Josephson Parametric Amplifier) 和 Qubit 模擬有興趣的人

## 快速開始

1. [安裝環境](getting-started/installation.md) — 設定 Julia 和相依套件
2. [第一次模擬](getting-started/first-simulation.md) — 執行你的第一個電路模擬
3. [理解 hbsolve](getting-started/understanding-hbsolve.md) — 認識核心函式

## 教學主題

| 主題 | 說明 |
|------|------|
| [LC 共振器](tutorials/lc-resonator.md) | 最基本的電路模型 |
| [參數掃描](tutorials/parameter-sweep.md) | 單維度與多維度掃描 |

## 專案結構

此專案採用 **App-Centric Hybrid 架構**，所有的核心代碼皆位於 `src/`。

### 1. Source Root (`src/`)
多語言的源碼中心：

- **`sc_analysis/`** (Python): 核心分析邏輯 (Clean Architecture)。
- **`sc_app/`** (Python): NiceGUI 應用程式介面。
- **`plotting.jl`** (Julia): 共用繪圖工具。

### 2. Interfaces
- **`scripts/`**: Python CLI 腳本 (呼叫 `src/sc_analysis`)。
- **`examples/`**: Julia 模擬與教學範例。

### 3. Documentation
- **`docs/`**: 文件網站 (MkDocs)。
