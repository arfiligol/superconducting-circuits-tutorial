---
aliases:
- Add Data Source
- 新增數據來源
tags:
- audience/team
status: stable
owner: docs-team
audience: team
scope: 如何擴展管線以支援新的數據格式
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Add New Data Source

如果你有新的模擬軟體 (e.g. Sonnet) 或測量儀器匯出的數據，請依此指南新增支援。

## Strategy

不需要修改分析核心，只需撰寫一個新的 `convert-*` 腳本，將新格式匯入 SQLite Dataset。

## Steps

1. **分析原始格式**
   - 確認 Header 結構。
   - 確認數據排列 (Pivot table vs Long format)。
   - 確認單位 (必須轉換為標準單位：GHz, nH, pF)。

2. **建立轉換腳本**
   在 `src/preprocess/` 新增 `convert_new_source.py`，流程包含：

   - 讀取 CSV/TXT
   - 解析軸與數值
   - 建立 Dataset 與 DataRecords
   - 寫入 SQLite (`data/database.db`)

3. **註冊 CLI 入口**
   在 `pyproject.toml` 新增：
   ```toml
   [project.scripts]
   convert-new-source = "src.preprocess.convert_new_source:main"
   ```

4. **測試**
   執行轉換並用 `sc db dataset-record list` / `sc plot admittance` 驗證資料已入庫。

## Checklist

- [ ] 單位是否正確轉換？
- [ ] Metadata (如 Power) 是否保留？
- [ ] 原始檔案路徑是否記錄在 `raw_files` 欄位？

## Related

- [Preprocessing Rationale](../../explanation/architecture/pipeline/preprocessing-rationale.md) - 為什麼要這樣做
- [Dataset Record](../../reference/data-formats/dataset-record.md) - Schema 參考
- [Script Authoring](../../reference/guardrails/code-quality/script-authoring.md) - 腳本規範
