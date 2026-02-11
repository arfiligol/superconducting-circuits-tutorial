---
aliases:
  - "Documentation Maintenance"
  - "文件維護"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
status: stable
owner: docs-team
audience: team
scope: "文件維護規範：雙語同步、版本與 Frontmatter 更新、Zensical 檢查"
version: v0.1.0
last_updated: 2026-02-08
updated_by: docs-team
---

# Documentation Maintenance

本文件定義文件維護流程（雙語同步、更新規則、檢查清單）。

---

## 雙語同步（必須）

本專案使用 Zensical 的 `i18n` 模組（suffix 結構）：

- 中文：`path/to/page.md`
- 英文：`path/to/page.en.md`

!!! warning "同步規則"
    - 新增文件：必須同時新增 `.en.md`
    - 修改內容：必須同步更新對應語言版本
    - 刪除/移動：必須同步處理兩個版本，並更新所有引用連結

---

## Frontmatter 更新

內容有改動時，至少更新：

- `last_updated`: `YYYY-MM-DD`
- `updated_by`: `team` 或 `team/person`

版本號建議：

- `v0.0.X`：小修正（typo、格式）
- `v0.X.0`：結構/內容新增（新增段落、規則調整）
- `vX.0.0`：重大重組（重新分章、移動/合併文件）

---

## 導覽與連結維護

新增/移動文件時：

1. 更新 `zensical.yml` 的 `nav:`（避免 orphan pages）
2. 檢查所有相對連結（含 `.en.md` 版本）
3. 若文件為 SoT，確認 `tags` 含 `sot/true`

---

## 檢查流程

### 本地預覽

```bash
uv run --group dev zensical serve -f zensical.yml
```

### 建置檢查

```bash
uv run --group dev zensical build -f zensical.yml
```

!!! tip "常見問題"
    - 若遇到 i18n/導航問題，先確認 `nav:` 與檔名 suffix（`.en.md`）是否正確。

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: update `zensical.yml` nav and fix all relative links
- **Verify**: `uv run --group dev zensical build -f zensical.yml` must pass
```
