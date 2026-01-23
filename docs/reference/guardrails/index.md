---
aliases:
  - "Guardrails"
  - "開發規範"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "開發規範 Source of Truth，類型檢查、程式風格、數據處理"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Guardrails

開發規範，確保程式碼品質與一致性。

> [!IMPORTANT]
> 此為 Source of Truth (SoT)。所有開發者（人類與 AI Agent）必須遵守。

## Rules

- [[./type-checking.md|Type Checking]] - BasedPyright 類型檢查規範
- [[./code-style.md|Code Style]] - 程式風格與單一職責原則
- [[./data-handling.md|Data Handling]] - 數據處理與路徑規範
- [[./script-authoring.md|Script Authoring]] - CLI 腳本撰寫規範

## Verification

```bash
# 類型檢查
uv run basedpyright src

# 程式風格
uv run ruff check .
```

## Related

- [[../../explanation/design-decisions/index.md|Design Decisions]] - 決策理由
