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
version: v0.5.0
last_updated: 2026-02-28
updated_by: docs-team
---

# Documentation Maintenance

本文件定義文件維護流程（雙語同步、更新規則、檢查清單）。

---

## 雙語同步（必須）

本專案採用 **單一原生設定檔**：

- 設定檔：`zensical.toml`
- 文件原始碼：`.md` 與 `.en.md` 並存
- 網站導覽與站點層設定：以 `zensical.toml` 為唯一真理來源

!!! info "原生 Zensical 寫法"
    文件規範全面採用 Zensical 原生 `zensical.toml`。  
    不再以舊版 YAML 雙設定檔作為維護標準，也不再以「雙設定檔」作為文件流程基礎。

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

## 原生 Zensical 盤點（文件層）

從文件維護角度，切換到原生 `zensical.toml` 時，必須同步修正以下四類資訊：

1. 所有文件指令改為以單一 `zensical.toml` 為前提（不再使用舊版明示 YAML 設定檔的寫法）。
2. 所有維護說明改為「單一設定檔」，不再描述舊版雙設定檔同步。
3. 所有導覽維護規則改為「更新 `zensical.toml`」，不再要求兩份 `nav:` 對稱維護。
4. 所有 CI / README / Contributing 文件必須與上述指令一致，避免使用者依舊沿用 MkDocs 相容流程。

---

## 導覽與連結維護

新增/移動文件時：

1. 更新 `zensical.toml` 中的導覽與站點層設定
2. 檢查所有相對連結（`.en.md` 仍需維持對應語言版本的正確連結）
3. 若文件為 SoT，確認 `tags` 含 `sot/true`

---

## Native Single-Build Bilingual Pages

本專案目前的正式架構名稱為：

- `Native Single-Build Bilingual Pages`

其技術特徵為：

- 單一原生設定檔：`zensical.toml`
- 雙語來源檔：`.md` 與 `.en.md` 成對
- 原生語言 selector：使用 `extra.alternate` 提供站點層 fallback

!!! info "同頁切換實作"
    `Native Single-Build Bilingual Pages` 下，Zensical 原生 `extra.alternate` 只提供站點層連結，不能直接宣告「目前頁面的對應語言頁」。  
    為了在不使用 MkDocs 外掛的前提下提供同頁切換，本專案使用原生 `extra_javascript` 載入 `docs/javascripts/language-switcher.js`，在前端依據 `.md` / `.en.md` 的實際成對關係改寫語言 selector。

!!! warning "切換邊界"
    - 若某頁缺少對應 `.en.md`（或 `.md`），selector 會保留站點首頁 fallback。
    - 這個做法只解決「內容頁路由切換」；站點 chrome（例如主題語言、系統文案、單一 nav 標籤）仍只有一個 canonical language。
    - 若未來需要完整的中英 UI 殼層切換，應改採原生 Separate Builds（每種語言各自一個 native config / build）。
    - 若新增、刪除或搬移 `.md` / `.en.md` 頁面，必須同步更新 `docs/javascripts/language-switcher.js` 內的路由對照表。

---

## 檢查流程

### 本地預覽

```bash
uv run --group dev zensical serve
```

### 建置檢查

```bash
uv run --group dev zensical build
```

!!! tip "常見問題"
    - 若本地無法直接執行 `zensical serve/build`，先確認專案根目錄存在 `zensical.toml`。
    - 若雙語導覽異常，先檢查 `zensical.toml` 的導覽來源與語言設定是否仍符合文件結構。

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Single Config SoT**: all site-level config and navigation changes go through `zensical.toml`
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: keep navigation and relative links aligned with the single config model
- **Architecture Term**: this repo uses `Native Single-Build Bilingual Pages`, not Separate Builds
- **Language Switch**: `extra.alternate` is site-level fallback; same-page switching depends on `docs/javascripts/language-switcher.js`
- **Verify**: `uv run --group dev zensical build` must pass
```
