# Refactor Master TODO (Maintainability + Extensibility)

Status: `in_progress`
Owner: `Integrator (Codex)`
Priority: `P0`
Last Updated: `2026-03-05`
Scope: 在 **不改 Repositories/ORM/DB 架構方向** 前提下，完成可維護性與可擴充性重構。

---

## 0) Hard Constraints (不可違反)

1. 不變更核心 persistence 方向：`SQLModel + UnitOfWork + Repository`。
2. 不做 destructive migration、不清空 DB、不改資料生命週期。
3. `Trace-first availability` 是唯一分析可用性權威；`dataset profile` 保持 hint-only。
4. 不破壞既有路由與核心互動（除非在本 TODO 明確列為設計變更）。
5. 每個結構改動批次必須同步補測試（unit/integration/e2e 至少一種）。
6. 多 Agent 協作時，只有 Integrator 可整合；Contributor 必須交接原子 commits。

---

## 1) Baseline Snapshot（啟動時現況）

1. `src/app/pages/simulation.py`、`src/app/pages/characterization.py` 為高複雜度單檔。
2. UI 層仍有部分流程編排與 query 參數組裝，導致 page 與 repository 耦合偏高。
3. `analysis_registry` 同時承擔 metadata 宣告與 runtime 判斷，邊界不清。
4. 大資料頁面存在效能風險（選取、篩選、分頁、全選）。
5. 部分 e2e 仍耦合文案，回歸測試穩定性不足。

---

## 2) Refactor Streams（對應 10 大優化面向）

### RS-1 Domain 強化（value objects / validator / error model）

- [x] 1.1 定義並引入明確 value objects（先從最常見的三個開始）
  - `TraceKind`, `ModeGroup`, `ParameterKey`（避免散落字串慣例）
  - 目標：`src/core/analysis/domain/`, `src/core/simulation/domain/`
- 已完成：新增 `core.analysis.domain.value_objects`，並在 Characterization trace scope / page mode filtering 路徑改用 typed normalization（含 domain tests）。
- [x] 1.2 集中 topology/netlist 規則驗證邏輯
  - ground token、`P*`、`K*`、component reference 進單一 validator module
- 已完成：新增 `core.simulation.domain.validators`，集中 `ground token`、`P*`、`K*` 與 component reference 檢查。
- [x] 1.3 建立標準化錯誤模型
  - 錯誤碼（machine-readable）+ 訊息模板（UI/i18n 友善）
- 已完成：新增 `CircuitValidationError(code=...)` 與 `CircuitValidationCode`，保留原訊息文案並補測試覆蓋。

**Acceptance**
- Domain 規則不再分散於 page/service 中。
- 關鍵錯誤可用穩定 error code 判斷，不依賴完整字串比對。

---

### RS-2 Application Use Cases 收斂（流程離開 page）

- [ ] 2.1 建立 simulation/characterization use-case 層（DTO in/out）
  - Page 只保留 I/O、state mapping、render call
- 進度：`app/services/characterization_runner.py` 已承接 analysis run dispatch（admittance / S21 fit / SQUID fit / Y11 fit），`characterization` page 移除本地流程分支。
- [ ] 2.2 移除 page 直接組 repository 查詢參數的路徑
  - 改由 use-case / query object 層輸入輸出
  - 進度：Characterization 的 trace scope page query 已抽到 `app/services/characterization_trace_scope.py`。
- [ ] 2.3 建立 pipeline step registry（post-processing / analysis 共用策略）
  - 讓新研究步驟可插拔，不走 page if/else 擴張
- 進度：新增 `app/services/post_processing_step_registry.py`，集中 `step options/default/serialize/normalize/preview/execute`，`simulation` page 改為 registry-dispatch 執行 CT/Kron。

**Acceptance**
- 至少 80% page business workflow 已轉移到 application/use-case 層。
- 新增一步分析/後處理不需要改多個 page 分支。

---

### RS-3 UI Page 模組化（不改路由，改內部結構）

- [x] 3.1 `simulation.py` folderize
  - 目標結構：
    - `src/app/pages/simulation/__init__.py`（保留 route）
    - `state.py`, `actions.py`, `mappers.py`, `sections/*.py`
- [x] 3.2 `characterization.py` folderize
  - 目標結構：
    - `src/app/pages/characterization/__init__.py`
    - `state.py`, `actions.py`, `compatibility.py`, `sections/*.py`
- [x] 3.3 單一 state source
  - 將分散 local dict state 收斂為 typed state object
  - 已完成：Characterization/Simulation 已導入 page runtime state dataclass（log history、trace-scope state、latest result/cache handles），並收斂 termination/setup 子狀態。
- [x] 3.4 補關鍵互動 `data-testid`
  - 降低 e2e 對文案耦合
  - 已完成：`simulation` 與 `characterization` 關鍵卡片/控制項補 testid（result cards、run button、trace/category filters、post-processing input/step controls），Playwright 改為 testid-first + fallback selector。

