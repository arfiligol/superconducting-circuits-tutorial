---
aliases:
  - "Explanation Physics Guardrail"
  - "Explanation 物理規範"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
  - topic/physics
status: stable
owner: docs-team
audience: team
scope: "Explanation/Physics 的教學定位、章節骨架與跨文件引用規範"
version: v0.2.0
last_updated: 2026-02-16
updated_by: docs-team
---

# Explanation Physics

本文件定義 `docs/explanation/physics/` 的寫作框架，確保內容可「完整從頭學」也可「中途切入」。

---

## 教學定位（必須同時成立）

1. **主幹課程（Backbone）**
   - 從基礎物理一路連到超導量子電路工程語境。
   - 目標讀者：修過四大力學的物理系學生（含複習需求）。
2. **可引用節點（Reusable nodes）**
   - 每篇可被 Tutorial / How-to / Reference 單獨引用。
   - 讀者不需先讀完整套內容才能進入特定主題。

!!! warning "Diataxis 邊界"
    Explanation 只回答「為什麼/如何理解」，不提供命令式操作步驟（那是 How-to/Tutorial）。

## 問題驅動優先（Physics Q&A First）

- 每篇 Physics 必須由一個**物理問題句**作為標題或開場（例如：為什麼磁通量子化？）。
- 問題本身應偏向物理因果，不以「工具怎麼用」或「流程怎麼做」為主。
- 工程內容只作為物理概念的落地映射，不可喧賓奪主。

!!! tip "歷史與應用提示（建議）"
    每篇至少放一個 Admonition，說明該物理概念在社群歷史上解決過的關鍵問題或典型應用，培養「理解 + 應用」的連結。

---

## 內容起點與深度邊界

### 起點（固定）

- 以「**單一超導體可由一個宏觀波函數描述**」作為超導段落起點。
- 可使用序參量（order parameter）記法，但需清楚說明相位與振幅的物理意義。

### 邊界（避免過度展開）

- 不要求完整 BCS 或凝態場論推導。
- 必須交代足以支持工程建模的最小物理鏈條：
  1. 宏觀波函數/相位
  2. Josephson 關係
  3. 電路等效（L/C/非線性項）
  4. 可量測工程量（頻率、阻抗、雜訊、增益、靈敏度等）

---

## 章節架構規範（Physics 子章節）

每篇 `docs/explanation/physics/*.md` 建議遵循以下骨架：

1. **本章回答的問題**：用 1–2 句定義核心問題（例如：為何非線性電感可形成參數放大）。
2. **先備知識對照**：對應四大力學中的先備觀念（量子/電磁/熱統/古典）。
3. **物理核心**：最小必要方程式與假設；所有符號需定義，單位需一致。
4. **工程映射**：將物理量映射到電路與系統設計量（元件、參數、量測可觀測量）。
5. **限制與近似**：明確寫出模型適用範圍與失效條件。
6. **跨文件導航**：依內容相關性提供 1–3 個延伸連結（可為 Tutorial、How-to、Reference、Design Decisions；不強制同時具備）。

## 學術引用與可靠性 (Citations & Reliability)

所有涉及核心物理推導、近似模型（如 CPZM）或工程擬合公式的段落，都**必須附上參考文獻**。
- 格式：文件底部需建立 `## References` 區塊，建議使用 **APA 格式**。
- 連結寫法：若有 DOI 或 arXiv 連結，應以 Markdown 形式附上（如 `[arXiv](link)`)，方便讀者追溯。

---

## 全域敘事路徑（維持一致性）

`Explanation/Physics` 的主路徑應維持由淺入深：

1. 超導宏觀描述（單一超導體波函數）
2. Josephson 元件與非線性來源
3. 電路模型與共振/參數耦合
4. 量測模型（S/Z/Y、共振擷取、雜訊/增益）
5. 與實際工程流程的介面（校準、設計取捨、操作點）

若新增頁面，需說明其位於主路徑的哪一層，並補齊前後連結。

---

## 可中途切入規範

每篇 Physics Explanation 應提供：

- **你可以從這裡開始**：適合直接閱讀的前置條件清單
- **若要補背景，請先讀**：1–3 個回補連結
- **如果你只想做任務**：導向對應 Tutorial/How-to

---

## 與其他 Diataxis 類型的關係

- `Explanation`：建立理解框架（why/how it works）
- `Tutorials`：提供完整學習路徑中的實作練習
- `How-to`：解決單點任務
- `Reference`：提供可查證規格、公式、CLI 與資料格式

Physics Explanation 必須同時具備：

- 可獨立閱讀（概念完整）
- 可被外部頁面引用（節點清楚）

---

## Agent Rule { #agent-rule }

```markdown
## Explanation Physics
- **Positioning**: `docs/explanation/physics/` must be both a full learning backbone and reusable concept nodes
- **Audience**: physics students with four-core-physics background; support bridging + review
- **Start point**: begin superconductivity from a single-superconductor macroscopic wavefunction
- **Depth boundary**: no full BCS derivation; include minimum chain: wavefunction/phase -> Josephson relations -> circuit equivalent -> measurable engineering quantities
- **Per-page contract**: question, prerequisites mapping, physics core equations/assumptions, engineering mapping, limits/approximations, cross-links
- **Cross-links**: provide 1-3 relevant links chosen by concept fit (Tutorial/How-to/Reference/Design Decisions); no mandatory pair
- **Narrative consistency**: place each page in the global path and maintain prev/next conceptual links
- **Diataxis boundary**: Explanation explains reasoning, not command-style procedures
- **Question-driven**: each page starts from a physics question, not an engineering operation question
- **Admonition usage**: include at least one history/application admonition per page
- **Citations**: physics models, equations, and engineering derivations MUST include references (APA format) at the bottom of the document.
```
