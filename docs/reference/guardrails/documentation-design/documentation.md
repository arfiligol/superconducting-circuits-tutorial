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
version: v0.7.0
last_updated: 2026-03-12
updated_by: codex
---

# Documentation Design

文件設計規範索引，確保文件的一致性與可維護性（對齊本專案 `Native zh-TW Build` 架構）。

---

## 快速參考

| 規範 | 說明 | Agent Rule |
|------|------|------------|
| [Standards](standards.md) | Diataxis + Frontmatter + 核心規則 | [#agent-rule](standards.md#agent-rule) |
| [Style](style.md) | 語氣/風格 + 視覺元素（Admonitions/Tabs/Mermaid） | [#agent-rule](style.md#agent-rule) |
| [Maintenance](maintenance.md) | 單語來源樹 + Frontmatter 更新 + Zensical 檢查 | [#agent-rule](maintenance.md#agent-rule) |
| [Explanation Physics](explanation-physics.md) | Explanation/Physics 教學定位、章節骨架與跨文件引用規則 | [#agent-rule](explanation-physics.md#agent-rule) |

---

## 正式術語

本專案在文件層的站點架構，正式名稱為：

- `Native zh-TW Build`

此術語代表：

- 使用單一設定檔：`zensical.toml`
- 使用單一 build，輸出到 `/`
- 編輯來源為 `docs/`，建置前產生 `docs/docs_zhtw/` staging tree
- 不再維護英文站點與 `.en.md` 對應頁

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
- **Maintenance**: 單語來源樹 + Frontmatter 更新 + Zensical 檢查（見 `maintenance.md`）
- **Explanation Physics**: 教學定位、章節骨架、跨文件引用規範（見 `explanation-physics.md`）
- **Architecture Term**: 本專案文件架構的正式名稱是 `Native zh-TW Build`
- 詳細規範請以各子文件為準。
```
