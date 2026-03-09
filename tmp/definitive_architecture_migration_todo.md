# Definitive Architecture Migration Master TODO

Status: `active`
Owner: `Migration Agent (Codex)`
Priority: `P0`
Last Updated: `2026-03-09` (strengthened pass: `2026-03-09T13:26`, second pass: `2026-03-09T13:40`, decision freeze: `2026-03-09T13:52`, extended freeze: `2026-03-09T14:08`, api inventory freeze: `2026-03-09T14:24`, worker topology freeze: `2026-03-09T14:31`, ws2 execution ownership: `2026-03-09T15:04`, ws2 persistence batch 1 complete: `2026-03-09T15:28`, ws2 bootstrap-reconcile foundations: `2026-03-09T15:41`, ws2 dual-write lifecycle wired: `2026-03-09T15:55`, ws2 checkpoint commit prep: `2026-03-09T16:20`, ws3 execution ownership: `2026-03-09T18:05`, ws3 worker lanes verified: `2026-03-09T19:02`, ws3 import-boundary fixup: `2026-03-09T19:27`)
Primary SoT:
- `/Users/arfiligol/Downloads/Definitive Architecture`
- `/Users/arfiligol/Github/superconducting-circuits-tutorial/docs/explanation/architecture/trace-platform-implementation-plan.md`
- `/Users/arfiligol/Github/superconducting-circuits-tutorial/docs/explanation/architecture/data-storage.md`
- `/Users/arfiligol/Github/superconducting-circuits-tutorial/docs/reference/guardrails/execution-verification/multi-agent-collaboration.md`
- `~/.gemini/antigravity/brain/b67dc671-a3bc-439c-b2a3-58230376e588/definitive_architecture.md` (原始架構設計)

Scope:
- 將現有系統從「NiceGUI page-local orchestration + in-process background helpers」收斂到 Definitive Architecture：
  - NiceGUI process 同時提供 Web UI + REST API
  - Huey worker 作為獨立 process 執行 Julia-heavy / crash-prone / long-running jobs
  - SQLite + Zarr 保留
  - UI / CLI 共享同一套 persisted execution boundary
  - 支援 multi-user local auth（`admin` / `user`）
  - 頁面 state 不再作為 workflow authority

Document rules for future updates:
- 本檔每次更新都要同步：
  - `Last Updated`
  - 本次變更摘要（若有新 decision / blocker / task split 調整）
  - 對應 task 狀態與 evidence
- 若架構決策已定案，需寫入 `Decision Freeze Log`，不要只散落在 task 描述中

Current execution ownership:
- `2026-03-09T15:04` `Migration Agent`
  - Branch / Worktree: `codex/da-migration-ws2` / `/Users/arfiligol/Github/superconducting-circuits-tutorial-da-ws2`
  - Active batch:
    - `DA-WS2-01`
    - `DA-WS2-02`
    - `DA-WS2-07`
    - `DA-WS2-08`
    - `DA-WS2-03`
  - Scope:
    - `src/core/shared/persistence/**`
    - `tests/core/shared/persistence/**`
    - `src/app/pages/simulation/__init__.py`
    - `tmp/definitive_architecture_migration_todo.md`
- `2026-03-09T18:05` `Migration Agent`
  - Branch / Worktree: `codex/da-migration-ws3` / `/Users/arfiligol/Github/superconducting-circuits-tutorial-da-ws3`
  - Active batch:
    - `DA-WS3-01`
    - `DA-WS3-02`
    - `DA-WS3-03`
    - `DA-WS3-04`
    - `DA-WS3-05`
    - `DA-WS3-06`
    - `DA-WS3-07`
    - `DA-WS3-08`
  - Scope:
    - `pyproject.toml`
    - `src/worker/**`
    - `src/core/shared/persistence/**`
    - `tests/worker/**`
    - `tmp/definitive_architecture_migration_todo.md`

---

## 0) 快速現況摘要（2026-03-09 實測）

以下是目前 repo 已確認的事實，後續 Agent 不要重複重新盤點：

### 0.1 已經對齊 Definitive Architecture 的部分

- [x] `core/shared/persistence/models.py`
  - 已有 canonical `DesignRecord / TraceRecord / TraceBatchRecord / AnalysisRunRecord` logical naming。
- [x] `core/shared/persistence/trace_store.py`
  - 已有 local-first `TraceStore` / `TraceStoreRef` / `local_zarr` contract。
- [x] `core/shared/persistence/unit_of_work.py`
  - 已有 `SqliteUnitOfWork` + Repository pattern，可直接擴展。
- [x] `scripts/cli/entry.py`
  - 已有 Typer CLI root（analysis/sim/plot/preprocess/db/docs），可作為 shared use-case 的 CLI composition root。
- [x] `docs/explanation/architecture/trace-platform-implementation-plan.md`
  - 已明確定義 phase-4 方向：persisted orchestration，不能再靠 live session authority。
- [x] Julia 隔離層已存在
  - App 層**不直接 import JuliaCall/juliacall**。所有 Julia 呼叫走 `core.simulation.application.run_simulation` → `core.simulation.infrastructure.julia_adapter.JuliaSimulator`。
  - 這意味著 Worker 隔離的切割面是乾淨的：只需要讓 `run_simulation()` 在 Worker process 被呼叫即可。
- [x] analysis-run repository boundary 已存在雛形
  - `core/shared/persistence/repositories/analysis_run_repository.py` 與相關 tests 已在使用 `analysis_run_id` summary/bundle mapping。
  - 代表 Characterization 的 persisted run boundary 不是從零開始設計，而是要避免被新 task system 破壞。

### 0.2 明顯尚未對齊的部分

- [ ] `pyproject.toml`
  - 尚未引入 `huey`。
- [ ] `src/app/main.py`
  - 目前只有 NiceGUI app（79 行），沒有 REST API registration、沒有 auth middleware、沒有 worker integration hooks。
  - 已使用 `ui.run()` 啟動，需改為 `ui.run()` + worker entrypoint 雙入口。
- [ ] `src/app/pages/simulation/__init__.py`
  - **10832 行 / 283 個 outline items / 476KB**，仍然是超大型 page module。
  - 仍大量依賴 `SimulationRuntimeState.latest_*` 作為流程 authority（14 個 mutable 欄位）。
  - 使用 `run.io_bound()` 共 **4 處**（行 7504, 9494, 10117, 10806）。**不使用 `run.cpu_bound()`**（之前描述有誤）。
  - Julia 呼叫發生在行 ~9980，透過 `run_simulation()` 間接呼叫。
  - 有 **4 個 module-level（process-global）cache dict**：
    - `_SWEEP_RUN_CACHE` (limit 8)
    - `_SWEEP_POINT_LOOKUP_CACHE` (limit 8)
    - `_SWEEP_SERIES_CACHE` (limit 512)
    - `_TRACE_STORE_AUTHORITY_CACHE` (limit 8)
  - 這些 cache 跨 session 共享（process-global），遷移時需決定保留/廢除/改為 per-design scoped。
- [ ] `src/app/pages/simulation/state.py`
  - 雖已有 typed runtime state（`SimulationRuntimeState`, `TerminationSetupState`），但本質上仍是 page-local live state，不符合 definitive architecture 的 persisted task authority。
- [ ] `src/app/pages/characterization/__init__.py`
  - **145KB**——Characterization 頁面同樣龐大，遷移時不可忽略。
  - 內含 analysis run 的 session-local orchestration 邏輯。
- [ ] `src/core/shared/persistence/models.py`
  - 尚未有真正的 `TaskRecord` table/contract。
- [ ] `src/app/`
  - 沒有 `/api/tasks`、`/api/designs`、`/api/simulation-runs` 類 REST route。
- [ ] `src/`
  - 尚未有 `tasks.py` / `huey_app` / worker entrypoint。

### 0.3 判斷：哪些要保留、哪些要重做

- 保留（~70% 的 core 程式碼）：
  - `core/analysis/domain/` — 純邏輯，不依賴框架
  - `core/simulation/domain/` — 電路定義、SimulationResult（含 `circuit.py` 60KB）
  - `core/simulation/application/run_simulation.py` — Sweep plan 邏輯
  - `core/simulation/application/post_processing.py` — 矩陣運算
  - `core/simulation/infrastructure/julia_adapter.py` — Julia bridge
  - `core/shared/persistence/` — 全部保留
  - `scripts/cli/` — 全部保留
  - `app/pages/raw_data.py` (32KB) — Data Browser，讀取邏輯可沿用
  - `app/pages/dashboard.py` (16KB) — 參數儀表板，讀取邏輯可沿用
  - `app/pages/schemas.py`, `schema_editor.py`, `schemdraw_live_preview.py` — Schema 類頁面可沿用
- 重構：
  - `app/services/` — 改成 orchestration adapter / DTO mapper，不直接承擔 page-local authority
  - `trace_architecture.py` (1392 行) — 可重用的 persisted write/read function，抽成 worker-callable use cases
  - `app/services/post_processing_runner.py` — input 從 `SimulationResult` object → persisted batch_id
  - `app/services/characterization_runner.py` — 對齊 task contract
- 重寫（UI 外觀保留，orchestration 全部重做）：
  - `simulation/__init__.py` — 10832 行，拆解 + 改 API-driven
  - `characterization/__init__.py` — 145KB，同樣需要 persisted analysis-run orchestration

---

## 1) 不可違反的硬約束

