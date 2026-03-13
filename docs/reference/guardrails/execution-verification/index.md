---
aliases:
  - Execution & Verification
  - 執行與驗證
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/execution
status: stable
owner: docs-team
audience: contributor
scope: build、lint、test、CI 與 migration phase 驗收規範索引。
version: v1.1.0
last_updated: 2026-03-12
updated_by: codex
---

# Execution & Verification

本區定義 rewrite branch 的執行與驗證基準。
若新規則與現有腳本暫時不一致，應視為 migration task，而不是放棄規則的理由。

- [Build Commands](./build-commands.md)
- [Linting & Formatting](./linting.md)
- [Testing](./testing.md)
- [CI Gates](./ci-gates.md)
- [Commit Standards](./commit-standards.md)
- [Phase Gates](./phase-gates.md)
- [Prompt Grading](./prompt-grading.md)

## Agent Rule { #agent-rule }

```markdown
## Execution & Verification
- 定義 build、lint、type-check、test、CI 的 workspace 基線。
- 變更程式碼時，優先執行與 touched area 直接相關的檢查。
- rewrite branch 最終基線包含 frontend、backend、CLI、docs 四條驗證線。
- migration phases 需搭配 Phase Gates 與 parity matrix 驗收。
```
