---
aliases:
  - "Code Style Rules"
  - "程式風格規範"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "程式風格、SRP、命名規範"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Code Style

程式風格與單一職責原則規範。

## Single Responsibility Principle (SRP)

### File Level
每個檔案應有單一、明確的目的：
- 數據載入
- 繪圖
- 優化
- 腳本入口

避免「上帝檔案」。

### Function/Class Level
函數與類別應只做一件事：
- 計算 Q-factor 的函數不應同時載入 CSV
- 物理模型與 I/O 邏輯分離

### Project Structure
維持清晰的關注點分離：
```
src/
├── models/         # 物理模型
├── visualization/  # 繪圖
├── scripts/        # CLI 入口
└── optimizer/      # 擬合邏輯
```

## Linting

```bash
uv run ruff check .
```

必須零錯誤。

## Schema Updates

當修改分析輸出或序列化格式時：

1. 更新相關 `TypedDict` / Pydantic 模型
2. 更新 [[../data-formats/index.md|Data Formats]] 文件
3. 在 PR 描述中說明破壞性變更

## Related

- [[./type-checking.md|Type Checking]] - 類型檢查規範
- [[./index.md|Guardrails]] - 規範總覽
