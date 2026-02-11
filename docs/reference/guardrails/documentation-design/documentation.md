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
version: v0.2.0
last_updated: 2026-02-08
updated_by: docs-team
---

# Documentation Design

文件設計規範索引，確保文件的一致性與可維護性（對齊本專案 Zensical + i18n 設定）。

---

## 快速參考

| 規範 | 說明 | Agent Rule |
|------|------|------------|
| [Standards](standards.md) | Diataxis + Frontmatter + 核心規則 | [#agent-rule](standards.md#agent-rule) |
| [Style](style.md) | 語氣/風格 + 視覺元素（Admonitions/Tabs/Mermaid） | [#agent-rule](style.md#agent-rule) |
| [Maintenance](maintenance.md) | 雙語同步 + Frontmatter 更新 + Zensical 檢查 | [#agent-rule](maintenance.md#agent-rule) |

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
- 詳細規範請以各子文件為準。
```
