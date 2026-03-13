---
aliases:
  - Core Blueprint
  - sc_core 藍圖
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/architecture
status: draft
owner: docs-team
audience: team
scope: 說明 sc_core 的責任邊界、canonical contracts 與 adoption roadmap。
version: v0.1.0
last_updated: 2026-03-12
updated_by: codex
---

# Core Blueprint

`sc_core` 是本專案的共享核心邊界。
它不是單純的 utility library，而是 canonical contracts 與共享計算規則的中心。

## What sc_core Owns

`sc_core` 應逐步擁有下列能力：

- circuit definition canonical invariants
- task routing / execution contracts
- storage / provenance canonical handles
- simulation orchestration
- characterization / analysis shared helpers
- trace / dataset canonical semantics

## What sc_core Must Not Own

以下內容不得放進 `sc_core`：

- FastAPI router / schema / HTTP transport
- Next.js page / component / UI state
- Typer command / CLI presenters
- Electron IPC / desktop runtime concerns
- database driver / ORM-specific code

## Target Module Shape

```text
src/core/sc_core/
├── circuit_definitions/
├── tasking/
├── execution/
├── storage/
├── simulation/
├── characterization/
├── traces/
└── datasets/
```

## Adoption Roadmap

### Current

- circuit definition inspection / normalization
- task routing
- execution contracts
- storage / provenance contracts

### Next

- backend task/result/storage adapter semantics 逐步改用 shared value objects
- worker runtime 進一步依賴 shared execution/storage helpers
- CLI commands 以 `sc_core` 為主要 compute consumer

### Later

- simulation orchestration
- characterization helpers
- trace / dataset canonical transforms

## Dependency Direction

1. `sc_core` 可以被 backend / worker / CLI 使用
2. `sc_core` 不得依賴 backend / frontend / CLI / desktop
3. adapter 層應將自己的 transport/persistence 狀態映射到 `sc_core` contracts

## Legacy Migration Rule

既有 `src/core/` legacy modules 不應一次全部重寫。
遷移原則是：

- 先抽出最穩定、最 canonical 的 contract 與 helper
- 再逐步讓 backend / worker / CLI adopt
- 避免為了追求結構整齊而做 sweeping move

## Related

- [Canonical Contract Registry](./canonical-contract-registry.md)
- [Task Semantics](./task-semantics.md)
- [Parity Matrix](./parity-matrix.md)
