---
aliases:
  - "Documentation Design"
  - "文件設計規範"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
status: stable
owner: docs-team
audience: team
scope: "文件設計規範索引：Standards / Style / Maintenance"
version: v0.6.0
last_updated: 2026-02-28
updated_by: docs-team
---

# Documentation Design

文件設計規範索引，確保文件的一致性與可維護性（對齊本專案 `Native Separate Builds` 架構）。

---

## 快速參考

| 規範 | 說明 | Agent Rule |
|------|------|------------|
| [Standards](standards.md) | Diataxis + Frontmatter + 核心規則 | [#agent-rule](standards.md#agent-rule) |
| [Style](style.md) | 語氣/風格 + 視覺元素（Admonitions/Tabs/Mermaid） | [#agent-rule](style.md#agent-rule) |
| [Maintenance](maintenance.md) | 雙語同步 + Frontmatter 更新 + Zensical 檢查 | [#agent-rule](maintenance.md#agent-rule) |
| [Explanation Physics](explanation-physics.md) | Explanation/Physics 教學定位、章節骨架與跨文件引用規則 | [#agent-rule](explanation-physics.md#agent-rule) |

---

## 正式術語

本專案在文件層的雙語站點架構，正式名稱為：

- `Native Separate Builds`

此術語代表：

- 使用兩份原生設定檔：`zensical.toml`（zh-TW）與 `zensical.en.toml`（en）
- 使用兩次原生 build，分別輸出到 `/` 與 `/en/`
- 使用成對的 `.md` / `.en.md` 內容頁，並在建置前產生 `docs_zh/` / `docs_en/`
- 使用同一路徑的語言切換，且兩個語言的站點殼層由各自 build-time 產生

---

## Related

- 視覺圖表：
  - [Circuit Diagram Guide](../../../how-to/contributing/circuit-diagrams.md)（Schemdraw → SVG）
- CLI 文件：
  - [CLI Docs Automation](../../../how-to/contributing/cli-docs-automation.md)

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Design
- **Standards**: Diataxis + Frontmatter/Tags + 核心規則（見 `standards.md`）
- **Style**: 語氣/風格 + 視覺元素（Admonitions/Tabs/Mermaid）（見 `style.md`）
- **Maintenance**: 雙語同步 + Frontmatter 更新 + Zensical 檢查（見 `maintenance.md`）
- **Explanation Physics**: 教學定位、章節骨架、跨文件引用規範（見 `explanation-physics.md`）
- **Architecture Term**: 本專案雙語文件架構的正式名稱是 `Native Separate Builds`
- 詳細規範請以各子文件為準。
```
