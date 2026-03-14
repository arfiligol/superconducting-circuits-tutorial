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
version: v1.2.0
last_updated: 2026-03-14
updated_by: codex
---

# Contract Versioning

本文件定義 migration 期間 contract 演進的最低要求，避免 `sc_core`、backend、CLI、frontend 之間各自演化。

!!! info "How to read this page"
    先判斷變更碰到哪一種 contract，再判斷變更類型是 additive、soft-breaking 還是 breaking。最後依照 required update set 補齊文件與測試。

## Decision Map

| 先回答 | 再決定 |
| --- | --- |
| 這是哪一類 contract？ | 需不需要 version-aware 欄位或 lockstep 說明 |
| 這是 additive 還是 breaking？ | 是否必須同步更新 registry / parity / migration notes |
| 這是 persisted data 嗎？ | 是否必須有 migration、fallback 或 rebuild 策略 |

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

| 類型 | 定義 | 預設處理 |
| --- | --- | --- |
| Additive | 新增可選欄位、附加 metadata、保留舊欄位語意 | 可接受，但仍需更新 reference |
| Soft-breaking | 欄位仍存在，但預設值、排序、空值語意改變 | 視為高風險，需同步寫明行為改變 |
| Breaking | 刪除欄位、改型別、改必要欄位、改 enum / lifecycle 語意 | 必須更新 registry / parity / migration notes / tests |

## Persisted Data Rules

- SQLite metadata、TraceStore payload、export artifact 不得在沒有 fallback 的情況下直接破壞舊資料可讀性
- 若 persistence contract 需要 breaking change，至少要有下列其一：
  - migration script
  - read-compat fallback
  - one-time rebuild strategy，且在 parity matrix 記錄影響範圍
- `sc_core` 與 backend 不得各自維護不同版本解讀規則

## Compatibility Rules

!!! warning "Do not fake compatibility"
    不要只在 adapter 裡偷偷補 patch，卻讓 registry、parity matrix、reference docs 看起來像完全相容。文件與實作必須同時承認 breaking reality。

| 規則 | 說明 |
| --- | --- |
| Additive changes are preferred | 先選不破壞既有 consumer 的演進方式 |
| Breaking changes require an explicit note | reference docs、parity matrix、contract registry 與 fallback/migration notes 必須同步更新 |
| Migration branch is lockstep by default | migration 期間不承諾 frontend/backend/cli 與 `sc_core` 的跨 minor 版本相容 |
| Persisted data needs fallback semantics | DB、TraceStore、export artifact 不能直接失去舊資料可讀性 |

## Required Update Set for Breaking Changes

任何 breaking contract 變更，都必須在同一交付線更新：

1. reference docs
2. [Parity Matrix](../../architecture/parity-matrix.md)
3. [Canonical Contract Registry](../../architecture/canonical-contract-registry.md)
4. fallback / migration notes
5. 對應測試

!!! tip "Fast check"
    如果你無法在同一交付線同時回答「舊資料怎麼讀、consumer 怎麼知道版本變了、哪些文件要更新」，就還不應該送出 breaking contract change。

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
