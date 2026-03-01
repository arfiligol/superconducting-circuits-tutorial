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
version: v0.6.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Documentation Maintenance

本文件定義文件維護流程（雙語同步、更新規則、檢查清單）。

---

## 雙語同步（必須）

本專案採用 **原生 Separate Builds**：

- 設定檔：`zensical.toml`（zh-TW）與 `zensical.en.toml`（en）
- 中文主編輯來源：`docs/docs_zhtw/`
- 英文對應來源：`docs/docs_en/`
- 網站輸出：`docs/site/`（zh-TW）與 `docs/site/en/`（en）

!!! info "原生 Zensical 寫法"
    文件規範全面採用 Zensical 原生 TOML 設定。
    不再使用舊版 YAML，也不再依賴 MkDocs i18n 外掛。

!!! warning "同步規則"
    - 日常編輯一律以 `docs/docs_zhtw/` 為主
    - 內容變更後，必須同步更新 `docs/docs_en/` 對應頁
    - 刪除/移動：必須同步處理兩個版本，並更新所有引用連結
    - `docs/` 根目錄若仍保留舊的對照檔，只視為輔助參考，不是目前站點建置來源

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

## 原生 Zensical 盤點（文件層）

從文件維護角度，切換到原生 Separate Builds 時，必須同步修正以下四類資訊：

1. 所有維護說明都必須明確區分 `zensical.toml`（zh-TW）與 `zensical.en.toml`（en）。
2. 所有導覽維護規則都必須要求同步更新兩份原生 TOML 的 `nav`。
3. 所有文件修改都以 `docs/docs_zhtw/` 為主，再同步到 `docs/docs_en/`。
4. 所有 CI / README / Contributing 文件必須與上述流程一致，避免混用舊的 staging tree 心智模型。

---

## 導覽與連結維護

新增/移動文件時：

1. 同步更新 `zensical.toml` 與 `zensical.en.toml` 中的導覽與站點層設定
2. 檢查所有相對連結（`.en.md` 仍需維持對應語言版本的正確連結）
3. 若文件為 SoT，確認 `tags` 含 `sot/true`

---

## Native Separate Builds

本專案目前的正式架構名稱為：

- `Native Separate Builds`

其技術特徵為：

- 雙原生設定檔：`zensical.toml`（zh-TW）與 `zensical.en.toml`（en）
- 直接維護兩套來源樹：`docs/docs_zhtw/` 與 `docs/docs_en/`
- 兩次 build，分別輸出 `docs/site/` 與 `docs/site/en/`

!!! info "同頁切換實作"
    `Native Separate Builds` 下，Zensical 原生 `extra.alternate` 仍是站點層設定。
    為了讓語言 selector 保留目前頁的相對路徑，本專案使用原生 `extra_javascript` 載入 `docs/javascripts/language-switcher.js`，在 `/` 與 `/en/` 之間切換同一路徑。

!!! warning "切換邊界"
    - 未翻譯頁面不應假設有自動 fallback；若需要對稱路徑，請明確補齊 `docs/docs_en/` 對應頁。
    - 若調整語言根路徑（例如不再使用 `/en/`），必須同步更新 `extra.alternate` 與 `docs/javascripts/language-switcher.js`。
    - 若修改導覽，必須同步更新兩份 TOML，否則中英站的 Sidebar 會失去一致性。

---

## 檢查流程

### 本地預覽

```bash
uv run --group dev zensical serve -f zensical.toml
uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001
```

### 建置檢查

```bash
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml

# 或使用正式靜態建置腳本（若腳本仍保留）
./scripts/build_docs_sites.sh
```

!!! tip "常見問題"
    - 若本地無法直接執行 `zensical serve/build`，先確認專案根目錄同時存在 `zensical.toml` 與 `zensical.en.toml`。
    - 若 build 失敗並提示找不到頁面，先檢查你是否把變更寫進 `docs/docs_zhtw/` / `docs/docs_en/`，而不是只改了 `docs/` 根目錄。
    - 若雙語導覽異常，先檢查兩份 TOML 的 `nav` 是否仍保持一致。

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Docs Source**: edit `docs/docs_zhtw/` first, then mirror the same change into `docs/docs_en/`
- **No Staging Assumption**: `docs/docs_zhtw/` and `docs/docs_en/` are maintained source trees for the docs site
- **Config SoT**: site-level config is split across `zensical.toml` and `zensical.en.toml`
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: keep navigation and relative links aligned across both native configs
- **Architecture Term**: this repo uses `Native Separate Builds`
- **Language Switch**: `extra.alternate` defines locale roots; same-page switching depends on `docs/javascripts/language-switcher.js`
- **Verify**: `uv run --group dev zensical build -f zensical.toml` and `uv run --group dev zensical build -f zensical.en.toml` must pass
```