1. 不回退 `Design / Trace / TraceBatch / TraceStore` 架構方向。
2. 不做歷史資料 migration；若 physical schema 收斂，走 direct cutover。
3. 不把大型 numeric payload 搬回 metadata DB。
4. UI / CLI 都必須共享同一套 application/use-case contract，不可各自複製流程。
5. Julia 初始化與執行應移到 worker process；Web UI process 不應承擔 crash risk。
6. `Simulation` / `Post Processing` / `Characterization` 的 authority 必須來自 persisted records，而不是 `latest_*` page state。
7. 這一輪不要為了快而破壞現有 `TraceStore` backend boundary。
8. 不碰使用者目前 dirty 的既有檔案，除非該 task 明確就是要接手那些檔案。
9. 重複提交（double-click / refresh / retry）不得產生語意未定義的 duplicate run；必須定義 idempotency 或 dedupe policy。
10. worker / app restart 後，系統必須能用 persisted state 做 reconcile，不可要求人工記憶 page-local context。
11. phase 1 必須支援 multi-user local auth；UI pages 與 `/api/v1/*` 都不可裸露。
12. `TaskRecord` / `AnalysisRunRecord` / 重要寫操作都要保留 actor/audit 資訊，不可只知道 `ui|cli|api` 不知道是誰做的。

---

## 2) 完成定義（Definition of Done）

全部完成時，至少要滿足：

1. `uv run sc-app` 可啟動 NiceGUI Web UI。
2. `uv run <worker-entry>` 可啟動 Huey worker。
3. `/simulation` 送出模擬時，UI 只建立 persisted task/run boundary，不直接跑 Julia。
4. worker crash 不會把 NiceGUI process 一起帶死。
5. 刷新頁面後，使用者仍可從 DB 查到 task status / outputs / error summary。
6. 已保存的 raw simulation batch 可在沒有 live session state 的情況下重新 post-process。
7. CLI 可呼叫同一套 use cases，選擇同步執行或 dispatch background task，但 contract 必須一致。
8. 至少有一套 regression 覆蓋：
   - simulation task dispatch
   - persisted status transition
   - post-processing rerun from saved batch
   - worker failure surfacing
   - UI refresh/reconnect 後讀 persisted result
9. double-submit / retry / stale-running recovery 的語意已被定義並驗證。
10. app restart / worker restart 後，進行中的 run 可以被 reconcile 或清楚標記 failed/stale。
11. 使用者可登入 / 登出；`admin` / `user` 角色可正常工作。
12. audit logs 可回答「誰在什麼時間觸發了哪個 task / run / 重要寫操作」。

---

## 3) 推薦執行順序（嚴格）

1. WS1 Schema and Runtime Contracts
2. WS2 Task Persistence Boundary
3. WS3 Huey Worker Integration
4. WS4 Shared Application Use Cases
5. WS5 REST API Surface
6. WS6 Simulation UI Cutover
7. WS7 Post-Processing Sessionless Cutover
8. WS8 Characterization Alignment
9. WS9 CLI Alignment
10. WS10 Deployment / Dev Scripts / Docs / Regression Hardening

Reason:
- 先定 persisted contract，再接 queue/worker，再改 UI。
- 若先改 page，後面 contract 容易反覆打掉重做。
- idempotency / stale recovery / restart semantics 必須早於 UI cutover，不然 UI 行為會反覆重寫。

---

## 4) Multi-Agent 切分建議

### Integrator Agent

責任：
- 維護本文件
- 決定 task split / allowed files / merge order
- 做 final integration
- 跑 acceptance regression

### Platform Agent

Allowed Files（預設）：
- `src/core/shared/persistence/**`
- `src/core/**/application/**`
- `src/tasks*.py`
- `src/worker/**`
- `pyproject.toml`
- `tests/core/**`
- `tests/integration/**`

### Simulation Agent

Allowed Files（預設）：
- `src/app/pages/simulation/**`
- `src/app/services/**`
- `src/app/api/**`（若 task 指派）
- `tests/app/pages/test_simulation*`
- `tests/app/services/test_post_processing*`

### Characterization Agent

Allowed Files（預設）：
- `src/app/pages/characterization/**`
- `src/app/services/characterization*`
- `src/core/analysis/**`
- `tests/app/pages/test_characterization*`
- `tests/app/services/test_characterization*`

### Temporary Docs/QA Agent

只在需要時增派：
- `tmp/definitive_architecture_migration_todo.md`
- `docs/explanation/architecture/**`
- regression scripts

---

## 5) Context Compacting Recovery Protocol

任何新接手的 Agent，第一步固定做：

1. 讀本檔。
2. 讀 `Definitive Architecture` 原文。
3. 讀 `docs/explanation/architecture/trace-platform-implementation-plan.md`。
4. 跑 `git status --porcelain`。
5. 找本檔中第一個尚未完成且 dependency 已滿足的 Task Card。
6. 僅在自己的 `Allowed Files` 內工作。
7. 更新本檔對應 task 的狀態、證據、未決事項。
8. 交付時必附 `Contributor Report v1`。

禁止：
- 因為 context 不夠就自行更改架構方向。
- 因為看到其他 task 很像相關就順手跨界改。
- 沒有 persisted contract 就先硬接 page event。

---

## 6) Workstreams

### WS1. Schema and Runtime Contracts

Status: `completed`
Goal:
- 先把「Task / Run / Status / Error / Progress」contract 定義清楚，避免後面每層各說各話。

Tasks:

- [ ] DA-WS1-01 定義背景任務語意總表
  - 內容：
    - task kinds：`simulation_run`, `post_processing_run`, `characterization_run`
    - status：`queued`, `running`, `completed`, `failed`, `cancelled`
    - progress model：百分比是否必要；如果沒有，至少有 phase label + heartbeat time
    - error model：`error_code`, `error_summary`, `error_details`
  - Output:
    - 本檔更新
    - 必要時補 architecture note
  - Verification:
    - 所有後續 task card 都使用同一套欄位名

- [ ] DA-WS1-02 決定 `TaskRecord` 與 `TraceBatchRecord` / `AnalysisRunRecord` 的責任切分
  - 必答：
    - `TaskRecord` 是 generic queue execution record，還是直接把 execution authority 放進 batch/run tables？
    - raw trace-producing flow 是否以 `TraceBatchRecord(status=running...)` 為唯一 authority，`TaskRecord` 只作 queue shell？
    - analysis flow 是否仍保留 `AnalysisRunRecord` 作 logical boundary？
  - Decision frozen (`DF-001`)：
    - `TaskRecord` 是 **mandatory universal execution boundary**
    - `TaskRecord` 負責 queue/process/execution lifecycle（kind, status, timestamps, error）
    - `TraceBatchRecord` / `AnalysisRunRecord` 負責 domain-level provenance/output semantics
    - 透過 `TaskRecord.trace_batch_id` / `TaskRecord.analysis_run_id` nullable FK 關聯
    - Worker 完成時：先寫 domain record → 再關聯 task → mark completed（一個 UoW transaction）
  - Result:
    - 此題不再是 blocker；後續 Agent 直接依此 contract 實作

- [ ] DA-WS1-03 補 runtime state transition 表
  - 至少涵蓋：
    - create task → status=`queued`
    - dispatch to Huey → (no status change, Huey handles delivery)
    - worker picks up → status=`running`, `started_at` set
    - heartbeat → `heartbeat_at` updated, `progress_payload` updated
    - success writeback → status=`completed`, `completed_at` set, domain records linked
    - failure writeback → status=`failed`, `error_payload` written
    - reconnect/readback → UI reads `TaskRecord` by design_id, restores view
    - cancelled (stretch) → status=`cancelled`
  - 邊界情況必答：
    - Worker crash without writeback → stale `running` task，如何偵測？（heartbeat timeout）
    - 多個相同 design 的 task 同時存在 → 如何處理並發？

- [ ] DA-WS1-04 決定 Huey broker 和 application DB 的關係
  - 必答：
    - Huey SQLite broker 是否使用與 `data/database.db` 相同的 SQLite 檔案？
  - Decision frozen (`DF-002`)：
    - **分開**
    - Huey broker 用 `data/huey.db`
    - application data 用現有 `data/database.db`
    - 原因：Huey 的 WAL/lock 行為不應與 application 的 read-heavy workload 衝突
  - 後續實作：
    - 驗證 worker process 能同時連兩個 DB

- [ ] DA-WS1-05 定義 idempotency / dedupe contract
  - 必答：
    - 使用者連點 Run 兩次，是否建立兩個 task？
    - 同一 `design_id + setup_hash + source_batch_id + task_kind` 是否允許短時間內重複排隊？
    - CLI `--retry` 是建立新 task 還是重用原 task？
  - Decision frozen (`DF-003`)：
    - 採 **soft dedupe + force rerun**
    - `Task` 要有 CRUD
    - `Task List` 要即時更新
    - UI submit 後要短暫鎖定，避免連點
    - `TaskRecord` 增加 `dedupe_key`（indexed）
    - 預設情況下：若同 dedupe_key 且 status in (`queued`, `running`) → 回既有 task
    - 明確指定 `force_rerun` / `allow_duplicate` 時，允許建立新 task
    - `completed` / `failed` task 允許重建新 task
  - Result:
    - UI、CLI、API 都必須遵守同一 dedupe 語意，不可各自發明規則

- [ ] DA-WS1-06 定義 restart / stale recovery contract
  - 必答：
    - NiceGUI 重啟後如何識別 stale `running` task？
    - worker 重啟後是否自動接續未完成 Huey job，還是僅標記 stale？
    - app startup 是否跑 reconcile pass？
  - Decision frozen (`DF-005`)：
    - 採 **startup automatic reconcile**
    - app / worker 啟動時都執行自動 reconcile
    - stale 判準使用固定 heartbeat timeout
    - 自動把 stale `running` task 改成 `failed` 或 `abandoned`
    - 自動把對應 incomplete `TraceBatchRecord` 標成 failed/incomplete
    - orphaned Zarr store 需先明確判定是否為未完成輸出，再自動清理
    - 所有自動 reconcile 都必須寫 log / summary，且可由 UI/CLI 查閱
  - Safety rule:
    - 可以自動 reconcile，但不能做無條件盲刪

