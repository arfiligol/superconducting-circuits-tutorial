---
aliases:
  - Project Basics
  - 專案基礎規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/project-basics
status: stable
owner: docs-team
audience: contributor
scope: 定義 rewrite branch 的專案目標、技術方向、結構與單一真理順序索引。
version: v1.2.0
last_updated: 2026-03-12
updated_by: codex
---

# Project Basics

本區定義目前 branch 的基礎共識：產品範疇、技術選型與 repo 結構。
任何會影響整體開發方向的修改，都應先更新這些文件。

- [Project Overview](./project-overview.md)
- [Tech Stack](./tech-stack.md)
- [Folder Structure](./folder-structure.md)
- [Backend Architecture](./backend-architecture.md)
- [Source of Truth Order](./source-of-truth-order.md)

## Agent Rule { #agent-rule }

```markdown
## Project Basics
- Project Basics 定義 rewrite branch 的使命、範疇、技術棧與結構。
- 任何影響整體協作與架構一致性的變更，必須先更新本區。
- 目前 UI 方向為 Next.js，API 方向為 FastAPI，CLI 必須保留且與核心能力一致。
- backend 的責任邊界與內部藍圖由 `backend-architecture.md` 定義。
- 舊的 NiceGUI 程式碼視為 migration legacy，不應再成為新功能的預設落點。
```
