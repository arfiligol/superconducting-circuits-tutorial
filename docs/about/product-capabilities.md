---
aliases:
  - Product Capabilities
  - 產品能力
  - Product Capability Matrix
  - 產品能力矩陣
tags:
  - diataxis/reference
  - audience/user
  - topic/project-overview
status: draft
owner: team
audience: user
scope: 以能力矩陣方式盤點本平台的目標能力與目前狀態。
version: v0.4.0
last_updated: 2026-03-13
updated_by: team
title: 產品能力
template: marketing.html
---

<section class="sc-marketing-page sc-marketing-page--capabilities">
  <div class="sc-marketing-hero sc-marketing-hero--capabilities">
    <p class="sc-marketing-eyebrow">Product Capability Matrix</p>
    <h1>用一張矩陣看平台能力與目前狀態。</h1>
    <p class="sc-marketing-lead">
      這一頁不重講平台定位。它只回答兩件事：這個平台要承接哪些能力，以及截至 2026-03-13，
      每一類能力目前走到哪裡。矩陣描述的是產品層級能力，不是單一 issue、單一 route 或單一 CLI 指令清單。
    </p>
    <div class="sc-marketing-pills">
      <span>Available</span>
      <span>Partial</span>
      <span>Scaffolded</span>
      <span>Candidate</span>
    </div>
  </div>

  <div class="sc-marketing-band">
    <p>
      這份矩陣用來維護平台版圖：能力需要夠清楚，讓使用者知道平台負責什麼；
      也要夠抽象，不直接滑進實作細節、暫時性 ticket 或內部模組命名。
    </p>
  </div>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Status Legend</p>
      <h2>狀態欄反映的是能力成熟度，不是短期排程。</h2>
    </div>
    <div class="sc-value-grid">
      <article class="sc-value-card">
        <h3><span class="sc-status-pill sc-status-pill--available">Available</span></h3>
        <p>已有可用入口與穩定主路徑，使用者可以把它當成平台現有能力的一部分。</p>
      </article>
      <article class="sc-value-card">
        <h3><span class="sc-status-pill sc-status-pill--partial">Partial</span></h3>
        <p>能力主幹已存在，但入口、深度、整合範圍或 recovery/parity 還不完整。</p>
      </article>
      <article class="sc-value-card">
        <h3><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></h3>
        <p>已有結構、契約或分析路線，但還不足以當成完整產品能力對外承諾。</p>
      </article>
      <article class="sc-value-card">
        <h3><span class="sc-status-pill sc-status-pill--candidate">Candidate</span></h3>
        <p>已被納入產品版圖，但目前仍停留在能力定義與邊界整理階段。</p>
      </article>
    </div>
  </section>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Research Definition</p>
      <h2>平台先固定研究對象，再讓後續模擬與分析共享同一個起點。</h2>
    </div>
    <div class="sc-capability-table-wrap">
      <table class="sc-capability-table">
        <thead>
          <tr>
            <th>能力</th>
            <th>主要入口</th>
            <th>涵蓋內容</th>
            <th>狀態</th>
            <th>說明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Canonical Circuit Definition</td>
            <td>UI / CLI / Core</td>
            <td>以單一 definition 承接電路結構、參數、模擬輸入與後續分析語意。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>canonical contract 已是平台主幹，但高層 authoring 與更完整 reusable patterns 仍未完全展開。</td>
          </tr>
          <tr>
            <td>Definition Validation &amp; Normalization</td>
            <td>Core / CLI / Backend</td>
            <td>讓不同入口對同一份電路定義維持一致驗證與結構化輸出。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>共享 contract 與驗證方向已清楚，跨所有入口的完整產品包覆仍在收斂中。</td>
          </tr>
          <tr>
            <td>Schematic / Structural Preview</td>
            <td>UI / Docs</td>
            <td>從 definition 生成可閱讀的結構視圖，協助確認電路語意而不是只看原始文字。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>結構 preview 與 schema editor 路線存在，但還不是完整的 design workspace。</td>
          </tr>
          <tr>
            <td>Reusable Parameterized Definitions</td>
            <td>Core / UI</td>
            <td>讓研究者能以可重複使用的方式表達重複段落、參數族與變體。</td>
            <td><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></td>
            <td>平台已明確朝 reusable definition 前進，但能力呈現仍偏基礎與局部。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Analysis Routes</p>
      <h2>平台同時維持 network-level 與 quantum-level 兩條分析主軸。</h2>
    </div>
    <div class="sc-capability-table-wrap">
      <table class="sc-capability-table">
        <thead>
          <tr>
            <th>能力</th>
            <th>主要入口</th>
            <th>涵蓋內容</th>
            <th>狀態</th>
            <th>說明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>S / Y / Z Matrix Analysis</td>
            <td>Docs / Analysis / Characterization</td>
            <td>用同一套 network representation 讀 layout simulation、circuit simulation 與 measurement。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>這是平台的重要中樞，但不是唯一主命題；它主要負責 comparison frame 與 source normalization。</td>
          </tr>
          <tr>
            <td>Cross-Source Comparison Frame</td>
            <td>UI / Analysis / Dataset</td>
            <td>把不同來源的 traces 與結果放進同一個分析座標，比較差異而不是只看單點輸出。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>comparison 與 characterization 路線已被納入平台，但結果呈現與整體產品深度仍在擴充。</td>
          </tr>
          <tr>
            <td>Circuit Definition to Hamiltonian</td>
            <td>Explanation / Core</td>
            <td>從 circuit definition、等效模型到量子化後的 Hamiltonian 描述，處理超導量子電路的核心差異。</td>
            <td><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></td>
            <td>概念路線與平台範圍已確立，但產品級 workflow 仍未完整成形。</td>
          </tr>
          <tr>
            <td>Layout-to-Quantum Bridge</td>
            <td>Layout Simulation / Core</td>
            <td>透過 pyEPR 類技術或同類方法，從 layout-derived information 延伸到量子化分析。</td>
            <td><span class="sc-status-pill sc-status-pill--candidate">Candidate</span></td>
            <td>這是平台與傳統 photonics workflow 拉開差異的重要能力，但目前仍屬能力邊界定義。</td>
          </tr>
          <tr>
            <td>Quantum-Specific Interpretation</td>
            <td>Explanation / Analysis</td>
            <td>讓使用者知道何時停在 S/Y/Z，何時必須往量子化模型前進。</td>
            <td><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></td>
            <td>這條理解路線已被列進平台核心，但仍偏 explanation-first，而非成熟 workflow-first。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Simulation &amp; Measurement</p>
      <h2>模擬、匯入與量測分析需要被當成同一個產品系統，而不是三套工具。</h2>
    </div>
    <div class="sc-capability-table-wrap">
      <table class="sc-capability-table">
        <thead>
          <tr>
            <th>能力</th>
            <th>主要入口</th>
            <th>涵蓋內容</th>
            <th>狀態</th>
            <th>說明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Circuit Simulation Workflow</td>
            <td>UI / CLI / Core</td>
            <td>從 definition 進到 simulation 執行、結果回看與後續處理。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>主工作流已存在，也是目前最可見的產品面之一，但整體 parity 與 recovery 還在補齊。</td>
          </tr>
          <tr>
            <td>Layout Simulation Trace Ingest</td>
            <td>CLI / Dataset / Analysis</td>
            <td>把 HFSS、Q3D 等 layout-derived traces 轉成平台可比較的研究資料。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>相容 traces 與 ingest 路線已被納入平台敘事，但入口整合仍不算完整。</td>
          </tr>
          <tr>
            <td>Measurement Dataset Ingest</td>
            <td>CLI / Dataset / Session</td>
            <td>把實驗量測資料納入 dataset 與 analysis 路線，而不是留在站外腳本。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>dataset 與 characterization 已在 rewrite 路線中，但 measurement-first UX 仍未完全成熟。</td>
          </tr>
          <tr>
            <td>Characterization &amp; Post-Processing</td>
            <td>UI / CLI / Analysis</td>
            <td>對 simulation、layout、measurement traces 套用一致後處理、比較與參數萃取語意。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>characterization 已是正式 lane，但結果表面與更完整研究操作仍在加厚。</td>
          </tr>
          <tr>
            <td>Derived Parameters &amp; Comparison Artifacts</td>
            <td>Analysis / Result</td>
            <td>保存 resonance fit、參數萃取、comparison 結果與可追溯 artifacts。</td>
            <td><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></td>
            <td>結果 contract 與 provenance 路線存在，但平台級 asset presentation 仍不完整。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Execution &amp; Recovery</p>
      <h2>平台能力不只在分析內容，也在流程是否可提交、可追蹤、可重建。</h2>
    </div>
    <div class="sc-capability-table-wrap">
      <table class="sc-capability-table">
        <thead>
          <tr>
            <th>能力</th>
            <th>主要入口</th>
            <th>涵蓋內容</th>
            <th>狀態</th>
            <th>說明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Persisted Task Lifecycle</td>
            <td>Backend / CLI / UI</td>
            <td>讓 simulation 與 characterization 任務以 persisted task state 被提交、執行、回看與驗證。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>task lifecycle 已是 rewrite 主幹，execution runtime 也已有 milestone，但整體操作面仍在打磨。</td>
          </tr>
          <tr>
            <td>Task Attach / Recovery</td>
            <td>UI / CLI / Backend</td>
            <td>在 refresh、reconnect 或重新開啟後，把任務、結果與上下文重新接回。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>recovery 是明確要求，persisted runtime 已開始支撐，但所有 surface 的體驗尚未齊平。</td>
          </tr>
          <tr>
            <td>Simulation &amp; Characterization Lanes</td>
            <td>Core / Worker / Backend</td>
            <td>讓不同類型任務以清楚 lane 語意執行，而不是散落在非正式腳本中。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>lane semantics 與 orchestration operation 已建立，但完整 product story 仍在延伸。</td>
          </tr>
          <tr>
            <td>Trace / Result / Provenance Persistence</td>
            <td>Backend / Core</td>
            <td>保存 trace、result handles、metadata 與 provenance，讓結果不只停在當下畫面。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>canonical contract 與 persisted storage 已成形，平台級呈現與使用密度仍在提升。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Product Surfaces</p>
      <h2>同一個平台需要能被不同入口使用，但不能在不同入口長成不同產品。</h2>
    </div>
    <div class="sc-capability-table-wrap">
      <table class="sc-capability-table">
        <thead>
          <tr>
            <th>能力</th>
            <th>主要入口</th>
            <th>涵蓋內容</th>
            <th>狀態</th>
            <th>說明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Simulation Workbench UI</td>
            <td>Frontend</td>
            <td>提供定義、任務、結果與 workflow framing 的互動式工作台。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>simulation UI 是目前最成熟的前台之一，但仍在朝更完整 research workflow 收斂。</td>
          </tr>
          <tr>
            <td>Characterization Workspace UI</td>
            <td>Frontend</td>
            <td>承接 dataset、task queue、結果回看與 comparison-oriented workflow。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>shared workflow layer 已建立，但 characterization product depth 仍在追上中。</td>
          </tr>
          <tr>
            <td>CLI-Available Workflows</td>
            <td>CLI</td>
            <td>關鍵工作流可從 CLI 執行，不把平台能力鎖在單一 UI surface。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>CLI 是一級介面，既有契約與測試持續收斂；完整 parity 仍是明確能力要求。</td>
          </tr>
          <tr>
            <td>Technical Documentation Surface</td>
            <td>Docs</td>
            <td>以 Tutorials / How-to / Explanation / Reference 承接工作流、概念與契約。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>文件已是正式產品表面，但 capability matrix 與 marketing/technical 分界仍在整理中。</td>
          </tr>
          <tr>
            <td>Desktop Runtime Shell</td>
            <td>Desktop</td>
            <td>提供本地包裝與桌面使用情境，不改變 canonical frontend/backend/CLI 邊界。</td>
            <td><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></td>
            <td>desktop 被納入技術棧與平台範圍，但還不是目前最成熟的主入口。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sc-marketing-section">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Boundary &amp; Hand-off</p>
      <h2>平台邊界要清楚，資料與分析資產才能和其他系統銜接。</h2>
    </div>
    <div class="sc-capability-table-wrap">
      <table class="sc-capability-table">
        <thead>
          <tr>
            <th>能力</th>
            <th>主要入口</th>
            <th>涵蓋內容</th>
            <th>狀態</th>
            <th>說明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Design-to-Measurement Boundary</td>
            <td>Docs / Product Scope</td>
            <td>明確把本平台定義為 fabrication 之外的 design / simulation / measurement / comparison / feedback 系統。</td>
            <td><span class="sc-status-pill sc-status-pill--partial">Partial</span></td>
            <td>平台邊界已被講清楚，但仍需要持續反映在文件、能力盤點與產品表述上。</td>
          </tr>
          <tr>
            <td>Lab-Chip-Data-Hub Hand-off</td>
            <td>Product Boundary / Data Assets</td>
            <td>讓本平台產出的資料、結果與分析資產可以被 fabrication integration 系統承接。</td>
            <td><span class="sc-status-pill sc-status-pill--candidate">Candidate</span></td>
            <td>分工方向已明確，但具體 hand-off product surface 仍未正式成型。</td>
          </tr>
          <tr>
            <td>Open-Source Product Surface</td>
            <td>Docs / UI / CLI</td>
            <td>把本平台定義成可公開的研究分析平台，而不是內部單點工具。</td>
            <td><span class="sc-status-pill sc-status-pill--scaffolded">Scaffolded</span></td>
            <td>公開定位已明確，但哪些能力以何種成熟度對外呈現，仍需持續收斂。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sc-marketing-section sc-marketing-section--cta">
    <div class="sc-marketing-section__header">
      <p class="sc-marketing-kicker">Related</p>
      <h2>介紹負責講定位；技術文件負責講原理與契約；這一頁只維護能力版圖。</h2>
    </div>
    <div class="sc-path-grid">
      <a class="sc-path-card" href="../">
        <h3>回到介紹</h3>
        <p>先看平台定位、產品邊界與整體主敘事。</p>
      </a>
      <a class="sc-path-card" href="../../explanation/">
        <h3>查看 Explanation</h3>
        <p>沿著 S/Y/Z、circuit definition 與 Hamiltonian 理解分析主幹。</p>
      </a>
      <a class="sc-path-card" href="../../reference/">
        <h3>查看 Reference</h3>
        <p>直接查 UI、CLI、資料格式與 guardrails 契約。</p>
      </a>
      <a class="sc-path-card" href="../../tutorials/">
        <h3>查看 Tutorials</h3>
        <p>從實際工作流理解平台現有的主要操作面。</p>
      </a>
    </div>
  </section>
</section>
