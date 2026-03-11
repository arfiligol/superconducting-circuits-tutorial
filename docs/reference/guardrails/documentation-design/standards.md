---
aliases:
  - "Documentation Standards"
  - "文件規範"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
status: stable
owner: docs-team
audience: team
scope: "Diataxis 分類邊界、Frontmatter/Tags 規格與文件核心規則"
version: v0.2.0
last_updated: 2026-03-12
updated_by: codex
---

# Documentation Standards

本文件定義本專案文件撰寫的核心規則與結構規範（Diataxis + Metadata + 核心約束）。

---

## Diataxis 框架

| 分類 | 目錄 | 目標 | 導向 |
|------|------|------|------|
| Tutorials | `docs/tutorials/` | 學習 | 導師引導 |
| How-to | `docs/how-to/` | 解決問題 | 任務導向 |
| Reference | `docs/reference/` | 資訊 | 技術導向 |
| Explanation | `docs/explanation/` | 理解 | 概念導向 |

### 分類邊界

=== "Tutorials"

    !!! tip "適用情境"
        讓新加入者「跟著做就成功」。

    - ✅ 明確前置條件、逐步操作、可驗證結果
    - ❌ 完整規格、決策背景、設計辯證

=== "How-to"

    !!! tip "適用情境"
        解決特定問題或完成單一任務。

    - ✅ 步驟清楚、最短路徑
    - ❌ 教學式鋪陳、規格列舉、決策理由

=== "Reference"

    !!! note "適用情境"
        提供可被引用的「規格與事實」。

    - ✅ 條列清楚、完整、可查找
    - ❌ 背景動機、教學步驟、使用情境故事

=== "Explanation"

    !!! info "適用情境"
        解釋「為什麼這樣設計」。

    - ✅ 概念釐清、設計取捨、原則與理由
    - ❌ 操作步驟、完整規格、命令式指令

---

## Frontmatter 規格

本專案文件普遍採用以下 YAML Frontmatter（對齊目前 `docs/` 的既有樣式）：

| Property | Required | Format |
|----------|----------|--------|
| `aliases` | ✅ | 字串陣列 |
| `tags` | ✅ | 字串陣列（需符合 Tag Taxonomy） |
| `status` | ✅ | `draft` / `incubating` / `stable` / `deprecated` |
| `owner` | ✅ | `team` 或 `team/person` |
| `audience` | ✅ | `team` / `contributor` / `user` |
| `scope` | ✅ | 摘要文件涵蓋範圍 |
| `version` | ✅ | `vX.Y.Z` |
| `last_updated` | ✅ | `YYYY-MM-DD` |
| `updated_by` | ✅ | `team` 或 `team/person` |

!!! warning "人名驗證規則"
    `owner` 與 `updated_by` 中提及的**人名**必須存在於 [貢獻者名錄](../../contributors.md)。新增貢獻者時，請先更新名錄再引用。

---

## Tag Taxonomy

Tags 採用 `namespace/value` 格式。

| 前綴 | 用途 | 範例 |
|------|------|------|
| `diataxis/*` | Diataxis 分類 | `diataxis/reference` |
| `audience/*` | 目標受眾 | `audience/team` |
| `sot/*` | 是否為權威來源 | `sot/true` |
| `topic/*` | 主題標籤 | `topic/documentation` |

---

## 核心規則

!!! warning "違反會造成文件一致性下降（且可能讓 CI/Zensical 檢查更難維護）"

| 規則 | 說明 |
|------|------|
| Diataxis 分類 | 內容必須符合對應分類邊界（避免混雜） |
| 連結格式 | 內部連結使用標準 Markdown（相對路徑） |
| 專有名詞 | 優先保留英文或中英並列（例如：導納 (Admittance)） |
| SoT 標記 | 權威文件標記 `sot/true` |
| 禁止模糊時間 | 禁用「未來」「後續」「即將」等；請寫明確日期（例如：`2026-01-30`） |

---

## 參考規範

- [Documentation Style](./style.md)
- [Documentation Maintenance](./maintenance.md)

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Standards
- **Diataxis**: Tutorials / How-to / Reference / Explanation；內容不可混類型
- **Frontmatter**: aliases, tags, status, owner, audience, scope, version, last_updated, updated_by
- **owner/updated_by**: `team` 或 `team/person`；人名需在 contributors registry
- **Tags**: `diataxis/*`, `audience/*`, `sot/*`, `topic/*`
- **SoT**: 權威文件標 `sot/true`
- **No vague time**: 禁用「未來/後續/即將」等，請寫明確日期
```