Acceptance:
- 所有 downstream 任務都能引用同一套 persisted orchestration contract。
- Huey broker 配置已決定且記錄。
- idempotency 與 restart recovery 語意已定義。

---

### WS2. Task Persistence Boundary

Status: `in progress`
Depends on:
- `DA-WS1-01`
- `DA-WS1-02`
- `DA-WS1-03`

Tasks:

- [x] DA-WS2-01 在 persistence models/repositories 增加 `TaskRecord`
  - Candidate fields:
    - `id` (PK, auto)
    - `task_kind` (str, indexed: `simulation_run` | `post_processing_run` | `characterization_run`)
    - `status` (str, indexed: `queued` | `running` | `completed` | `failed` | `cancelled`)
    - `design_id` (FK → `dataset_records.id`, indexed)
    - `trace_batch_id` (FK → `result_bundle_records.id`, nullable)
    - `analysis_run_id` (nullable, for characterization tasks)
    - `requested_by` (str: `ui` | `cli` | `api`)
    - `actor_id` (FK → `user_records.id`, nullable only for system/internal maintenance flows)
    - `dedupe_key` (str, indexed, nullable)
    - `request_payload` (JSON: 不含大型數值，只含 config snapshot)
    - `progress_payload` (JSON, nullable: phase label, current step, etc.)
    - `result_summary_payload` (JSON, nullable: 簡短 summary，不含 numeric data)
    - `error_payload` (JSON, nullable: `{"error_code": ..., "summary": ..., "details": ...}`)
    - `created_at` (datetime)
    - `started_at` (datetime, nullable)
    - `heartbeat_at` (datetime, nullable)
    - `completed_at` (datetime, nullable)
  - Notes:
    - 不要把大型數值結果塞進任何 payload 欄位
    - `result_summary_payload` 存的是 "N traces written, sweep 5×3 completed" 這類文字摘要
    - 實際數值結果透過 `trace_batch_id` → `TraceRecord` → `TraceStore(Zarr)` 路徑讀取
  - Completed:
    - `TaskRecord` 已落地於 `src/core/shared/persistence/models.py`
    - `analysis_run_id` 依現有 phase-2 physical carrier 對接 `result_bundle_records.id`
  - Evidence:
    - `src/core/shared/persistence/models.py`
    - `src/core/shared/persistence/repositories/task_repository.py`

- [x] DA-WS2-02 增加 repository / UoW contract
  - `TaskRepository` 方法：
    - `create_task(task_kind, design_id, request_payload, requested_by) → TaskRecord`
    - `mark_running(task_id) → None` (sets `started_at`)
    - `heartbeat(task_id, progress_payload) → None` (updates `heartbeat_at`)
    - `mark_completed(task_id, trace_batch_id, result_summary_payload) → None`
    - `mark_failed(task_id, error_payload) → None`
    - `get_task(task_id) → TaskRecord | None`
    - `list_tasks_by_design(design_id, status_filter?) → list[TaskRecord]`
    - `get_latest_task_by_kind(design_id, task_kind) → TaskRecord | None`
    - `find_active_by_dedupe_key(dedupe_key) → TaskRecord | None`
    - `list_stale_running_tasks(before_heartbeat_at) → list[TaskRecord]`
  - 加入 `SqliteUnitOfWork.tasks` property
  - Completed:
    - `TaskRepository` 已提供 create/running/heartbeat/completed/failed/get/list/latest/dedupe/stale API
    - `SqliteUnitOfWork.tasks` 已接線
  - Evidence:
    - `src/core/shared/persistence/repositories/task_repository.py`
    - `src/core/shared/persistence/repositories/contracts.py`
    - `src/core/shared/persistence/unit_of_work.py`

- [x] DA-WS2-07 增加 User/Auth/Audit persistence boundary
  - 新增最小模型：
    - `UserRecord`
      - `id`
      - `username` (unique, indexed)
      - `password_hash`
      - `role` (`admin` | `user`)
      - `is_active`
      - `created_at`
      - `last_login_at`
    - `AuditLogRecord`
      - `id`
      - `actor_id` (FK → `user_records.id`)
      - `action_kind`
      - `resource_kind`
      - `resource_id`
      - `summary`
      - `payload`
      - `created_at`
  - Task / run / important write path 至少要能帶出：
    - 誰觸發
    - 做了什麼
    - 影響了哪個 resource
  - 不要求 phase 1 做細粒度 ACL
  - Completed:
    - `UserRecord` / `AuditLogRecord` 已落地於 metadata DB schema
    - `TaskRecord.actor_id`、`requested_by`、`dedupe_key` 與 audit payload 欄位已準備好供 WS4/WS5 actor propagation 使用
  - Evidence:
    - `src/core/shared/persistence/models.py`
    - `src/core/shared/persistence/database.py`

- [x] DA-WS2-08 auth/audit repository contracts
  - `UserRepository`
    - `get_by_username`
    - `get_by_id`
    - `create_user`
    - `list_users`
    - `set_password`
    - `set_active`
  - `AuditLogRepository`
    - `append_log`
    - `list_logs`
    - `list_logs_by_actor`
  - `SqliteUnitOfWork.users`
  - `SqliteUnitOfWork.audit_logs`
  - Completed:
    - `UserRepository` 與 `AuditLogRepository` 已實作並匯出 contract
    - `SqliteUnitOfWork.users` / `SqliteUnitOfWork.audit_logs` 已接線
  - Evidence:
    - `src/core/shared/persistence/repositories/user_repository.py`
    - `src/core/shared/persistence/repositories/audit_log_repository.py`
    - `src/core/shared/persistence/repositories/contracts.py`
    - `src/core/shared/persistence/unit_of_work.py`

- [x] DA-WS2-03 補 contract tests
  - status transition: queued → running → completed
  - status transition: queued → running → failed
  - JSON payload roundtrip (request_payload, error_payload)
  - task 與 design / batch / analysis run 的 FK 關聯
  - `get_latest_task_by_kind` 正確性
  - 併發：同一 design 多個 task 不互相干擾
  - Completed:
    - 新增 task/auth/audit repository tests
    - UoW contract exposure 已加入 repository contract tests
  - Verification:
    - `uv run pytest tests/core/shared/persistence/test_task_auth_audit_repository.py tests/core/shared/persistence/test_repository_contracts.py tests/core/shared/persistence/test_result_bundle_repository.py`
  - Evidence:
    - `tests/core/shared/persistence/test_task_auth_audit_repository.py`
    - `tests/core/shared/persistence/test_repository_contracts.py`

- [x] DA-WS2-04 確認 DB bootstrap path 會建立新 table
  - 現有 `init_db()` 呼叫 `SQLModel.metadata.create_all`，新增 model 應自動建表
  - 須驗證：現有 137MB 的 `data/database.db` 上跑 `create_all` 不會影響既有資料
  - 須驗證：SQLite WAL mode 在 NiceGUI process + Worker process 同時連線時正常運作
  - Completed:
    - `init_db()` 已納入 `TaskRecord` / `UserRecord` / `AuditLogRecord` import side effects
    - temp SQLite bootstrap regression 已驗證新舊表共存建立
  - Verification:
    - `uv run pytest tests/core/shared/persistence/test_database_bootstrap.py`
  - Evidence:
    - `src/core/shared/persistence/database.py`
    - `tests/core/shared/persistence/test_database_bootstrap.py`

- [x] DA-WS2-05 Zarr dual-write atomicity 保護
  - 現有問題：`IncrementalRawSimulationSweepWriter` 逐點寫入 Zarr，若中途 crash，Zarr 有部分數據但 `TraceBatchRecord` 可能已 commit 或未 commit
  - 新增：
    - `TraceBatchRecord` 在寫入開始時 status = `in_progress`
    - 寫入完成後改為 `completed`
    - 讀取端過濾掉非 `completed` 的 batch
    - Worker cleanup: 若 task failed，清理對應的 orphaned Zarr store
  - 注意：不要改 `TraceStore` 的 interface，只在 application layer 加 status 檢查
  - Completed:
    - `TraceBatchRepository` 已增加 `mark_in_progress` / `mark_completed` / `mark_failed`
    - `get_snapshot()` / `get_trace_batch_snapshot()` 已過濾非 `completed` batches
    - current raw simulation save path 與 post-process save path 已切到先 `in_progress`，完成後 `completed`，失敗時 `failed`
    - reconcile helper 已可針對 failed/incomplete batch 清理已知 local Zarr store keys
  - Evidence:
    - `src/core/shared/persistence/repositories/result_bundle_repository.py`
    - `src/core/shared/persistence/reconcile.py`
    - `src/app/pages/simulation/__init__.py`
    - `tests/core/shared/persistence/test_result_bundle_repository.py`
    - `tests/core/shared/persistence/test_reconcile.py`

- [ ] DA-WS2-06 stale/orphan reconcile path
  - 需要一個固定入口：
    - app startup reconcile
    - worker startup reconcile
    - 或 manual admin command
  - 職責：
    - 找出 heartbeat timeout 的 `running` tasks
    - 將對應 batch 標記 `failed` / `abandoned`
    - 清理 orphaned Zarr store（若 policy 決定清）
    - 產生可追蹤的 summary log
  - 建議：
    - 先做 manual/admin reconcile command，再評估自動化
    - 避免 app start 時做 destructive cleanup；先 mark stale 再由 explicit cleanup 處理
  - Progress:
    - 已新增 persistence-level manual reconcile entrypoint `reconcile_stale_tasks_and_batches()`
    - 已覆蓋 stale task → failed、orphan incomplete batch → failed、known local store cleanup、system audit logs
  - Remaining:
    - 尚未接到 app startup / worker startup / admin command surface
  - Verification:
    - `uv run pytest tests/core/shared/persistence/test_reconcile.py`
  - Evidence:
    - `src/core/shared/persistence/reconcile.py`
    - `tests/core/shared/persistence/test_reconcile.py`

