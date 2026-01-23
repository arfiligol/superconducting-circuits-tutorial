# Guardrails: 程式碼風格與品質 (Code Style)

本文檔概述了專案的程式碼撰寫標準與最佳實踐。

## 一般原則

我們遵循 **[PEP 8](https://peps.python.org/pep-0008/)** 作為 Python 程式碼風格標準。

> **PEP 8** 是 Python 官方的風格指南（**規範標準**），而 **Ruff** 是我們用來自動檢查與強制執行這些規範的**工具**。詳見 [工具鏈章節](#工具鏈-toolchain)。

## Clean Code 原則

我們採用 Robert C. Martin 《*Clean Code*》一書中的原則。

### 1. 命名 (Naming)
- **函數 (Functions)**：使用**動詞**或**動詞片語**，清楚描述函數做了什麼（例如：`calculate_frequency`, `build_record`, `process_data`）。
    - *Bad*: `squid_lc_frequency`, `y11_imaginary`, `process`
    - *Good*: `calculate_squid_lc_frequency`, `calculate_y11_imaginary`, `process_hfss_file`
- **變數 (Variables)**：使用有意義的**名詞**。
- **類別 (Classes)**：使用**名詞**或**名詞片語**。

### 2. 函數 (Functions)
- **單一職責原則 (SRP)**：一個函數應該只做一件事，把它做好，且只做這件事。
- **短小精悍 (Small)**：函數應該保持短小且專注。
- **參數 (Arguments)**：限制參數數量（目標是 3 個或更少）。對於大量參數，請使用資料類別 (Data Classes) 或物件封裝。

## Clean Architecture 原則

我們採用 **Clean Architecture** 來確保關注點分離與可維護性。

### 1. 分層 (Separation of Layers)
- **Domain Layer** (`domain/`)：包含核心業務邏輯與實體（例如 Pydantic schemas）。不依賴外部層級。
- **Application Layer** (`application/`)：包含應用程式特定的業務規則與使用案例。僅依賴 Domain 層。
- **Infrastructure Layer** (`infrastructure/`)：包含框架、驅動程式與外部介面（例如 視覺化、檔案 I/O）。依賴 Application/Domain 層。

### 2. 依賴原則 (The Dependency Rule)
原始碼的依賴關係必須只能**向內**指向更高級別的策略。
- 內圈（如 Domain）中的任何東西都不能知道外圈（如 Infrastructure）的任何資訊。

## 型別標註 (Type Hinting)
- 使用 **Python 3.10+** 語法。
- 使用 `|` 來表示 Union（例如：用 `int | None` 取代 `Optional[int]`）。
- 使用標準集合型別 (`list`, `dict`, `tuple`) 取代 `typing` 模組的對應項目。

## 工具鏈 (Toolchain)

專案使用自動化工具來確保程式碼一致性與品質。詳細說明請參考：

👉 **[Linting & Formatting Guardrails](./linting.md)**

### 快速參考
- **Ruff**: 統一 Linting & Formatting
- **Pre-commit**: Git commit 前自動檢查
- **BasedPyright**: 型別檢查 (Basic mode)

### 日常使用
```bash
# 執行所有檢查
uv run pre-commit run --all-files

# 手動執行 Ruff
uv run ruff check .
uv run ruff format .
```
