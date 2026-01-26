---
aliases:
  - "Documentation Rules"
  - "文件撰寫規範"
tags:
  - audience/team
  - sot/true
status: stable
owner: docs-team
audience: team
scope: "文件撰寫與維護規範 (Diataxis, Style, Formatting)"
version: v2.0.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Documentation Standards

本文件為專案文件撰寫的單一真理來源 (Source of Truth)。我們採用 **Diataxis** 框架，並嚴格規範格式與風格。

## 1. 架構哲學 (Architecture)

我們採用 [Diataxis](https://diataxis.fr/) 框架，將所有文件分為四大類。寫作前請先確認您的內容屬於哪一類。

| 類別 | 目錄位置 | 目標 (Goal) | 導向 (Orientation) | 內容特徵 |
|---|---|---|---|---|
| **Tutorials** | `docs/tutorials/` | **學習 (Learning)** | 導師引導 (Detailed) | Step-by-step 教學，確保讀者能完成特定任務並獲得成就感。 |
| **How-to** | `docs/how-to/` | **解決問題 (Problem)** | 任務導向 (Practical) | 針對特定問題的解決方案 (Recipes)。不解釋原理，只給步驟。 |
| **Reference** | `docs/reference/` | **資訊 (Information)** | 資訊導向 (Technical) | API 規格、指令參數、數據格式。嚴謹、準確、無廢話。 |
| **Explanation** | `docs/explanation/` | **理解 (Understanding)** | 概念導向 (Theoretical)| 背景知識、設計決策、物理原理。解釋 "Why"。 |

## 2. 寫作風格 (Style Guide)

- **語言 (雙語政策)**:
    - **確保文件都有雙語產生** (透過 i18n 插件)。
    - 核心內容寫作時優先使用 **繁體中文 (zh-TW)**，並同步維護 `.en.md`。
    - 專有名詞保留英文或使用括號標註，例如：`SQUID`、`導納 (Admittance)`。
    - 避免使用中國用語 (例如：避免「視圖」、「項目」，使用「View」、「專案」)。
- **語氣**:
    - **Tutorials**: 鼓勵、引導 (如：「現在我們來試試...」)。
    - **Reference**: 客觀、中立 (如：「此參數控制...」)。
    - **How-to**: 直接、命令式 (如：「執行以下指令...」)。

## 3. 維護規範 (Maintenance)

- **Guardrails as Single Source of Truth**: `docs/reference/guardrails/` 目錄下的文件是人類開發者與 AI Agent 共同遵循的**唯一真理來源**。不需要額外維護 `.agent/rules/` 目錄。
- **雙語同步 (Bilingual Sync)**: 修改任何 `.md` 文件時，**必須同步更新對應的 `.en.md` 檔案**，確保中英文版本內容一致。
- **Commit**: 文件更新應使用 `docs:` type。

## 4. 格式規範 (Formatting)

### Frontmatter Schema

所有 `.md` 檔案必須包含符合以下規範的 YAML frontmatter。

#### 必填欄位 (Required)

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `aliases` | `list[str]` | 文件的替代名稱，用於搜尋與連結跳轉。至少需一個描述性名稱。 | `["LC 諧振器教學", "LC Resonator Tutorial"]` |
| `tags` | `list[str]` | 分類標籤，用於管理與篩選。必須遵循下方 **Tags Taxonomy**。 | `["diataxis/tutorial", "status/stable"]` |

#### 可選欄位 (Optional / Automation)

| 欄位 | 類型 | 說明 | 範例 |
|------|------|------|------|
| `owner` | `str` | 文件負責人或團隊。預設由 Git History 判斷。 | `"docs-team"` |
| `last_updated_by` | `str` | 最後修改者 (建議由 CI 自動更新)。 | `"arfiligol"` |
| `last_updated` | `str` | 最後更新日期 `YYYY-MM-DD` (建議由 CI 自動更新)。 | `"2026-01-27"` |

!!! warning "人名驗證規則"
    `owner` 和 `last_updated_by` 中提及的**所有人名必須存在於 [貢獻者名錄](../contributors.md)**。新增貢獻者時，請先更新名錄再引用。

#### Tags Taxonomy (標籤分類體系)

所有 Tags 採用 `namespace/value` 格式，確保一致性與可管理性。

| Namespace | 說明 | 有效值 |
|-----------|------|--------|
| `diataxis` | 文件類型 (按 Diataxis 框架) | `tutorial`, `how-to`, `reference`, `explanation` |
| `status` | 文件成熟度狀態 | `draft` (草稿), `incubating` (開發中), `stable` (穩定), `deprecated` (棄用) |
| `audience` | 目標讀者 | `user` (使用者), `contributor` (貢獻者), `maintainer` (維護者) |
| `sot` | Source of Truth 標記 | `true` (此文件為該主題的權威來源) |
| `topic` | 主題領域 (自由定義，但建議統一) | `simulation`, `analysis`, `physics`, `cli`, `data-format`, ... |

**範例 Frontmatter**:

```yaml
---
aliases:
  - "LC 共振器模擬教學"
  - "LC Resonator Simulation Tutorial"
tags:
  - diataxis/tutorial
  - status/stable
  - audience/user
  - topic/simulation
---
```

!!! tip "Tag 使用原則"
    - 每個文件至少需要 `diataxis/*` 和 `status/*` 兩個 Tag。
    - `topic/*` 可依內容自由添加，但盡量使用已存在的 topic 值以保持一致。


### Links

- **內部連結**: 使用標準 Markdown 語法 `[顯示文字](path/to/file.md)`。
- **外部連結**: 使用標準 Markdown `[顯示文字](url)`。
- **引用圖片**: 使用 `![Alt](../assets/image.png)` (圖片存放在 `docs/assets/`)。

### 排版元素

- **Admonitions (提示區塊)**: 使用 MkDocs Material 語法。

    !!! warning "語法注意"
        **不要使用** GitHub 風格 `> [!NOTE]`，MkDocs 無法正確渲染。

    **正確語法**:

    ```markdown
    !!! note "標題（可選）"
        內容必須縮排 4 個空格。
        可以有多行。
    ```

    **可摺疊版本** (使用 `???`):

    ```markdown
    ??? tip "點擊展開"
        隱藏的內容。
    ```

    **支援的類型**:

    | 類型 | 用途 |
    |------|------|
    | `note` | 一般註記、補充說明 |
    | `tip` | 技巧、捷徑、最佳實踐 |
    | `warning` | 潛在風險、注意事項 |
    | `danger` | 危險操作、可能造成資料遺失 |
    | `info` | 背景資訊 |
    | `example` | 範例說明 |

- **數學公式**: 使用 MathJax 區塊。
    - 行內: `$E = mc^2$`
    - 區塊: `$$ \Phi_0 = \frac{h}{2e} $$`
- **程式碼**: 必須指定語言。
    ```python
    def hello():
        print("Hello")
    ```

## 4. 視覺與圖表 (Visuals)

- **電路圖**: 必須使用 **Schemdraw** (Python) 生成 SVG。
    - 詳見: [Circuit Diagram Guide](../../how-to/contributing/circuit-diagrams.md)
- **流程圖**: 使用 Mermaid。
    ```mermaid
    graph TD;
        A-->B;
    ```

---

## Agent Rule { #agent-rule }

```markdown
## Docs Rules
- **Architecture (Diataxis)**:
    - `tutorials/`: Learning-oriented (Step-by-step).
    - `how-to/`: Problem-oriented (Recipes).
    - `reference/`: Information-oriented (Specs).
    - `explanation/`: Understanding-oriented (Concepts).
- **Style**:
    - Language: Traditional Chinese (zh-TW).
    - **Bilingual**: Ensure all docs have both zh and en versions.
    - Keep technical terms in English (e.g., SQUID, Admittance).
- **Maintenance**:
    - **Single Source of Truth**: `docs/reference/guardrails/` is the only source for both human devs and AI agents. No separate `.agent/rules/` sync needed.
    - **Bilingual Sync**: When modifying `.md`, MUST update corresponding `.en.md` (and vice versa).
- **Formatting**:
    - Frontmatter: Required (aliases, tags, owner).
    - Links: Use Standard Markdown `[Label](path)`.
    - Math: Use `$$ ... $$` for blocks.
    - Code: Always specify language (e.g., `python`, `julia`).
    - **Admonitions**: Use MkDocs Material syntax only.
        - Correct: `!!! note "Title"` with 4-space indented content.
        - WRONG: `> [!NOTE]` (GitHub style, not supported).
        - Types: `note`, `tip`, `warning`, `danger`, `info`, `example`.
- **Visuals**:
    - Circuits: Use Schemdraw (Python) SVG only.
    - Flows: Use Mermaid.
```
