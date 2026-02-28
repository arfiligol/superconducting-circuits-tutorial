---
aliases:
  - Live Preview Domain Semantics Profiles
  - Live Preview 領域語意設定檔
tags:
  - diataxis/explanation
  - audience/team
  - topic/architecture
  - topic/visualization
status: draft
owner: docs-team
audience: team
scope: Qubit/JPA/JTWPA/Quantum Memory 的 preview 語意設定與分文件決策
version: v0.1.1
last_updated: 2026-02-27
updated_by: docs-team
---

# Live Preview Domain Semantics Profiles

本頁定義超導電路領域語意（domain-specific semantics）如何映射到 Live Preview，並約束何時拆分成多份領域文件。

## Positioning

### Corpus Density Snapshot (2026-02-27)

| Keyword Group | Hits in docs/ |
|---|---:|
| `JTWPA` | 12 |
| `JPA / parametric amplifier` | 26 |
| `Qubit / transmon / fluxonium` | 55 |
| `SQUID / Josephson / junction` | 265 |
| `Quantum Memory / cat qubit` | 0 |

!!! info "分文件決策（目前）"
    目前維持單一 profiles 文件，不拆成四份：  
    1) Qubit/JPA/JTWPA 有足夠素材；2) Quantum Memory 幾乎無案例；3) 先集中契約可降低漂移與維護成本。

## Profile Contract

每個 domain profile 至少需包含以下欄位：

| 欄位 | 用途 |
|---|---|
| `recognition_signals` | 拓樸/命名辨識訊號 |
| `visual_grammar` | 使用者應該看到的結構語法 |
| `hard_constraints` | 不可破壞規則 |
| `soft_preferences` | 可調整偏好 |
| `validation_cases` | 回歸測試案例 |

## Domain Profiles

!!! example "Profile A: JTWPA / JJTWPA"
    `recognition_signals`  
    - 主幹連續串聯（`L*` / `Lj*`）  
    - 重複 cell + 對地 shunt（`C*`, `Cj*`）  
    - 節點沿主幹單調推進  

    `visual_grammar`  
    - 必須呈現 ladder cell 節奏  
    - 主幹水平連續  
    - shunt 垂直落地  

    `hard_constraints`  
    - cell pitch 一致（可允許小幅誤差）  
    - bridge 僅在不可避免衝突啟用  
    - `Lj` 與 `Cj` 值標不可互蓋  

    `validation_cases`  
    - `JTWPA (10~20 cells)`  
    - `Floquet JTWPA with Dissipation`

!!! example "Profile B: JPA / SQUID Amplifier"
    `recognition_signals`  
    - 輸入/輸出 port + 中央非線性核心（`Lj*`/SQUID 等價結構）  
    - pump/readout 支路並存  
    - 常見 shunt resistor 與耦合電容  

    `visual_grammar`  
    - 入口/出口可辨  
    - 非線性核心為視覺重心  
    - pump 支路與 signal path 可分辨  

    `hard_constraints`  
    - port 邊界標籤不可碰撞  
    - 核心元件標籤優先保證可讀  
    - 節點保持單次標註  

    `validation_cases`  
    - `Flux-pumped JPA`  
    - `Double-pumped JPA`

!!! example "Profile C: Qubit + Readout"
    `recognition_signals`  
    - qubit 非線性元件與 readout resonator 共存  
    - 耦合元件位於兩子系統之間  
    - 驅動/讀出線路可能分離  

    `visual_grammar`  
    - qubit 子電路與 readout 子電路分區可辨  
    - coupling 元件位置明確  
    - 不把兩子系統畫成單一路徑  

    `hard_constraints`  
    - coupling 標記不可模糊（元件名/值）  
    - 子系統主幹保持可追蹤  

    `validation_cases`  
    - `Floating Qubit` 相關案例  
    - `Qubit structure resonance map` 對應結構

!!! warning "Profile D: Quantum Memory (Provisional)"
    目前資料不足，先保留 profile 介面。  
    在缺乏可重現案例前，不可覆寫 A/B/C 的既有規則。  
    目前 validation case 暫缺。

## Shared Rules and Split Criteria

!!! success "Shared Semantic Rules"
    1. `value_ref -> parameters` 綁定規則  
    2. node 單次標註  
    3. 禁止 wire 穿模  
    4. 大圖可 zoom/pan 檢視

!!! tip "Split Criteria（何時拆成多份領域文件）"
    下列條件需同時成立：  
    1) 該領域至少 3 個穩定可重現案例  
    2) 至少 2 條與其他領域衝突的專屬規則  
    3) 已有獨立回歸測試（含至少 1 個視覺壓力測試）

## Related

- [Circuit Schema Live Preview](circuit-schema-live-preview.md)
- [Dataset Schema Design](schema-design.md)
- [Data Formats / Circuit Netlist](../../../reference/data-formats/circuit-netlist.md)
