---
aliases:
- Pipeline Explanation
- 管線概念
tags:
- diataxis/explanation
- audience/team
- topic/architecture
- topic/pipeline
status: draft
owner: docs-team
audience: team
scope: 分析與可視化一體化管線的設計原則與資料流程
version: v0.2.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Pipeline

Pipeline 的核心不是把 Analysis 與 Visualization 拆成兩個階段，而是把它們視為同一個分析單元的兩種輸出（數值 + 圖像）。

!!! tip "統一原則"
    一次 analysis run 應同時產生可驗證的數值結果與可讀的視覺化結果。
    UI 與 CLI 的差異只在呈現通道，不在分析語意。

## Why This Matters

- 使用者不需要先完成抽象分析，再切換另一套心智模型看圖。
- 可避免 UI/CLI 兩條流程逐漸分岔，降低維護成本。
- 每個分析都能直接對應「看得見」的結果，有助 debug 與決策。

## Topics

- [Data Flow](data-flow.md) - 資料如何進入、執行分析並輸出視覺化
- [Preprocessing Rationale](preprocessing-rationale.md) - 為什麼仍需要 Dataset 標準化中間層

## Related

- [Architecture](../index.md) - 架構總覽
- [Circuit Simulation](../circuit-simulation/index.md) - 模擬相關設計決策
- [Data Formats](../../../reference/data-formats/index.md) - Schema 規格