Acceptance:
- 可以在不啟 UI 的情況下，單純用 persistence contract 建立並更新 task lifecycle。
- Zarr dual-write 有 status-based 保護。
- stale running / orphan batch 有一致的 reconcile path。
- user/auth/audit persistence contracts 已存在，後續 app/api 層不需再臨時發明身份模型。

---

### WS3. Huey Worker Integration

Status: `completed`
Depends on:
- `DA-WS2-01`
- `DA-WS2-02`

Tasks:

- [x] DA-WS3-01 在 `pyproject.toml` 引入 `huey`
  - 加入 `huey>=2.5` 到 `[project].dependencies`
  - 確認 Huey 的 `SqliteHuey` backend 不需要額外依賴

- [x] DA-WS3-02 建立 Huey app / consumer entrypoint
  - 建議結構：
    - `src/worker/__init__.py`
    - `src/worker/huey_app.py` — Huey instance 定義（`SqliteHuey(filename='data/huey.db')`）
    - `src/worker/tasks.py` — task 函數定義
  - `pyproject.toml` 加入 worker entrypoint：`sc-worker = "worker.entry:main"` 或直接用 `huey_consumer worker.huey_app.huey`
  - NiceGUI Process 不 import `worker.tasks`（避免觸發 Julia init）

- [x] DA-WS3-03 建立最小 smoke task
  - 只更新 `TaskRecord` status，證明 queue → worker → DB writeback path 正常
  - 測試：`python -c "from worker.tasks import smoke_task; smoke_task(task_id=1)"`

- [x] DA-WS3-04 worker init policy（關鍵！）
  - JuliaCall 只在 worker process 初始化，做法：
    - `worker/tasks.py` 頂層 import `run_simulation`（這會 lazy-load Julia via `juliacall`）
    - `app/main.py` 和 `app/pages/` 完全不 import `core.simulation.infrastructure.julia_adapter`
    - 驗收：`uv run sc-app` 啟動時不觸發 Julia init（可用 `PYTHON_JULIACALL_TRACE=1` 驗證）
  - Julia 冷啟動成本：
    - JuliaCall 首次 import 約 5-15 秒（取決於 JosephsonCircuits.jl 的 precompile 狀態）
    - Worker consumer 啟動後第一個 task 會包含此成本
    - 後續 task 在同一 worker process 內可復用已初始化的 Julia runtime
    - 策略：worker consumer 長駐，不要 per-task spawn process

- [x] DA-WS3-05 worker failure semantics
  - 三種 failure 模式需分別處理：
    - **Python exception** (e.g. ValueError, 網路錯) → 捕捉，寫 `error_payload`，task → `failed`
    - **Julia exception** (e.g. SingularMatrix) → JuliaCall 會轉為 Python exception，同上處理
    - **Worker process crash** (e.g. Julia segfault / OOM) → Huey consumer 重啟後，stale `running` task 須靠 heartbeat timeout 偵測
  - 實作：Huey task decorator 加 `@huey.task(retries=0)` + 外層 try/except 全捕捉
  - 偵測 stale tasks：定期（或 UI 查詢時）檢查 `status=running AND heartbeat_at < NOW - threshold`

- [x] DA-WS3-06 crash isolation 驗證
  - 必須實測：worker process crash 後 NiceGUI process 仍存活
  - 測試方式：建一個 test task 故意 `os._exit(1)`，確認 NiceGUI 能偵測到 task 變 stale

- [x] DA-WS3-07 worker concurrency policy
  - 必答：
    - Huey consumer 預設跑幾個 worker threads/processes？
    - Julia tasks 是否允許並行？
    - 同一 design 的兩個 simulation tasks 是否允許同時執行？
  - Decision frozen (`DF-004`)：
    - 採 **雙 lane 並行**
    - `simulation lane`：simulation / post-processing，lane 內單一任務序列化
    - `characterization lane`：characterization heavy work，lane 內單一任務序列化
    - 兩條 lane 可以彼此並行
    - phase 1 不做 lane 內多工
  - 後續實作：
    - 定義 queue routing / worker naming / consumer 啟動方式
    - 驗證雙 lane 並行時 SQLite / Zarr / CPU 負載仍可控

- [x] DA-WS3-08 worker lane topology
  - Decision frozen (`DF-012`)：
    - 採兩個完全獨立的 worker consumer stack
    - `simulation_huey` / `simulation queue` / `simulation consumer`
    - `characterization_huey` / `characterization queue` / `characterization consumer`
    - 兩條 lane 各自一個 consumer process
    - 共用 application DB，但 queue runtime 分離
  - 後續實作：
    - `src/worker/simulation_huey.py`
    - `src/worker/characterization_huey.py`
    - lane-specific task registration
    - lane-specific startup commands
  - Why:
    - lane 邊界最乾淨，debug 最容易，未來較不易重構

Acceptance:
- 能從 shell 建立 task，worker 消費後寫回 DB。
- Julia import 失敗不會讓 NiceGUI process 掛掉。
- Worker crash 不影響 NiceGUI，且 stale task 有偵測機制。
- worker concurrency policy 已明確，沒有隱含 race assumption。

Progress:
- 已新增 `huey>=2.5`，並建立兩個完全分離的 lane-specific broker stacks：
  - `src/worker/simulation_huey.py`
  - `src/worker/characterization_huey.py`
- broker DB 與 app DB 分離：
  - app DB 保持 `data/database.db`（或 `SC_DATABASE_PATH` override）
  - simulation broker：`data/huey/simulation_huey.db`
  - characterization broker：`data/huey/characterization_huey.db`
- lane consumer 都採單進程、序列化 dequeue/execute loop；符合 `DF-004` / `DF-012`
- 已新增 smoke / failure / crash tasks：
  - `simulation_smoke_task`
  - `simulation_failure_task`
  - `simulation_crash_task`
  - `characterization_smoke_task`
  - `characterization_failure_task`
  - `characterization_crash_task`
- Python exception 會被 worker runtime 捕捉並寫回 `TaskRecord.error_payload`
- crash task 會先把 task 標成 `running` 再 `os._exit(86)`；stale task 之後可由 WS2 reconcile path 偵測並標成 `failed`
- `app.main` 未新增任何 worker import；worker lane import 仍留在 `src/worker/**`
- `core.simulation.application.run_simulation` 已改成 execution-time lazy import `JuliaSimulator`；`import app.main` 不再載入 `core.simulation.infrastructure.julia_adapter`

Verification:
- `uv sync`
- `uv run pytest tests/worker/test_huey_workers.py tests/core/shared/persistence/test_task_auth_audit_repository.py tests/core/shared/persistence/test_result_bundle_repository.py tests/core/shared/persistence/test_reconcile.py tests/core/shared/persistence/test_repository_contracts.py tests/core/shared/persistence/test_database_bootstrap.py`
- `uv run ruff check src/worker tests/worker src/core/shared/persistence`
- `uv run basedpyright src/worker src/core/shared/persistence`
- `uv run python - <<'PY' ... import app.main ... PY`
- `PYTHON_JULIACALL_TRACE=1 uv run python -c "import app.main; print('APP_IMPORT_OK')"`
- shell smoke:
  - simulation lane consumer
  - characterization lane consumer
  - crash + reconcile drill
  - app import / startup isolation smoke

Evidence:
- `pyproject.toml`
- `src/worker/config.py`
- `src/worker/runtime.py`
- `src/worker/simulation_huey.py`
- `src/worker/characterization_huey.py`
- `src/worker/simulation_tasks.py`
- `src/worker/characterization_tasks.py`
- `tests/worker/test_huey_workers.py`
- `src/core/simulation/application/run_simulation.py`

---

### WS4. Shared Application Use Cases

Status: `completed`
Execution Owner: `Migration Agent (Codex)`
Depends on:
- `DA-WS3-02`

Tasks:

- [x] DA-WS4-01 梳理 simulation shared use case 邊界
  - 把 page 內純 orchestration 邏輯抽成 worker/UI/CLI 都可共用的 function
  - 優先抽：
    - create simulation run request
    - resolve cache hit
    - persist running batch
    - persist success/failure summary

- [x] DA-WS4-02 梳理 post-processing shared use case 邊界
  - 目標：
    - input 改為 persisted source batch / persisted trace refs
    - 不再依賴 `latest_simulation_result`

- [x] DA-WS4-03 梳理 characterization shared use case 邊界
  - 目標：
    - analysis run contract 與 worker task contract 對齊
    - future-proof 到 `/api/characterization-runs`

- [x] DA-WS4-04 決定 sync vs async adapter 層
  - CLI 可能要支援：
    - `--wait` 同步等待完成
    - `--detach` 只建立 task 後離開

- [x] DA-WS4-05 heartbeat / progress payload parity
  - 現況：
    - simulation page 與 characterization page 都有 page-local heartbeat/status_history UX
  - 目標：
    - worker 端 progress event 能映射成 `TaskRecord.progress_payload`
    - UI 的 `status_history` 只作 render cache，不再是唯一訊息來源
  - 至少定義：
    - phase labels
    - heartbeat warning threshold
    - user-facing summary lines 的來源

- [x] DA-WS4-06 actor context propagation
  - 目標：
    - login session / API actor → use case request context → `TaskRecord.actor_id` / `AuditLogRecord.actor_id`
    - worker 執行時仍保留「誰觸發了這個 task」的 actor context
  - 最低要求：
    - app/api layer 建一個 `ActorContext`
    - domain/application 層不直接依賴 HTTP session object
    - worker task input 可重建 actor context（至少 actor_id + role）

