---
aliases:
  - Type Checking
  - 類型檢查
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Python 與 TypeScript 的型別檢查規範。
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Type Checking

型別規範的目的不是追求表面上的零警告，而是讓 UI、API、CLI 與科學核心的資料契約保持穩定。

## Python

- 工具：`basedpyright`
- 基線：`basic`，但視為 mandatory
- 所有函式都要標註參數與回傳值
- 使用 `list[str]`、`dict[str, float]`、`str | None`
- 非必要不使用 `Any`

### Allowed Exceptions

- 第三方科學套件無型別時，可使用最小範圍 `# type: ignore`
- 需要附上原因，不可整檔大面積忽略

## TypeScript

- 使用 `strict: true`
- service、schema、component props、hook 回傳值需有清楚型別
- 禁止把未驗證的 API payload 直接當成可信任資料
- `zod` 或等效 schema 驗證後的型別，才可進入 UI 業務流程

## Fix Policy

- 有型別錯誤時先修正程式碼
- 只有在第三方型別缺失且修復成本不合理時，才接受局部忽略

## Agent Rule { #agent-rule }

```markdown
## Type Checking
- **Python**:
    - use BasedPyright
    - treat `basic` mode as mandatory
    - type all function parameters and return values
    - use modern syntax like `list[str]` and `str | None`
    - avoid `Any` unless dealing with untyped third-party code
- **TypeScript**:
    - use strict mode
    - do not trust raw API payloads without schema validation
    - keep service, schema, hook, and component contracts typed
- **Fix policy**:
    - fix the code first
    - use `# type: ignore` only in the smallest justified scope
```