**Acceptance**
- 路由不變（`/simulation`, `/characterization`）。
- 關鍵 UI 回歸全綠；e2e 主要斷言改為語義 selector。

---

### RS-4 App Services 分層（registry / evaluator / profile）

- [x] 4.1 `analysis_registry` 拆層
  - Static metadata（宣告）
  - Dynamic evaluator（依 trace scope 運行）
- [x] 4.2 `dataset_profile` 標註與實作一致
  - 明確 hint-only，不得 hard-gate
- 已完成：`analysis_capability_evaluator` 改為 hint-only 契約（永不回傳 unavailable/blocked），Run Analysis 仍以 trace compatibility 為唯一可執行權威。
- [x] 4.3 建立 typed service interfaces
  - page 僅依賴介面，不依賴 service 內部欄位命名
  - 進度：`analysis_registry` 已導入 `AnalysisDescriptor`/`AnalysisConfigField` typed interface 與 `list_dataset_analyses()` API；`dataset_profile` 已導入 `DatasetProfile` typed payload；capability evaluator 改用 typed `Mapping + DatasetProfile` 介面。
  - 已完成：`characterization_trace_scope` 導入 `CharacterizationTraceScopeUnitOfWork` Protocol，並用 repository contracts 約束 `data_records`/`result_bundles` 依賴。

**Acceptance**
- Run Analysis 只顯示單一、無重複的 availability 結果來源。
- profile 只作建議，不影響 trace-first hard decision。

---

### RS-5 Repository 合約與查詢穩定化（不改 DB 架構）

- [x] 5.1 補齊 repository protocol contract tests
  - 防止 `attribute missing` 類 runtime 崩潰再發生
- [x] 5.2 導入 query object（頁面禁直接拼 kwargs）
  - 例如 trace index page query、bundle-scope query
- [x] 5.3 明確 cache/provenance 查詢 API 語意
  - `result_bundle` 查詢依目的分流
- 已完成：`ResultBundleRepository` 新增 `list_cache_by_dataset` / `list_provenance_by_dataset` / `count_by_dataset`，Characterization Source Scope bundle 統計改用 provenance（排除 cache）。
- [x] 5.4 補高頻查詢索引策略文件（不必改 schema 方向）
- 已完成：新增 `reference/data-formats/query-indexing-strategy(.en).md`，定義 DataRecord/ResultBundle 高頻查詢路徑、現況索引、候選複合索引與監控建議。

**Acceptance**
- Page 層不再直接呼叫 ad-hoc repository 方法名。
- 關鍵 repository 方法變更會被 contract test 即時攔截。

---

### RS-6 測試體系升級（contract + perf + e2e）

- [x] 6.1 Cross-layer contract tests
  - `simulation -> post_processing`
  - `characterization -> repositories`
- 已完成：`test_post_processing.py` 覆蓋 simulation->post_processing 轉換契約；新增 trace-scope protocol contract test 與 `ResultBundleDatasetSummaryContract` 測試，補齊 characterization->repositories API 防退化。
- [x] 6.2 大資料基準測試（JTWPA 級）
  - 分頁、篩選、trace 選取延遲、全選保護
- 已完成：新增 `test_trace_scope_benchmark.py`（10k trace metadata）驗證 trace-scope 查詢走分頁且在基準時間內完成。
- [x] 6.3 E2E 語義化
  - 優先 testid/結構，不依賴易變文案
- 已完成：Characterization Playwright 的 availability/hint 斷言改為 testid-first（`characterization-availability-label` / `...-reason`），降低文案漂移造成的誤報。

**Acceptance**
- 大資料路徑有固定回歸守門。
- 關鍵功能 e2e 可抗文案調整。

---

### RS-7 Runtime Contract Docs（最小必要更新）

- [x] 7.1 為主要流程新增 runtime contract 區塊
  - input / output / invariants / failure modes
- [x] 7.2 加入 code reference map（檔案與函式對照）
- [x] 7.3 加入 runtime parity checklist
  - Data Format vs runtime validator（含 `K*`、ground 等）
- 已完成：`circuit-netlist(.en)`、`characterization(.en)`、`circuit-simulation(.en)` 新增 Runtime Contract Snapshot / Code Reference Map / Runtime Parity Checklist，並對齊 K* 與 ground 規則。

**Acceptance**
- 每個核心流程可從文件直接定位到實作位置。
- parity checklist 可作 release 前檢查清單。

---

### RS-8 Multi-Agent 流程制度化（Guardrails 對齊）

- [x] 8.1 所有 contributor 任務強制 `worktree + allowed files`
- [x] 8.2 Contributor report 固定欄位（API touched matrix）
- [x] 8.3 Integrator 合併前固定 smoke suite
  - lint + pytest + targeted playwright
- 已完成：新增 `scripts/run_integrator_smoke_suite.sh`，統一執行 `ruff check`、`pytest`、characterization/josephson Playwright。