Acceptance:
- 重要流程不再被 page event handler 或 CLI command body 綁死。
- heartbeat 與 progress UX 不因 cutover 而消失。
- auth 加入後，不需要重寫 application/use-case boundary。

Progress:
- 已新增 shared execution contracts：
  - `app/services/execution_context.py`
  - `app/services/task_progress.py`
- 已建立三條可共用的 request/result/context boundary：
  - `app/services/simulation_runner.py`
  - `app/services/post_processing_runner.py`
  - `app/services/characterization_runner.py`
- `ActorContext` / `UseCaseContext` 已提供 `actor_id + role + requested_by + source + task_id + dedupe/force_rerun` shape，後續 API/auth 可直接沿用而不需把 session object 帶進 domain/application
- `TaskProgressUpdate` 已定義 reusable progress payload shape：
  - `phase`
  - `summary`
  - `stage_label`
  - `current_step` / `total_steps`
  - `warning`
  - `stale_after_seconds`
  - `details`
- WS3 worker runtime 已改用 shared progress payload helper 產生 `TaskRecord.progress_payload` / completion summary payload
- simulation page 已把 Julia solver 呼叫改成 shared `SimulationRunRequest -> execute_simulation_run` boundary
- post-processing page 已以 enriched `PostProcessingRunRequest(context=...)` 執行 shared boundary，page-local code 不再直接持有 actor/session-specific authority
- characterization page 已把 run dispatch 改成 shared `CharacterizationRunRequest -> execute_characterization_run` boundary
- 已新增 tests 證明 shared use-case modules 可由 worker-facing import 使用，且不會拉進 `app.pages.*`

Verification:
- `uv run pytest tests/app/services/test_simulation_runner.py tests/app/services/test_post_processing_runner.py tests/app/services/test_characterization_runner.py tests/worker/test_huey_workers.py tests/core/shared/persistence/test_task_auth_audit_repository.py tests/core/shared/persistence/test_result_bundle_repository.py tests/core/shared/persistence/test_reconcile.py tests/core/shared/persistence/test_repository_contracts.py tests/core/shared/persistence/test_database_bootstrap.py`
- `uv run ruff check src/app/services/execution_context.py src/app/services/task_progress.py src/app/services/simulation_runner.py src/app/services/post_processing_runner.py src/app/services/characterization_runner.py src/worker/runtime.py tests/app/services/test_simulation_runner.py tests/app/services/test_post_processing_runner.py tests/app/services/test_characterization_runner.py tests/worker/test_huey_workers.py src/app/pages/simulation/__init__.py src/app/pages/characterization/__init__.py`
- `uv run basedpyright src/app/services/execution_context.py src/app/services/task_progress.py src/app/services/simulation_runner.py src/app/services/post_processing_runner.py src/app/services/characterization_runner.py src/worker/runtime.py src/app/pages/simulation/__init__.py src/app/pages/characterization/__init__.py`
- `uv run python -m py_compile src/app/pages/simulation/__init__.py src/app/pages/characterization/__init__.py`
- `uv run python - <<'PY' ... execute_simulation_run(...) ... PY`

Evidence:
- `src/app/services/execution_context.py`
- `src/app/services/task_progress.py`
- `src/app/services/simulation_runner.py`
- `src/app/services/post_processing_runner.py`
- `src/app/services/characterization_runner.py`
- `src/worker/runtime.py`
- `src/app/pages/simulation/__init__.py`
- `src/app/pages/characterization/__init__.py`
- `tests/app/services/test_simulation_runner.py`
- `tests/app/services/test_post_processing_runner.py`
- `tests/app/services/test_characterization_runner.py`
- `tests/worker/test_huey_workers.py`

---

### WS5. REST API Surface

Status: `not started`
Depends on:
- `DA-WS4-01`
- `DA-WS4-02`

Tasks:

- [ ] DA-WS5-01 在 NiceGUI/FastAPI app 上建立 API module 結構
  - Candidate:
    - `src/app/api/__init__.py`
    - `src/app/api/tasks.py`
    - `src/app/api/designs.py`
    - `src/app/api/simulation_runs.py`

- [ ] DA-WS5-02 tasks API
  - phase 1 required:
    - `POST /api/v1/tasks/simulation`
    - `POST /api/v1/tasks/post-processing`
    - `POST /api/v1/tasks/characterization`
    - `GET /api/v1/tasks/{task_id}`
    - `GET /api/v1/designs/{design_id}/tasks`

- [ ] DA-WS5-03 persisted result lookup API
  - UI refresh 後需要：
    - 找 design 下最近 raw simulation batch
    - 找最近 post-processing batch
    - 找 task 對應 outputs
  - phase 1 required:
    - `GET /api/v1/designs/{design_id}/simulation/latest`
    - `GET /api/v1/designs/{design_id}/post-processing/latest`
    - `GET /api/v1/designs/{design_id}/characterization/latest`

- [ ] DA-WS5-04 auth/config seam
  - Decision frozen (`DF-010`)：
    - phase 1 直接支援 multi-user local auth
    - local username/password + session cookie
    - 角色僅兩種：`admin`, `user`
    - UI pages 與 `/api/v1/*` 都必須受保護
    - queue 共享，不做 per-user queue 切分
    - 不做細粒度 RBAC / ACL

- [ ] DA-WS5-06 login/session/auth API 與 page guard
  - 最低包含：
    - login endpoint / form
    - logout endpoint / action
    - current-session / current-user lookup
    - page guard（未登入不能進 app pages）
    - `/api/v1/*` auth guard
  - 角色要求：
    - `admin`：可管理 users、可看全部 audit logs
    - `user`：可登入、可建立 task、可看共享 task/result

- [ ] DA-WS5-07 audit log API / admin surfaces
  - `admin` 可查：
    - user list
    - audit logs
    - shared task history
  - 至少先有 API；UI 可以 phase 1 簡版

- [ ] DA-WS5-08 public API auth contract
  - `/api/v1/*` response 需清楚區分：
    - `401 unauthenticated`
    - `403 unauthorized`
  - auth 不可只保護 UI，不保護 API

- [ ] DA-WS5-09 完整 API inventory（必寫，即使 phase 1 不全做）
  - 目標：
    - 列出完整 planned API surface
    - 每個 endpoint 標註：
      - `phase 1 required`
      - `planned later`
      - `admin only` / `authenticated user`
  - Decision frozen (`DF-011`)：
    - `/api/v1` 採 completeness-first inventory
    - 先完整列出 CRUD / Lifecycle / Functionality
    - 再標註 `phase 1 required` 與 `planned later`
  - Frozen inventory:
    - `auth` (Functionality)
      - `POST /api/v1/auth/login`
        - access: public
        - phase: `phase 1 required`
      - `POST /api/v1/auth/logout`
        - access: authenticated user
        - phase: `phase 1 required`
      - `GET /api/v1/auth/me`
        - access: authenticated user
        - phase: `phase 1 required`
    - `users` (CRUD + admin)
      - `GET /api/v1/admin/users`
        - access: admin only
        - phase: `phase 1 required`
      - `POST /api/v1/admin/users`
        - access: admin only
        - phase: `phase 1 required`
      - `GET /api/v1/admin/users/{user_id}`
        - access: admin only
        - phase: `planned later`
      - `PATCH /api/v1/admin/users/{user_id}`
        - access: admin only
        - phase: `phase 1 required`
      - `POST /api/v1/admin/users/{user_id}/password-reset`
        - access: admin only
        - phase: `phase 1 required`
      - `POST /api/v1/users/me/password-change`
        - access: authenticated user
        - phase: `planned later`
    - `audit-logs` (Functionality + admin)
      - `GET /api/v1/admin/audit-logs`
        - access: admin only
        - phase: `phase 1 required`
      - `GET /api/v1/admin/audit-logs/{log_id}`
        - access: admin only
        - phase: `planned later`
    - `tasks` (Lifecycle)
      - `POST /api/v1/tasks/simulation`
        - access: authenticated user
        - phase: `phase 1 required`
      - `POST /api/v1/tasks/post-processing`
        - access: authenticated user
        - phase: `phase 1 required`
      - `POST /api/v1/tasks/characterization`
        - access: authenticated user
        - phase: `phase 1 required`
      - `GET /api/v1/tasks/{task_id}`
        - access: authenticated user
        - phase: `phase 1 required`
      - `GET /api/v1/designs/{design_id}/tasks`
        - access: authenticated user
        - phase: `phase 1 required`
      - `POST /api/v1/tasks/{task_id}/cancel`
        - access: authenticated user
        - phase: `planned later`
      - `POST /api/v1/tasks/{task_id}/retry`
        - access: authenticated user
        - phase: `planned later`
    - `designs` (CRUD)
      - `GET /api/v1/designs`
        - access: authenticated user
        - phase: `planned later`
      - `POST /api/v1/designs`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/designs/{design_id}`
        - access: authenticated user
        - phase: `planned later`
      - `PATCH /api/v1/designs/{design_id}`
        - access: authenticated user
        - phase: `planned later`
      - `DELETE /api/v1/designs/{design_id}`
        - access: admin only
        - phase: `planned later`
    - `schemas` (CRUD)
      - `GET /api/v1/schemas`
        - access: authenticated user
        - phase: `planned later`
      - `POST /api/v1/schemas`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/schemas/{schema_id}`
        - access: authenticated user
        - phase: `planned later`
      - `PATCH /api/v1/schemas/{schema_id}`
        - access: authenticated user
        - phase: `planned later`
      - `DELETE /api/v1/schemas/{schema_id}`
        - access: admin only
        - phase: `planned later`
    - `raw-data / traces / batches` (CRUD + browsing)
      - `GET /api/v1/designs/{design_id}/traces`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/traces/{trace_id}`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/designs/{design_id}/batches`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/batches/{batch_id}`
        - access: authenticated user
        - phase: `planned later`
      - `POST /api/v1/designs/{design_id}/raw-data/import`
        - access: authenticated user
        - phase: `planned later`
    - `simulation` (Lifecycle + Functionality)
      - `GET /api/v1/designs/{design_id}/simulation/latest`
        - access: authenticated user
        - phase: `phase 1 required`
      - `GET /api/v1/designs/{design_id}/simulation/runs`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/simulation/runs/{run_id}`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/simulation/runs/{run_id}/result`
        - access: authenticated user
        - phase: `planned later`
    - `post-processing` (Lifecycle + Functionality)
      - `GET /api/v1/designs/{design_id}/post-processing/latest`
        - access: authenticated user
        - phase: `phase 1 required`
      - `GET /api/v1/designs/{design_id}/post-processing/runs`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/post-processing/runs/{run_id}`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/post-processing/runs/{run_id}/result`
        - access: authenticated user
        - phase: `planned later`
    - `characterization` (Lifecycle + Functionality)
      - `GET /api/v1/designs/{design_id}/characterization/latest`
        - access: authenticated user
        - phase: `phase 1 required`
      - `GET /api/v1/designs/{design_id}/characterization/runs`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/characterization/runs/{analysis_run_id}`
        - access: authenticated user
        - phase: `planned later`
      - `GET /api/v1/characterization/runs/{analysis_run_id}/artifacts`
        - access: authenticated user
        - phase: `planned later`
  - Output:
    - 本檔直接附完整 API inventory 表
    - 明確區分 phase 1 vs planned later
  - Rule:
    - 不可因為 phase 1 不做就不列；完整規劃要先存在

