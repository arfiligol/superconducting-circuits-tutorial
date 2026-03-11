---
aliases:
  - Code Quality
  - 程式碼品質規範
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Code quality、型別、架構邊界、契約版本與錯誤模型索引。
version: v1.1.0
last_updated: 2026-03-12
updated_by: codex
---

# Code Quality

本區定義 rewrite branch 的程式品質規範。
重點不是追求框架技巧，而是讓 UI、API、CLI 與科學核心可以穩定共演化。

- [Code Style](./code-style.md)
- [Type Checking](./type-checking.md)
- [Design Patterns](./design-patterns.md)
- [Script Authoring](./script-authoring.md)
- [Data Handling](./data-handling.md)
- [Logging](./logging.md)
- [Contract Versioning](./contract-versioning.md)
- [Error Handling](./error-handling.md)

## Agent Rule { #agent-rule }

```markdown
## Code Quality
- 遵循 Clean Code：命名清晰、函式短小、責任單一。
- UI、API、CLI 不得各自複製業務流程；共享規則應集中在 backend services 或 `src/core/`。
- 優先修正程式碼而不是增加例外或忽略規則。
- 需要時查閱子文件：Code Style / Type Checking / Design Patterns / Script Authoring / Data Handling / Logging / Contract Versioning / Error Handling。
```