**Acceptance**
- 不再出現 contributor 在髒樹停工的高頻阻塞。
- 合併可追蹤「誰改了哪個 public API」。

---

### RS-9 觀測與除錯能力

- [x] 9.1 UI log 與 backend log 對齊 run identifiers
  - `run_id`, `bundle_id`, `dataset_id`
- 已完成：Simulation/Characterization log prefix 加入 context tokens；characterization provenance bundle 與 simulation cache bundle 皆寫入 `run_id`。
- [x] 9.2 長任務 heartbeat + timeout state 一致化
- 已完成：Simulation 與 Characterization 長任務都採 5s heartbeat，並在 60s 後追加 long-running warning（不中止任務）。
- [x] 9.3 cache hit/miss 原因結構化輸出
- 已完成：Simulation cache logs 區分 hit/miss 與 `schema_source_hash + simulation_setup_hash` 匹配原因。

**Acceptance**
- 使用者可從 UI logs 快速定位 backend 執行狀態與卡點。

---

### RS-10 研究擴充性（長期主軸）

- [x] 10.1 新分析統一走 `Artifact View Model + Registry`
- 已完成：新增 `app/services/result_artifact_registry.py`，Characterization Result View artifact manifest（分類/排序/shape metadata）改由 registry 產生，page 只負責 render + state。
- [x] 10.2 Post-processing step plugin 化（CT/Kron/後續方法）
- 已完成：新增 `app/services/post_processing_step_registry.py`，Post Processing step 行為（label preview + runtime execute）由 registry 管理，page 移除核心 if/else 流程。
- [x] 10.3 堅持 trace-first availability（禁止 dataset-level hard gate）
- 已完成：run availability 由 trace compatibility + selected trace ids 決定；dataset profile capability 僅輸出 `Profile hint`，不再 hard-block 執行。

**Acceptance**
- 新分析上線不需侵入式修改多頁面控制流程。

---

## 3) Execution Order（嚴格順序）

1. RS-5 Repository contracts/query stability（先止血）
2. RS-4 Services split（registry/evaluator/profile）
3. RS-2 Use cases（流程上移）
4. RS-3 Page modularization（大檔拆分）
5. RS-6 Test hardening（contract + perf + e2e）
6. RS-9 Observability（追蹤與除錯）
7. RS-1 Domain consolidation（值物件/validator/error model）
8. RS-10 Extensibility polish（plugin/artifact pattern）
9. RS-7/RS-8 文檔與流程補完（收尾）

Reason: 先解 API/契約風險，再做結構調整，避免大搬移時失控。

---

## 4) Commit Batch Plan（每批可獨立回退）

- Batch A: Repository contracts + query objects + contract tests
- Batch B: analysis registry split + evaluator + UI status unification
- Batch C: simulation use-case extraction + page modular scaffolding
- Batch D: characterization use-case extraction + page modular scaffolding
- Batch E: testid rollout + e2e semantic migration + large data benchmarks
- Batch F: logging/run-id alignment + heartbeat/timeouts
- Batch G: domain value objects + centralized validators + error codes
- Batch H: plugin/registry extensibility polish + runtime contract docs

Each batch gate:
- `uv run ruff check .`
- `uv run basedpyright src`
- `uv run pytest`
- Relevant Playwright subset for touched pages

---

## 5) Definition of Done

1. `/simulation`, `/characterization`, `/raw-data` 行為一致且回歸通過。
2. Page 不再直接依賴 ad-hoc repository 方法名或拼湊長 query kwargs。
3. `simulation`、`characterization` 完成模組化與 typed state/control 流程。
4. `analysis_registry` 與 evaluator 清楚分離；availability 呈現單一來源。
5. 大數據路徑具備穩定性能與回歸測試（JTWPA 級別）。
6. 可觀測性可用（run_id/bundle_id 對齊、heartbeat、cache reason）。
7. 新分析/新後處理可透過 plugin/registry 擴充，不需改 page 主流程。

---

## 6) Risks & Mitigations

- R1: Page folderize 造成 route/import 斷裂
  - Mitigation: route decorator 留在 `__init__.py`；先搬 helper 再搬 render。
- R2: state 合併導致 UI refresh 時序問題
  - Mitigation: 為每個 state transition 補 unit tests。
- R3: 大資料測試成本上升
  - Mitigation: 增設標準小型 smoke + 每日/手動大型基準測試。
- R4: 多 Agent 同檔衝突
  - Mitigation: 強制 Allowed Files + worktree + integrator-only merge。

---

## 7) Context Compacting Preserve Set

如果需要 context compacting，至少保留：
1. 本 TODO 檔（完整版本）
2. 當前 batch 與 blocking issue
3. 任何 API/contract 決策（含 tradeoffs）
4. 最新測試失敗簽名與 root cause
5. 尚未整合的 contributor commit hashes