- [ ] DA-WS5-05 API schema / stability boundary
  - 必答：
    - `/api/internal/*` 還是 `/api/*`？
    - response schema 是否固定包含 `task_id`, `status`, `trace_batch_id`, `analysis_run_id`, `error`
    - 哪些 endpoint 視為 unstable internal contract？
  - Decision frozen (`DF-006`)：
    - API 從第一天起視為 public contract
    - 使用 `/api/v1/*`
    - phase 1 只公開最小必要 endpoint
    - response schema 必須 typed、穩定、可測
    - 後續 breaking change 走 `v2`，不回頭破壞 `v1`

Acceptance:
- UI 不必直接埋 persistence 細節；可以靠 API 重建頁面狀態。
- API contract boundaries 已被凍結，後續 Agent 不需要臆測 response shape。
- auth 與 session contract 已納入 API 邊界，而不是事後外掛。
- 完整 API inventory 已寫出，phase 1 / later scope 清楚分離，避免因漏規劃再重構。

---

### WS6. Simulation UI Cutover

Status: `not started`
Depends on:
- `DA-WS5-02`
- `DA-WS5-03`

Tasks:

- [ ] DA-WS6-01 列出 `/simulation` 目前所有 authority 使用點
  - **A) `SimulationRuntimeState.latest_*` 欄位（14 個）**：
    - `latest_sweep` — 模擬 sweep payload
    - `latest_simulation_result` — SimulationResult domain object（可能數百 MB）
    - `latest_simulation_sweep_payload` — sweep config dict
    - `latest_post_processing_runtime` — PortMatrixSweep/PortMatrixSweepRun
    - `latest_post_processing_bundle_id` — 後處理 batch ID
    - `latest_source_simulation_bundle_id` — 源模擬 batch ID
    - `latest_flow_spec` — 後處理 pipeline config
    - `latest_circuit_record` — 電路記錄
    - `latest_schema_source_hash` — schema 變更偵測
    - `latest_simulation_setup_hash` — 模擬設定變更偵測
    - `latest_sweep_setup_hash` — sweep 設定變更偵測
    - `latest_raw_save_callback` — **閉包引用，最脆弱的一環**
    - `termination_last_warning` — 端口補償警告
    - `termination_last_summary` — 端口補償摘要
  - **B) Module-level (process-global) cache dict（4 個）**：
    - `_SWEEP_RUN_CACHE` — SwepRun 物件 cache (limit 8)
    - `_SWEEP_POINT_LOOKUP_CACHE` — sweep point 查找 cache (limit 8)
    - `_SWEEP_SERIES_CACHE` — 繪圖用 series cache (limit 512)
    - `_TRACE_STORE_AUTHORITY_CACHE` — TraceStore 讀取 authority cache (limit 8)
  - **C) `run.io_bound()` 呼叫點（4 處）**：
    - 行 7504: 持久化後處理結果
    - 行 9494: 載入 circuit record + circuit definition
    - 行 10117: 儲存模擬結果到 cache dataset
    - 行 10806: 儲存到 dataset
  - 先做完整 mapping 到 spreadsheet/table，不要直接邊找邊改

- [ ] DA-WS6-02 切 simulation submit path
  - 現在按 Run 應只：
    - validate form
    - 建立 `TaskRecord(status=queued)` + 空 `TraceBatchRecord(status=in_progress)`
    - dispatch Huey task（傳入 `task_id`）
    - 顯示 queued/running state（用 `ui.timer` polling）
  - Julia 呼叫（行 ~9980 `run_simulation()`）移入 worker task

- [ ] DA-WS6-03 切 result polling / refresh path
  - UI 應從 `/api/tasks/{id}` + persisted batch 查結果
  - reconnect / F5 後流程：
    1. 讀 `TaskRecord` by current design_id → 找到最新 task
    2. 若 `status=running` → 恢復 polling UI
    3. 若 `status=completed` → 從 `trace_batch_id` 讀結果
    4. 若 `status=failed` → 顯示 error summary
  - 用 `ui.timer(interval=2.0, callback=poll)` 而非 WebSocket push（simpler）

- [ ] DA-WS6-04 降低 page-local state 職責
  - 保留（transient UI state，OK to lose on F5）：
    - form draft values
    - transient UI selection (mode, trace selection)
    - just-submitted task_id（用於 polling）
    - result view state（family, metric, z0）
  - 移除 authority（改讀 DB）：
    - raw simulation result → 從 persisted batch 讀
    - post-processing result → 從 persisted post-proc batch 讀
    - status truth → 從 TaskRecord 讀
    - `latest_raw_save_callback` → 完全移除（Worker 自動持久化）
  - Module-level cache 決策：
    - Decision frozen (`DF-009`)：**全部移除**
    - `_TRACE_STORE_AUTHORITY_CACHE`：移除
    - `_SWEEP_RUN_CACHE`：移除
    - `_SWEEP_POINT_LOOKUP_CACHE`：移除
    - `_SWEEP_SERIES_CACHE`：移除
    - phase 1 不保留任何 module-level process-global cache
    - 所有結果回到 persisted source + deterministic recomputation

- [ ] DA-WS6-05 拆 `simulation/__init__.py`
  - 10832 行不可能一次重寫，按 area 拆：
    - `simulation/api_client.py` — API 呼叫封裝（submit, poll, load result）
    - `simulation/submit_actions.py` — form validation + task creation
    - `simulation/result_loader.py` — 從 DB+Zarr 讀結果並建立 plotly traces
    - `simulation/sections/` — UI section components
    - `simulation/state.py` — 保留，但大幅縮減為 transient-only state
  - 拆分順序：先抽 `api_client` + `submit_actions`（最小 viable 切割）

- [ ] DA-WS6-06 simulation heartbeat/status UX parity
  - 目前 `status_history` 與 long-running heartbeat warning 是使用者可見行為
  - cutover 後必須保留：
    - queued/running/completed/failed 明確可見
    - 長任務 warning 仍顯示
    - task id / batch id 可追蹤
  - 不要求保留每個字串文案，但要求保留語意與 debug usefulness

Acceptance:
- `/simulation` 刷新後不會因為 `latest_*` 消失而失去結果。
- Julia 呼叫不在 NiceGUI process 中發生。
- Module-level caches 已全部移除，不再存在 authority/optimization 混淆。
- simulation 的 heartbeat/status UX 未退化到黑盒狀態。

---

### WS7. Post-Processing Sessionless Cutover

Status: `not started`
Depends on:
- `DA-WS6-02`
- `DA-WS6-03`

Tasks:

- [ ] DA-WS7-01 post-processing input authority 改成 persisted source batch
- [ ] DA-WS7-02 rerun flow 可從 saved raw batch 重啟
- [ ] DA-WS7-03 post-processing result view 只從 persisted batch + TraceStore 讀取
- [ ] DA-WS7-04 斷線/重整後仍能查到 post-processing 狀態與結果

Acceptance:
- Definitive Architecture 中最核心的一條 requirement 落地：raw batch 可在沒有 live result 的情況下再加工。

---

### WS8. Characterization Alignment

Status: `not started`
Depends on:
- `DA-WS2-01`
- `DA-WS4-03`

注意：`characterization/__init__.py` 也是 **145KB** 的大型 page module，不可低估改動量。

Tasks:

- [ ] DA-WS8-01 決定 characterization 是否同樣走 Huey task
  - 分析不同 analysis 的執行時間：
    - 快速分析（< 2s，如 resonance extraction）→ 可先同步執行，但 contract 走 `TaskRecord`
    - 慢速分析（> 5s，如 SQUID fit）→ 應走 Huey worker
  - Decision frozen (`DF-007`)：
    - `Characterization` 視為 **heavy-work capable workflow**
    - canonical run path 一律對齊 `TaskRecord + AnalysisRunRecord + worker-compatible execution`
    - `Characterization` 屬於獨立的 `characterization lane`
    - lane 內先序列化，但可與 simulation lane 並行
  - Implementation note:
    - 可以分批把不同 analysis 實際搬進 worker
    - 但架構上不再保留 page-local synchronous authority 路線

- [ ] DA-WS8-02 讓 `AnalysisRunRecord` 與 `TaskRecord` 對齊
  - 確認 `AnalysisRunRecord` 是否已有足夠的 status/error 欄位
  - 若沒有，加入或透過 `TaskRecord` FK 補齊

