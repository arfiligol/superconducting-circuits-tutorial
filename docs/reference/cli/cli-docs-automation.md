---
aliases:
  - "CLI 文件自動生成"
  - "CLI Docs Automation"
tags:
  - diataxis/reference
  - status/draft
  - audience/contributor
  - topic/cli
  - topic/documentation
owner: I-LI CHIU
---

# CLI 文件自動生成

本文件定義 **CLI Reference 自動化產生** 的整合方式與維護規範。

## 現況

目前 `docs/reference/cli/` 仍以人工維護為主。完成 Typer 遷移後，將改用自動生成流程以避免參數文件與實作不一致。

## 目標

- 以 CLI 的 help 輸出作為單一來源
- 自動產生 `docs/reference/cli/*.md`
- 取代手寫的 CLI Options 內容，僅保留額外說明與導覽頁

## 整合規則

1. **產生來源**：從各 CLI 指令的 `--help` 輸出生成 Reference。
2. **輸出位置**：`docs/reference/cli/`。
3. **人工內容**：只保留導覽（如 `index.md`）與補充說明頁，不手改生成檔。
4. **更新時機**：新增/變更 CLI 參數後必須重新生成。

## 後續動作（Typer 遷移完成後）

- 建立 CLI 文件產生器（建議放在 `scripts/docs/`）。
- 在 `pyproject.toml` 加入對應指令入口（例如 `sc-docs-cli`）。
- 產生內容覆蓋現有 CLI Reference（或以「生成區塊」取代）。

!!! note "狀態提醒"
    此流程尚未啟用，待 Typer 遷移完成後再落實自動生成。

## Related

- [CLI Reference](index.md)
