---
aliases:
  - "Contract Versioning"
  - "契約版本策略"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: team
scope: "定義 canonical contracts、資料格式與 adapter payload 的版本與相容性策略"
version: v1.1.0
last_updated: 2026-03-12
updated_by: codex
---

# Contract Versioning

本文件定義 migration 期間 contract 演進的最低要求，避免 `sc_core`、backend、CLI、frontend 之間各自演化。

## Contracts That Must Be Version-Aware

- circuit definition / netlist canonical contract
- dataset / trace / result / provenance contracts
- task submission / task detail / task result contracts
- session / workspace context payloads
- machine-consumable CLI output contracts

## Version Fields

| Contract 類型 | 最低要求 |
| --- | --- |
| persisted data contract | 明確 `schema_version` 或等價欄位 |
| API payload contract | route-level version note 或明確 lockstep branch policy |
| CLI machine output | command docs 中記錄版本或穩定輸出保證 |
| task/result handle | 必須可追到 result/provenance contract 版本 |

## Compatibility Classes

- **Additive**：新增可選欄位、附加 metadata、保留舊欄位語意
- **Soft-breaking**：欄位仍存在，但預設值、排序、空值語意改變
- **Breaking**：刪除欄位、改型別、改必要欄位、改 enum / lifecycle 語意

## Persisted Data Rules

- SQLite metadata、TraceStore payload、export artifact 不得在沒有 fallback 的情況下直接破壞舊資料可讀性
- 若 persistence contract 需要 breaking change，至少要有下列其一：
  - migration script
  - read-compat fallback
  - one-time rebuild strategy，且在 parity matrix 記錄影響範圍
- `sc_core` 與 backend 不得各自維護不同版本解讀規則

## Compatibility Rules

- **Additive changes are preferred**
- **Breaking changes require an explicit note**：
  任何 breaking contract 變更都必須同步更新 reference docs、parity matrix、contract registry 與 fallback/migration notes。
- **Migration branch is lockstep by default**：
  migration 期間不承諾 frontend/backend/cli 與 `sc_core` 的跨 minor 版本相容。
- **Persisted data needs fallback semantics**
- **Do not fake compatibility**

## Required Update Set for Breaking Changes

任何 breaking contract 變更，都必須在同一交付線更新：

1. reference docs
2. [Parity Matrix](../../architecture/parity-matrix.md)
3. [Canonical Contract Registry](../../architecture/canonical-contract-registry.md)
4. fallback / migration notes
5. 對應測試

## Agent Rule { #agent-rule }

```markdown
## Contract Versioning
- Treat circuit definitions, dataset/trace/result contracts, task contracts, session/workspace payloads, and machine-readable CLI outputs as version-aware surfaces.
- Prefer additive evolution over breaking changes.
- Any breaking contract change MUST update:
    - reference docs
    - parity matrix
    - contract registry
    - fallback/migration notes
- During migration, assume frontend/backend/cli/`sc_core` evolve in lockstep on the same branch unless an explicit compatibility promise is documented.
- Persisted DB/TraceStore/exported data MUST have fallback, migration, or read-compat semantics before breaking a contract.
- Do not hide compatibility patches only inside adapters; document them.
```