- [ ] DA-WS8-03 `/characterization` authority audit（類似 DA-WS6-01）
  - 列出 characterization page 中所有 session-local authority 使用點
  - `characterization/state.py` 檢查
  - `app/services/characterization_runner.py` 的 input contract 檢查
  - `app/services/characterization_trace_scope.py` (486 lines) 的 scope query 路徑檢查

- [ ] DA-WS8-04 `/characterization` history/result navigation 改讀 persisted run

- [ ] DA-WS8-05 analysis failure / diagnostics 寫回 persisted records

- [ ] DA-WS8-06 characterization heartbeat/status UX parity
  - 現況：
    - `characterization/state.py` 有 `analysis_status_history`
    - page 內已有 long-running heartbeat warning 行為
  - 目標：
    - 與 simulation 同樣切到 persisted progress source
    - refresh 後可重建近期 status / diagnostics

Acceptance:
- `Characterization` 與 simulation/post-processing 擁有一致的 persisted execution semantics。
- `/characterization` F5 刷新後不失去 analysis 結果。
- Characterization 的 debug / progress 可見性不退化。

---

### WS9. CLI Alignment

Status: `not started`
Depends on:
- `DA-WS4-04`
- `DA-WS5-02`

Tasks:

- [ ] DA-WS9-01 決定 CLI 是直接呼叫 shared use cases 還是打本地 API
  - 建議：
    - CLI 直接呼叫 shared use cases
    - 不強迫依賴已啟動的 web server
- [ ] DA-WS9-02 simulation CLI 支援建立 task / wait for completion
- [ ] DA-WS9-03 post-processing CLI 支援從 persisted source batch rerun
- [ ] DA-WS9-04 CLI output 對齊 task/run identifiers

- [ ] DA-WS9-05 CLI exit code / output contract
  - 必答：
    - `--wait` 成功時 exit 0；failed/stale 時 exit non-zero
    - `--detach` 成功建立 task 時 exit 0 並輸出 task id
    - stderr/stdout 各承載什麼
  - Decision frozen (`DF-008`)：
    - CLI 預設採 `--wait`
    - `--detach` 作為 opt-in
    - `--wait` 模式下要顯示 logs / progress，而不是靜默等待
  - 若不定義，後面 shell script / CI 整合會不穩定

Acceptance:
- CLI 與 UI 是同一架構的兩個入口，不是兩套平行實作。
- CLI 可被 shell script / automation 穩定調用。

---

### WS10. Deployment / Dev Scripts / Docs / Regression Hardening

Status: `not started`
Depends on:
- `DA-WS6-03` (至少 simulation cutover 的 polling path 完成)
- `DA-WS7-01`
- `DA-WS8-01`
- `DA-WS9-01`

Tasks:

- [ ] DA-WS10-01 補 dev startup scripts
  - **本地模式**：
    ```bash
    # 終端 1
    uv run sc-app
    # 終端 2
    uv run huey_consumer worker.huey_app.huey
    ```
  - **一鍵啟動** (optional)：`scripts/dev_start.sh` 用 `&` 背景啟動兩者
  - **遠端模式**：
    ```bash
    SC_APP_HOST=0.0.0.0 SC_DEPLOYMENT_SCOPE=trusted_lan uv run sc-app
    uv run huey_consumer worker.huey_app.huey
    ```
  - `pyproject.toml` 新增 script entry：`sc-worker = ...`

- [ ] DA-WS10-02 補 `.env` / config surface 文件
  - `SC_APP_HOST` (default: `127.0.0.1`)
  - `SC_APP_PORT` (default: `8080`)
  - `SC_HUEY_DB` (default: `data/huey.db`)
  - `SC_DATABASE_PATH` (default: `data/database.db`)
  - `SC_TRACE_STORE_PATH` (default: `data/trace_store`)
  - `SC_SESSION_SECRET`
  - `SC_BOOTSTRAP_ADMIN_USERNAME`
  - `SC_BOOTSTRAP_ADMIN_PASSWORD`
  - 寫成 `.env.example` 文件
  - auth bootstrap 規則：
    - 首次啟動可透過 env 建立 admin user
    - 實際密碼不可寫死在 repo
    - `.env.example` 只放 placeholder

- [ ] DA-WS10-03 補 regression matrix
  - **Unit tests**:
    - TaskRecord CRUD + status transitions
    - TaskRepository contract tests
    - Huey task function (mocked Julia)
  - **Integration tests**:
    - task dispatch → worker consume → DB writeback (end-to-end)
    - persisted batch + Zarr write consistency
    - post-processing rerun from saved batch
  - **Crash isolation test**:
    - worker process 故意 crash 後 NiceGUI 仍存活
    - stale task 偵測機制正確觸發
  - **UI/E2E** (Playwright):
    - simulation submit → polling → result display
    - F5 refresh → result recovery
    - worker failure → error display
    - login → protected page access
    - logout → session invalidation
    - admin 可看 audit logs / user management
    - normal user 不可進 admin-only surface

- [ ] DA-WS10-04 更新 architecture docs
  - 僅在 code contract 穩定後更新，不要先寫假文件
  - 更新 `docs/explanation/architecture/trace-platform-implementation-plan.md`
  - 更新 Guardrails 中的 folder structure / tech stack
  - 更新 deployment/auth note：phase 1 使用本地帳密、多使用者 session auth、共享 queue

- [ ] DA-WS10-05 補 integrator smoke suite
  - 至少：
    - `uv run ruff format . --check`
    - `uv run ruff check .`
    - `uv run basedpyright`
    - targeted `uv run pytest tests/core/ tests/app/`
    - `uv run sc-app &` 啟動不 crash（5 秒後 kill）
    - `uv run huey_consumer worker.huey_app.huey &` 啟動不 crash（5 秒後 kill）

- [ ] DA-WS10-06 未受 cutover 影響的頁面驗證
  - 以下頁面不在 WS6-WS8 的改動範圍內，但共享 persistence 層，需確認不被 break：
    - `raw_data.py` (32KB) — Data Browser
    - `dashboard.py` (16KB) — 參數儀表板
    - `schemas.py` (9KB) — Schema 管理
    - `schema_editor.py` (13KB) — Schema 編輯器
    - `schemdraw_live_preview.py` (15KB) — 電路圖預覽
  - Verification：啟動 app 後確認每個頁面可正常載入、讀取資料

- [ ] DA-WS10-07 restart / recovery drill
  - 至少演練：
    - app 存活、worker 重啟
    - worker 存活、app 重啟
    - app 與 worker 同時重啟
  - 每種情境都要驗證：
    - stale/running/completed task 的呈現是否合理
    - UI 是否能重新讀到 persisted 狀態
    - 是否需要 manual reconcile command

Acceptance:
- 新架構不只可以寫，還可以被團隊穩定啟動、驗證、接手。
- 所有未改動的頁面功能不受影響。
- restart/recovery semantics 經過實測，而不是只存在文字假設。

---

## 7) 建議第一輪切法（最務實）

如果現在要立刻開工，建議只先做第一輪最小可切：

### Round 1

- Platform Agent
  - `DA-WS1-01`
  - `DA-WS1-02`
  - `DA-WS1-03`
  - `DA-WS1-04`
  - `DA-WS1-05`
  - `DA-WS1-06`
  - `DA-WS2-01`
  - `DA-WS2-02`
  - `DA-WS2-03`
  - `DA-WS2-07`
  - `DA-WS2-08`

- Simulation Agent
  - `DA-WS6-01`
  - 只做 authority mapping，不改 submit path

- Integrator
  - 對齊 WS1/WS2 contract 與 `/simulation` authority inventory

### Round 2

- Platform Agent
  - `DA-WS3-01`
  - `DA-WS3-02`
  - `DA-WS3-03`
  - `DA-WS3-05`
  - `DA-WS3-07`
  - `DA-WS3-08`

- Simulation Agent
  - `DA-WS4-01`
  - `DA-WS4-05`
  - `DA-WS4-06`
  - `DA-WS5-02`
  - `DA-WS5-04`
  - `DA-WS5-06`
  - `DA-WS5-05`
  - `DA-WS5-09`
  - `DA-WS6-02`

### Round 3

- Platform Agent
  - `DA-WS2-05`
  - `DA-WS2-06`
  - `DA-WS3-06`
  - `DA-WS5-07`
  - `DA-WS5-08`

- Simulation Agent
  - `DA-WS6-03`
  - `DA-WS6-04`
  - `DA-WS6-06`
  - `DA-WS7-01`
  - `DA-WS7-02`

- Characterization Agent
  - `DA-WS8-01`
  - `DA-WS8-02`
  - `DA-WS8-03`

這樣做的理由：
- 先把 persisted contract 與 worker path 站穩。
- 不先嘗試一次性重寫整個 simulation UI。

---

## 8) 每個 Task Card 的標準交付格式

每次完成一張卡，Contributor 必須回報：

```markdown
## Contributor Report v1

### 0) 任務資訊
- Agent:
- Task ID / Topic:
- Branch / Worktree:
- Scope (Allowed Files):
- 狀態:

### 1) Summary
- 目標:
- 結果:

### 2) Preflight 與邊界遵守
- 開工前 `git status --porcelain`:
- 是否遇到跨界需求:
- 跨界處理方式:

### 3) 變更內容
- Commit(s):
- Changed Files:

### 4) 文件更新（若有）
- <path>:

### 5) 測試結果
- Commands:
- Results:

### 6) API Touched Matrix
- Public APIs touched:
- Downstream callers checked:

### 7) Playwright / E2E（若任務要求）
- Scenarios:
- Evidence:
- 結果:

### 8) 已知風險與限制
- ...

### 9) 需要 Integrator 決策的事項
- ...

### 10) 回退資訊
- 建議回退 commit:
```

