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

- [ ] 1.1 定義並引入明確 value objects（先從最常見的三個開始）
  - `TraceKind`, `ModeGroup`, `ParameterKey`（避免散落字串慣例）
  - 目標：`src/core/analysis/domain/`, `src/core/simulation/domain/`
- [ ] 1.2 集中 topology/netlist 規則驗證邏輯
  - ground token、`P*`、`K*`、component reference 進單一 validator module
- [ ] 1.3 建立標準化錯誤模型
  - 錯誤碼（machine-readable）+ 訊息模板（UI/i18n 友善）

**Acceptance**
- Domain 規則不再分散於 page/service 中。
- 關鍵錯誤可用穩定 error code 判斷，不依賴完整字串比對。

---

### RS-2 Application Use Cases 收斂（流程離開 page）

- [ ] 2.1 建立 simulation/characterization use-case 層（DTO in/out）
  - Page 只保留 I/O、state mapping、render call
- [ ] 2.2 移除 page 直接組 repository 查詢參數的路徑
  - 改由 use-case / query object 層輸入輸出
- [ ] 2.3 建立 pipeline step registry（post-processing / analysis 共用策略）
  - 讓新研究步驟可插拔，不走 page if/else 擴張

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
- [ ] 3.3 單一 state source
  - 將分散 local dict state 收斂為 typed state object
  - 進度：Characterization/Simulation 已導入 page runtime state dataclass（log history、trace-scope state、latest result/cache handles），後續收斂 termination/setup 子狀態。
- [ ] 3.4 補關鍵互動 `data-testid`
  - 降低 e2e 對文案耦合

**Acceptance**
- 路由不變（`/simulation`, `/characterization`）。
- 關鍵 UI 回歸全綠；e2e 主要斷言改為語義 selector。

---

### RS-4 App Services 分層（registry / evaluator / profile）

- [x] 4.1 `analysis_registry` 拆層
  - Static metadata（宣告）
  - Dynamic evaluator（依 trace scope 運行）
- [ ] 4.2 `dataset_profile` 標註與實作一致
  - 明確 hint-only，不得 hard-gate
- [ ] 4.3 建立 typed service interfaces
  - page 僅依賴介面，不依賴 service 內部欄位命名

**Acceptance**
- Run Analysis 只顯示單一、無重複的 availability 結果來源。
- profile 只作建議，不影響 trace-first hard decision。

---

### RS-5 Repository 合約與查詢穩定化（不改 DB 架構）

- [x] 5.1 補齊 repository protocol contract tests
  - 防止 `attribute missing` 類 runtime 崩潰再發生
- [x] 5.2 導入 query object（頁面禁直接拼 kwargs）
  - 例如 trace index page query、bundle-scope query
- [ ] 5.3 明確 cache/provenance 查詢 API 語意
  - `result_bundle` 查詢依目的分流
- [ ] 5.4 補高頻查詢索引策略文件（不必改 schema 方向）

**Acceptance**
- Page 層不再直接呼叫 ad-hoc repository 方法名。
- 關鍵 repository 方法變更會被 contract test 即時攔截。

---

### RS-6 測試體系升級（contract + perf + e2e）

- [ ] 6.1 Cross-layer contract tests
  - `simulation -> post_processing`
  - `characterization -> repositories`
- [ ] 6.2 大資料基準測試（JTWPA 級）
  - 分頁、篩選、trace 選取延遲、全選保護
- [ ] 6.3 E2E 語義化
  - 優先 testid/結構，不依賴易變文案

**Acceptance**
- 大資料路徑有固定回歸守門。
- 關鍵功能 e2e 可抗文案調整。

---

### RS-7 Runtime Contract Docs（最小必要更新）

- [ ] 7.1 為主要流程新增 runtime contract 區塊
  - input / output / invariants / failure modes
- [ ] 7.2 加入 code reference map（檔案與函式對照）
- [ ] 7.3 加入 runtime parity checklist
  - Data Format vs runtime validator（含 `K*`、ground 等）

**Acceptance**
- 每個核心流程可從文件直接定位到實作位置。
- parity checklist 可作 release 前檢查清單。

---

### RS-8 Multi-Agent 流程制度化（Guardrails 對齊）

- [ ] 8.1 所有 contributor 任務強制 `worktree + allowed files`
- [ ] 8.2 Contributor report 固定欄位（API touched matrix）
- [ ] 8.3 Integrator 合併前固定 smoke suite
  - lint + pytest + targeted playwright

**Acceptance**
- 不再出現 contributor 在髒樹停工的高頻阻塞。
- 合併可追蹤「誰改了哪個 public API」。

---

### RS-9 觀測與除錯能力

- [ ] 9.1 UI log 與 backend log 對齊 run identifiers
  - `run_id`, `bundle_id`, `dataset_id`
- [ ] 9.2 長任務 heartbeat + timeout state 一致化
- [ ] 9.3 cache hit/miss 原因結構化輸出

**Acceptance**
- 使用者可從 UI logs 快速定位 backend 執行狀態與卡點。

---

### RS-10 研究擴充性（長期主軸）

- [ ] 10.1 新分析統一走 `Artifact View Model + Registry`
- [ ] 10.2 Post-processing step plugin 化（CT/Kron/後續方法）
- [ ] 10.3 堅持 trace-first availability（禁止 dataset-level hard gate）

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
