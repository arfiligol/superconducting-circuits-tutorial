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
scope: "Explanation/Physics 的知識架構、分層規則與寫作規範"
version: v1.0.0
last_updated: 2026-02-24
updated_by: team
---

# Explanation Physics

本文件定義 `docs/explanation/physics/` 的知識架構與寫作規範。

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

---

## 知識架構（A–J Roadmap）

`explanation/physics/` 的內容覆蓋範圍以下列 A–I 區塊為準。每個區塊代表一個知識領域；工具使用（G 區塊的操作面）與量測工程（H 區塊的操作面）屬於 How-to/Reference，不收錄在 Physics Explanation 中。

| 區塊 | 領域 | 節點類型 |
|------|------|----------|
| **A** | Foundations: The Four Pillars | Principle |
| **B** | Electromagnetics to Circuits | Model |
| **C** | Superconductivity & Dissipation | Principle / Model |
| **D** | Josephson Physics & Nonlinearity | Device / Model |
| **E** | Quantum Circuits Formalism | Model / Method |
| **F** | Core Building Blocks | Device |
| **G** | Design & Simulation (原理面) | Model / Method |
| **H** | Cryogenic RF Engineering (原理面) | Principle / Model |
| **I** | Experiments & Protocols (原理面) | Model / Method |

> **J. End-to-End Workflows** 歸屬於 `tutorials/`，不放在 Physics Explanation。

### Overview 頁面

`explanation/physics/index.md` 必須包含完整的 A–I 路線圖總覽，列出所有區塊與子主題。已有內容的子主題以超連結呈現；尚未建立的以純文字標記。

---

## 三層分層規則

```
explanation/physics/
├── index.md                           ← Overview（A–I 總覽）
├── foundations/                        ← L1：A 區塊
│   ├── index.md                       ← L1 Landing
│   ├── lagrangian-mechanics.md        ← L2：A1 主題
│   └── electromagnetic-energy.md      ← L2：A2 主題
├── superconductivity/                 ← L1：C 區塊
│   ├── index.md
│   ├── basics.md                      ← L2：C1
│   ├── loss-channels/                 ← L2→L3（當 C3 太大時拆分）
│   │   ├── index.md
│   │   ├── dielectric.md              ← L3
│   │   └── quasiparticles.md          ← L3
│   └── ...
```

### 規則

1. **L1（Sidebar 頂層子目錄）** = A–I 的大類領域（Foundations, EM-to-Circuits, Superconductivity...）
   - 每個 L1 是一個子目錄，含一個 `index.md` Landing Page
   - **只有當該 L1 底下有至少一篇 L2 頁面時，才建立該 L1 目錄與 Nav 項目**
2. **L2（子目錄內的頁面）** = 各大類底下的具體主題（A1, A2, C1, C2, C3...）
   - 預設每個主題一篇文件
3. **L3（選擇性細分）** = 只有當 L2 頁面內容過多（建議 > 3000 字）時，才可拆分為子目錄
   - L3 目錄需包含自己的 `index.md`
   - 不建議超過三層

---

## 內容邊界

### Physics 收錄

- 物理原理（why）
- 數學模型與推導（how it works）
- 工程映射：將物理量映射到電路設計量（元件值、可觀測量）
- 限制與近似條件

### Physics 不收錄（屬於其他 Diataxis 類型）

| 內容 | 歸屬 |
|------|------|
| CLI 操作步驟 | How-to |
| 軟體工具使用指南（HFSS, Python, Julia） | How-to |
| CLI 參數規格 | Reference |
| 端到端工作流程 | Tutorials |

---

## 節點類型（Frontmatter）

每篇 Physics 頁面的 frontmatter 應包含 `node_type`：

```yaml
tags:
  - node_type/principle    # 基礎原理（不依賴特定器件或工具）
  - node_type/model        # 可計算模型（方程、近似、邊界條件）
  - node_type/method       # 推導方法 / 數值方法
  - node_type/device       # 器件與元件描述
```

依賴方向：

- **Principle** 不依賴 Tool 或 Device
- **Model** 可依賴 Principle，不依賴特定 Device
- **Device** 必須指出依賴的 Model（例：SQUID 依賴 D1+D2+B5）
- **Method** 可依賴 Model + Principle

---

## 問題驅動優先（Physics Q&A First）

- 每篇 Physics 必須由一個**物理問題句**作為標題或開場。
- 問題本身應偏向物理因果，不以「工具怎麼用」或「流程怎麼做」為主。
- 工程內容只作為物理概念的落地映射，不可喧賓奪主。

!!! tip "歷史與應用提示（建議）"
    每篇至少放一個 Admonition，說明該物理概念在社群歷史上解決過的關鍵問題或典型應用。

---

## 每頁寫作骨架

1. **本章回答的問題**：用 1–2 句定義核心問題。
2. **先備知識對照**：對應四大力學中的先備觀念。
3. **物理核心**：最小必要方程式與假設；所有符號需定義，單位需一致。
4. **工程映射**：將物理量映射到電路與系統設計量。
5. **限制與近似**：明確寫出模型適用範圍與失效條件。
6. **跨文件導航**：依內容相關性提供 1–3 個延伸連結。

---

## 學術引用與可靠性

所有涉及核心物理推導、近似模型或工程擬合公式的段落，都**必須附上參考文獻**。

- 格式：文件底部需建立 `## References` 區塊，建議使用 **APA 格式**。
- 連結寫法：若有 DOI 或 arXiv 連結，應以 Markdown 形式附上。

---

## 可中途切入規範

每篇 Physics Explanation 應提供：

- **你可以從這裡開始**：適合直接閱讀的前置條件清單
- **若要補背景，請先讀**：1–3 個回補連結
- **如果你只想做任務**：導向對應 Tutorial/How-to

---

## Agent Rule { #agent-rule }

```markdown
## Explanation Physics
- **Architecture**: `docs/explanation/physics/` follows the A-J knowledge roadmap (A=Foundations, B=EM-to-Circuits, C=Superconductivity, D=Josephson, E=Quantum-Circuits, F=Building-Blocks, G/H/I=principles-only)
- **Hierarchy**: L1 = domain directories (A-I groups), L2 = topic pages, L3 = optional sub-pages when L2 > 3000 words
- **L1 creation rule**: only create an L1 directory + nav entry when it has at least one L2 page
- **Content boundary**: Physics explains WHY/HOW-IT-WORKS only. Tool usage, CLI steps, workflows → How-to/Tutorials/Reference
- **Node types**: each page declares node_type in tags (principle/model/method/device). Dependencies flow: Principle → Model → Device/Method
- **Positioning**: must be both a full learning backbone and reusable concept nodes
- **Question-driven**: each page starts from a physics question, not an engineering operation question
- **Per-page contract**: question, prerequisites mapping, physics core, engineering mapping, limits/approximations, cross-links
- **Citations**: physics models and derivations MUST include APA references at bottom
- **Overview**: `index.md` contains the full A-I roadmap; linked when content exists, plain text when planned
```