---

## 9) 本輪已知風險

1. `simulation/__init__.py` 體積過大（10832 行 / 283 items），任何直接切 submit path 都有高機率造成 side-effect。
2. `characterization/__init__.py` 同樣巨大（145KB），WS8 不可低估。
3. `TaskRecord` 與 `TraceBatchRecord` 的責任邊界若沒先定清楚，後面 API/worker/UI 會三次重做。
4. 目前 repo 有未提交變更：
   - `docs/docs_en/explanation/architecture/circuit-simulation/index.md`
   - `docs/docs_en/reference/ui/schema-editor.md`
   - `docs/docs_zhtw/explanation/architecture/circuit-simulation/index.md`
   - `docs/docs_zhtw/reference/ui/schema-editor.md`
   - `src/app/pages/simulation/__init__.py`
   - `src/app/pages/simulation/state.py`
   後續整合時要避免誤覆蓋。
5. 若 worker import path 處理不好，容易在 NiceGUI 啟動時提早初始化 Julia，直接違反新架構目標。
6. Zarr + SQLite 雙寫沒有 transaction 語意——中途 crash 可能造成 orphaned Zarr stores 或 incomplete batches。DA-WS2-05 必須先做。
7. Julia 冷啟動（5-15 秒）——worker consumer 必須長駐，不能 per-task spawn。
8. SQLite 在 NiceGUI process + Worker process 同時連線時的 WAL/locking 行為需要驗證——DA-WS2-04 覆蓋此風險。
9. 在 `DF-009` 尚未完全落地前，現有 module-level process-global caches 仍可能造成行為混淆；cutover 過程要避免同時依賴新舊路徑。
10. 若沒有 dedupe policy，UI double-click / browser retry / CLI retry 會產生 duplicate tasks，之後很難清理。
11. 若沒有 restart/reconcile drill，task system 很容易只在 happy path 可用。
12. 多使用者 auth 與 audit log 會擴大 schema / app/api scope；若 actor propagation 沒先做好，後面會再重構一次。

---

## 10) Integrator 決策清單（剩餘未決）
 
- [x] 核心架構決策已凍結；剩餘只允許 implementation-level 細節調整，不得推翻 `DF-001` ~ `DF-012`

---

## 11) 完整性自檢清單

完成所有 WS1-WS10 後，以下問題必須全部回答 Yes：

- [ ] `uv run sc-app` 啟動時不觸發 Julia 初始化？
- [ ] `uv run sc-worker` 啟動後可以消費任務？
- [ ] 在 simulation 頁面按 Run → task 被 dispatch 到 worker → 結果寫入 DB？
- [ ] Worker 跑 Julia 時 crash (kill -9) → NiceGUI 仍存活？
- [ ] 任務狀態可從 DB 查到且 UI 正確顯示 running/completed/failed？
- [ ] F5 重新整理後 → 能從 DB 恢復到最新任務的結果？
- [ ] 同一個 submit 連點兩次，不會建立語意未定義的 duplicate task？
- [ ] 已保存的 raw batch 可在沒有 live session 的情況下重新 post-process？
- [ ] CLI `uv run sc sim lc ...` 仍然能獨立執行（不需要 worker running）？
- [ ] app/worker 重啟後，stale/running/completed task 的呈現與 reconcile 行為可預期？
- [ ] 多位使用者可正常 login/logout，且 session 保護 UI pages 與 `/api/v1/*`？
- [ ] `admin` / `user` 角色行為符合預期，且 audit logs 可追查 actor？
- [ ] `raw_data.py`, `dashboard.py`, `schemas.py` 等未改動頁面功能正常？
- [ ] Zarr 部分寫入（crash 場景）不會造成後續讀取 crash？
- [ ] `ruff check`, `basedpyright`, `pytest` 全過？

---

## 12) Decision Freeze Log

用途：
- 把已定案的架構決策集中收斂，避免後續 Agent 只看 task 卡片時重新辯論已結論。

填寫規則：
- 每條包含：
  - `Decision ID`
  - `Date`
  - `Owner`
  - `Decision`
  - `Why`
  - `Affected Tasks`

已定案：
- `DF-001`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: `TaskRecord` 是 mandatory universal execution boundary；`TraceBatchRecord` / `AnalysisRunRecord` 只承擔 domain semantics
  - `Why`: queue lifecycle、heartbeat、timeout、retry、UI/CLI/API 一致性需要獨立於 domain record 的統一邊界
  - `Affected Tasks`: `DA-WS1-02`, `DA-WS2-*`, `DA-WS5-*`, `DA-WS6-*`, `DA-WS8-*`, `DA-WS9-*`
- `DF-002`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: Huey broker DB 與 application DB 分開；使用 `data/huey.db` 與 `data/database.db`
  - `Why`: 避免 Huey broker 的 WAL/lock 行為與 application read/write workload 混在一起
  - `Affected Tasks`: `DA-WS1-04`, `DA-WS3-*`, `DA-WS10-02`
- `DF-003`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: 採 soft dedupe + force rerun；Task 有 CRUD、Task List 即時更新、UI submit 短暫鎖定
  - `Why`: 防 accidental duplicate，同時保留顯式重跑能力，不把 UI/CLI/API 行為做成三套不同規則
  - `Affected Tasks`: `DA-WS1-05`, `DA-WS2-01`, `DA-WS2-02`, `DA-WS5-*`, `DA-WS6-02`, `DA-WS9-*`
- `DF-004`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: 採雙 lane 並行；`simulation lane` 與 `characterization lane` 可彼此並行，但各自 lane 內先序列化
  - `Why`: Characterization 也被視為 heavy-work capable workflow，需能與 Simulation 並行，但 phase 1 先避免 lane 內多工風險
  - `Affected Tasks`: `DA-WS3-07`, `DA-WS8-01`, `DA-WS10-03`
- `DF-005`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: 採 startup automatic reconcile（安全版）；app / worker 啟動時都執行自動 reconcile，但不得無條件盲刪
  - `Why`: 早期沒有重要資料，正適合把自動恢復機制練成熟；等正式資料進來才第一次做自動 reconcile 風險更高
  - `Affected Tasks`: `DA-WS1-06`, `DA-WS2-05`, `DA-WS2-06`, `DA-WS3-05`, `DA-WS3-06`, `DA-WS10-07`
- `DF-006`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: API 從第一天起視為 public contract；使用 `/api/v1/*`，phase 1 僅公開最小必要 endpoint
  - `Why`: 目標是降低未來再次重構 API 邊界的機率
  - `Affected Tasks`: `DA-WS5-05`, `DA-WS6-*`, `DA-WS8-*`, `DA-WS9-*`
- `DF-007`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: `Characterization` 視為 heavy-work capable workflow，canonical path 對齊 `TaskRecord + AnalysisRunRecord + worker-compatible execution`
  - `Why`: 未來可能承接機器學習與重度分析，不應保留 page-local synchronous authority 路線
  - `Affected Tasks`: `DA-WS8-*`, `DA-WS3-07`, `DA-WS10-03`
- `DF-008`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: CLI 預設採 `--wait`；`--detach` 作為 opt-in；`--wait` 模式需顯示 logs / progress
  - `Why`: 較符合研究工具 CLI 的直覺，同時保留背景化能力
  - `Affected Tasks`: `DA-WS9-05`, `DA-WS10-05`
- `DF-009`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: phase 1 全部移除現有 module-level process-global caches
  - `Why`: 直接消滅 authority 混淆，優先保證 persisted orchestration 正確性，效能優化之後再重設計
  - `Affected Tasks`: `DA-WS6-04`, `DA-WS6-05`, `DA-WS10-06`
- `DF-010`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: phase 1 直接支援 multi-user local auth；採本地帳密 + session cookie；角色僅 `admin` / `user`
  - `Why`: 系統是一個應用多個使用者一起使用，Tasks 共用 Queue；需要登入、登出與 audit logs，但不需要複雜 ACL
  - `Affected Tasks`: `DA-WS2-07`, `DA-WS2-08`, `DA-WS4-06`, `DA-WS5-04`, `DA-WS5-06`, `DA-WS5-07`, `DA-WS5-08`, `DA-WS10-02`, `DA-WS10-03`, `DA-WS10-04`
- `DF-011`
  - `Date`: `2026-03-09`
  - `Owner`: `Codex`
  - `Decision`: `/api/v1` 採 completeness-first inventory；完整 API surface 先列完，再標 phase 1 required / planned later
  - `Why`: Phase 1 不一定全做，但完整規劃必須先存在，否則容易因漏想而再重構
  - `Affected Tasks`: `DA-WS5-02`, `DA-WS5-03`, `DA-WS5-05`, `DA-WS5-06`, `DA-WS5-07`, `DA-WS5-08`, `DA-WS5-09`
- `DF-012`
  - `Date`: `2026-03-09`
  - `Owner`: `User + Codex`
  - `Decision`: 雙 lane 採兩個完全獨立的 worker consumer stack；`simulation_huey` 與 `characterization_huey` 各自對應一個 queue 與一個 consumer process
  - `Why`: lane 邊界最乾淨、debug 最容易、後續最不易因 worker topology 再重構
  - `Affected Tasks`: `DA-WS3-07`, `DA-WS3-08`, `DA-WS10-01`, `DA-WS10-05`

---

## 13) 下一位 Agent 的第一個建議動作

若你是下一位接手的 Agent，直接做：

1. 先讀 `Decision Freeze Log`
2. 直接依 `DF-001` 到 `DF-010` 中已定案部分實作，不再重新討論
3. 先從 `DA-WS2-01` / `DA-WS2-02` / `DA-WS2-03` 開始進入實作
4. 接著處理 `DA-WS3-07` 與 lane routing 具體落地

如果跳過這一步，後面高機率重工。
