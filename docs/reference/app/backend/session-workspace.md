---
aliases:
  - Backend Session Workspace Reference
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Backend session、workspace context 與 active dataset reference surface。
version: v0.5.0
last_updated: 2026-03-13
updated_by: team
---

# Session & Workspace

本頁定義 frontend app pages 依賴的 session / workspace surface。

!!! info "Surface Boundary"
    本頁負責 session state、workspace scope 與 active dataset binding。
    dataset browse、task lifecycle、characterization result 不屬於本頁責任。

!!! tip "Primary Consumers"
    主要消費者是 [Dashboard](../frontend/workspace/dashboard.md)、[Raw Data Browser](../frontend/workspace/raw-data-browser.md) 與 [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md)。

---

## 涵蓋範圍 (Coverage)

| Surface | 說明 |
| :--- | :--- |
| **Session State** | 使用者作業階段狀態 |
| **Active Dataset Context** | 目前啟用中的資料集上下文 |
| **Capability Exposure** | 權限與能力曝露 |
| **Workspace Identity** | 與 workspace 綁定的身份識別語意 |

---

## Surface Contracts

=== "Active Dataset Binding"

    active dataset surface 至少必須支援：

    | 操作 | 職責 |
    | :--- | :--- |
    | **讀取** | 讀取目前 session 綁定的 dataset。 |
    | **切換** | 進行 active dataset 的變更。 |
    | **更新** | mutation 後讓 frontend 能立即重讀最新 session state。 |

=== "Capability Exposure"

    | 規則 | 說明 |
    | :--- | :--- |
    | **Workspace-scoped** | frontend 可見能力必須由 workspace / session scope 決定。 |
    | **No page-local guessing** | frontend page 不得自行推斷 capability exposure。 |
    | **Cross-page consistency** | 同一 session 內各頁讀到的 active dataset 必須一致。 |

!!! warning "Single Session Authority"
    app pages 讀到的 active dataset 必須來自**同一份 session / workspace authority**。
    frontend 不得各頁各自維護分叉的 dataset 選擇。

---

## Delivery Rules

| 項目 | 規則 |
| :--- | :--- |
| **Session Read** | page refresh 後必須能重建 active dataset 與 workspace scope。 |
| **Capability Exposure** | frontend 可見能力必須由 **workspace / session scope** 決定，不可在頁面自行猜測。 |
| **Cross-page Consistency** | Dashboard、Raw Data、Circuit Simulation 讀到的 active dataset 必須保持一致。 |
| **Mutation Propagation** | dataset switch 後，各 page consumer 應能重建同一份最新 session context。 |

---

## Related

- [Dashboard](../frontend/workspace/dashboard.md)
- [Circuit Simulation](../frontend/research-workflow/circuit-simulation.md)
- [Identity / Workspace Minimal Model](../../architecture/identity-workspace-model.md)
- [Datasets & Results](datasets-results.md)
