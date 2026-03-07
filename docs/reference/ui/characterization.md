---
aliases:
- Characterization UI
- 特徵分析介面
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /characterization 的 Design Scope、Run Analysis、Trace Selection 與 Result View 契約
version: v0.10.0
last_updated: 2026-03-08
updated_by: codex
---

# Characterization

本頁定義 `/characterization` 的正式 UI 契約。

## Core Data Model

`/characterization` 必須以以下產品語意作為主體：

- `Design`：使用者操作的 root container
- `Trace`：統一分析與選取單位
- `Trace Batch`：run / import / analysis 的 provenance boundary
- `ResultArtifact`：Result View 的統一可顯示單元（view contract）

!!! note "Phase-2 internal compatibility"
    目前實作仍透過 `DatasetRecord` / `DataRecord` / `ResultBundleRecord` 相容層落地，
    但 UI 主語言與查詢語意必須維持 `Design / Trace / Trace Batch`。

## Result Artifact Contract

每次 analysis run 完成後，Result View 不直接綁 `DerivedParameter` 命名細節，
而是先整理成 artifact manifest。

`ResultArtifact` 最小欄位：

- `artifact_id`：唯一鍵（例如 `admittance.mode_vs_ljun`）
- `analysis_id`：來源 analysis（例如 `admittance_extraction`）
- `category`：分類（例如 `resonance`, `fit`, `summary`, `qa`）
- `view_kind`：`matrix_table`, `series_plot`, `scalar_cards`, `record_table` 等
- `title` / `subtitle`
- `query_spec`：延遲查詢規格（分頁、排序、過濾、資料來源）
- `meta`：單位、軸標籤、row/col 規模、是否 sweep

!!! important "UI 邊界"
    UI 只依賴 artifact contract，不應直接推論 `DerivedParameter.name` 字串格式。

## Page Sections

1. `Design Scope`
2. `Run Analysis`
3. `Result View`

## Client Lifecycle Contract

`/characterization` 的 refresh 行為必須受 owner client lifecycle 保護。

!!! important "斷線後不可持續 rerender"
    若使用者 reload 頁面、切離 `/characterization`，或在 `reconnect_timeout` 內未重新連回，
    stale / deleted client 上不得再執行 shell refresh 或 analysis-related 局部 refresh。

!!! note "Analysis 可繼續，舊頁面不可再收 UI 更新"
    server-side characterization run 可以完成並保存結果，
    但舊 client 一旦 disconnected 或 deleted，任何 background UI refresh path 都必須停止命中該頁面的 refreshable target。

## Design Scope Contract

!!! note "Current behavior（2026-03-04）"
    舊版 UI 曾提供 `Trace Batch`（internal: `Result Bundle`）下拉，
    允許使用者直接切換 Characterization scope。

!!! important "Contract（Design-centric）"
    使用者應只對 `Design` 操作。`Design Scope` 不再暴露「選 trace batch 再分析」入口。
    Run Analysis 的 trace 候選來源預設為 design-level trace index，並採 trace-first 相容性判定。

!!! important "Phase-3 cross-source contract"
    若同一個 `Design` 內同時存在來自 `circuit` / `layout` / `measurement` 的相容 traces，
    `/characterization` 必須把它們視為同一個 design scope 下的可選 trace pool，
    不得因 `source_kind` 不同而切成不同分析模型或不同 run surface。
    UI 應呈現 source coverage / provenance summary，但不得退回 source-specific picker。

!!! note "Internal provenance"
    系統仍可在內部維持 `input_bundle_id` 等 provenance；但 UI 不應要求使用者理解或操作 trace batch 細節。

## Design Profile Contract

design profile 是 Characterization 的 summary/recommendation 資料來源：

- 儲存位置：phase-2 相容層目前仍是 `DatasetRecord.source_meta.dataset_profile`
- schema（versioned）：
  - `schema_version`：目前 `1.0`
  - `device_type`：`unspecified` / `single_junction` / `squid` / `traveling_wave` / `resonator` / `other`
  - `capabilities`：字串陣列（canonical capability keys）
  - `source`：`inferred` / `template` / `manual_override`

!!! note "Current implementation（2026-03-04）"
    UI 目前仍展示 profile 推導出的推薦狀態與提示文字，
    並保留 `required_capabilities` / `excluded_capabilities` 作為建議訊息來源。

!!! important "Contract（Trace-first authority）"
    是否可執行 analysis 必須由 trace compatibility 決定，且 run 時必須提供 selected trace ids。
    `dataset_profile.capabilities` 不可作為唯一 hard-block 條件。

!!! warning "backward compatibility"
    舊 design 若沒有 `dataset_profile`，系統必須自動 fallback 到 `inferred` profile，
    由現有 trace metadata 推導最低必要 capabilities，避免既有流程突然全部變成不可用。

## Run Analysis Contract

`Run Analysis` 採集中式執行模型：

- 單一 analysis selector
- 依 analysis 顯示對應 config fields
- 單一 `Run Selected Analysis` 按鈕
- 同一區塊顯示執行 log/status

!!! note "Current behavior（2026-03-04）"
    可用性資訊可能以多種形式重複呈現（主文字 + status 行 + 總表）。

!!! important "Contract（Single availability render）"
    可用性只允許一個主要呈現元件（例如 chip/label + reason line），
    由單一 `availability state` 驅動：`state` + `reason` + `severity`。
    除錯資訊可保留，但不得把同一資訊重複顯示多次。

## Analysis Gating Contract（by capabilities）

analysis registry 必須可宣告：

- `required_capabilities`
- `excluded_capabilities`
- `recommended_for`（device_type 清單）

Run Analysis UI 必須顯示每個 analysis 的狀態（trace-first）：

- `Recommended`：有 compatible traces，且 profile/recommended_for 提示命中
- `Available`：有 compatible traces，但無推薦提示或僅有 profile 警示
- `Unavailable`：compatible traces = 0（僅此 hard block）

Reason 必須可機器組合，最少包含：

- `No compatible traces in current design scope`
- `Select at least one trace to run.`

可選的 profile 提示（不阻擋 run）：

- `Profile hint: missing capability <capability_key>`
- `Profile hint: excluded capability <capability_key>`

!!! note "單頁動態呈現"
    Characterization 不拆多頁；同一頁面需同時呈現 analysis 列表狀態、reason 與 run 互動。

!!! warning "去重要求"
    若保留分析總表，其內容不可與主要 availability 狀態重複。
    主顯示為唯一 source of truth。

## Trace Selection Contract

每次 run 前必須可明確指定要分析哪些 traces。

### Minimum Requirements

- 使用 `ui.table`（可 row click 選取）
- 支援分頁（pagination）
- 支援排序（sorting）
- 支援欄位過濾（filtering）

### Trace Mode Semantics

- `Base`：基頻 / signal trace（含無 sideband tuple 的參數命名）
- `Sideband`：含非零 mode tuple（例如 `[...] [om=(...), im=(...)]`）的 trace
- 預設選取策略必須優先 `Base`，不得預設全選所有 sideband traces

!!! note "Signal 與 Base"
    在 Characterization 的 trace 過濾語意中，`Signal` 歸入 `Base`。

### Interaction Performance Requirements

- row click 切換選取時，不可觸發整個頁面重載
- Trace Selection 區塊需局部刷新（table + selection counters + run state）
- Scope / Analysis 切換才可觸發整體資料重算
- Compatibility metadata 應按 scope 快取，避免重複全量掃描

!!! important "Sideband 風險控制"
    大型多 pump / sideband 資料集不應預設全選。
    UI 應提供「Base traces 優先」的快速選擇方式，避免一次送入大量 sideband traces 導致分析結果失真或無意義膨脹。

### Data Boundary

- Trace table 僅載入 metadata（`id`, `data_type`, `parameter`, `representation`）
- Trace table / scope summary 可附帶 source / provenance metadata（例如 `source_kind`, `stage_kind`, `bundle_id`），
  但那些欄位只用於呈現與 lineage，不可成為分析模型分叉條件
- run 時只傳 selected trace ids 給 analysis service
- compatibility 判定只能使用 metadata index（不得讀取 payload）
- `data_type` alias 必須一致正規化（例如：`y_params` ↔ `y_parameters`、`s_params` ↔ `s_parameters`）

## Parameter Sweep Support Boundary（Current vs Target）

!!! note "Current behavior（2026-03-07）"
    `/characterization` 目前仍是 trace-first、design-centric。
    它處理的是「可選取的 traces」，不是直接把 raw/post-processed sweep trace batch 當 primary input object。

目前支援邊界如下：

- `Supported`：
  `admittance_zero_crossing`、`squid_fitting`、`y11_fit` 這類已定義的 analysis，
  在 sweep design 已 materialize 成可相容 traces、且使用者明確選到那些 traces 時，可以照既有 trace-first 契約執行。
- `Partial support`：
  這些 analysis 可以跑在 sweep-origin traces 上，但目前沒有正式 sweep-native UI 契約來保證：
  軸切片 selector、N-D sweep summary artifact、或直接從 canonical trace batch payload 做跨點瀏覽。
- `Blocked`：
  直接把 `ResultBundleRecord(bundle_type=circuit_simulation|simulation_postprocess, run_kind=parameter_sweep)` 當 `/characterization` 的主要輸入物件、
  或要求 analysis 直接遍歷完整 canonical sweep payload，而不經 trace selection，現在都不在契約內。

!!! important "Target contract"
    之後若擴充 Characterization 對 sweep 的支援，仍必須保留：
    - trace-first authority 是 run gate
    - `dataset_profile` 只是 hint，不是 hard gate
    - raw/post-processed sweep trace batch 可作 provenance 與 reconstruction source，但不能取代 selected trace ids

!!! warning "代表點不是 analysis authority"
    若 sweep design 只有 representative-point projection，而沒有對應 selected traces 或 sweep-aware contract，
    `/characterization` 不得宣稱自己支援「完整 sweep analysis」。

## Result View Contract

`Result View` 採單一統一結果檢視，且支援可擴充分類：

- 第一層：`Category Selector`
- 第二層：`Tabs`（該 category 內的 artifacts）
- 共用結果檢視區（由 `view_kind` 驅動）

### Run Success Navigation Contract

當 `Run Selected Analysis` 成功完成後，Result View 必須立即同步到本次執行的 analysis：

- 自動切到剛執行完成的 `analysis_id`
- 若該 analysis 有 artifacts，直接選到第一個可用 artifact
- 若該 analysis 無 artifacts，停留在該 analysis 並顯示可診斷 empty-state

!!! important "禁止停留在舊 analysis"
    run 成功後不可沿用先前的 Result View analysis/category/artifact 選擇，
    否則會讓使用者誤以為新 analysis 沒有產生結果。

!!! note "SQUID Fitting 顯示要求"
    `SQUID Fitting` 完成後，Result View 應優先落在 `fit` category，
    並顯示 `Fit Parameters` tab（若有資料）。
    不可讓畫面仍停在舊的 `Admittance Extraction / Mode vs L_jun` 視圖。

### Trace Mode Filter (Result View)

- Result View 必須提供 `Trace Mode Filter`
- 允許選項僅限：`All`, `Base`, `Sideband`（`Signal` 若出現在來源語意，必須歸併至 `Base`）
- 不可暴露 `Unknown` 作為選項或顯示文字
- artifact manifest 與 payload query 必須吃同一個 mode filter
- 切換 mode filter 時，只可刷新當前 artifact payload，不可重跑 analysis

!!! important "分類契約（禁止 Unknown）"
    Trace mode 分類必須是封閉集合：
    - `Base`：base/signal traces（含無 sideband tuple 的參數命名）
    - `Sideband`：含非零 mode tuple 的 sideband traces
    - `All`：`Base + Sideband` 聯集
    不符合規則的資料來源必須在資料層被正規化/忽略，不得在 UI 形成 `Unknown` 分類。

### Result View Controls Layout Contract

- Result View controls 必須包含 `Trace Mode Filter` 與 `Category Selector`
- 桌面版（`lg` 以上）兩者必須同列呈現
- 行動版可換行，但仍屬同一 controls row（同一操作區塊）
- 不可用任意 margin hack；需沿用既有 spacing token（`gap-*`, `p-*`, `mb-*`）

!!! note "狀態一致性"
    `Available for current design scope` 文案、可選 trace 集合、analysis run enable/disable 狀態，必須以同一份 mode-filtered compatibility 結果驅動，禁止分叉判定。

## Fitting Analyses UI Contract

### SQUID Fitting

- Run Analysis 必須提供可操作輸入欄位（至少涵蓋 model / bounds / fit window）
- 執行流程：`Run Selected Analysis` 觸發後，需回寫 status/log（開始、成功、失敗）
- Result View 必須可顯示 `SQUID Fitting` 結果，並以 artifact manifest 組織於 `fit` category

輸入契約（最小）：
- `fit_model`: `NO_LS` / `WITH_LS` / `FIXED_C`
- `fit_min_nh`, `fit_max_nh`
- `ls_min_nh`, `ls_max_nh`, `c_min_pf`, `c_max_pf`
- `fixed_c_pf`（僅 `FIXED_C` 必要）

輸出契約（最小）：
- 每個 mode 的擬合參數（例如 `Ls_nH`, `C_eff_pF`）與 quality metric（例如 `RMSE`）
- 至少一個可檢視 artifact（`record_table` 或 `scalar_cards`）

### Y11 Response Fit

- Run Analysis 必須提供可操作輸入欄位（至少涵蓋初始值與上界）
- 執行流程同樣需寫入 status/log 並可失敗回報
- Result View 必須可顯示 `Y11 Response Fit` 結果，並以 artifact manifest 組織於 `fit` category

輸入契約（最小）：
- `ls1_init_nh`, `ls2_init_nh`, `c_init_pf`
- `c_max_pf`

輸出契約（最小）：
- 擬合參數（`Ls1_nH`, `Ls2_nH`, `C_pF`）與 `RMSE`
- 至少一個可檢視 artifact（建議 `scalar_cards`）

### S21 Resonance Fit（2D Sweep）

- 單軸 2D `S21` sweep 的正式語意為：`Freq x L_jun`
- 單軸 2D `Freq x L_jun` sweep 應逐 bias slice 執行 fitting，並保留每個 slice 的 `L_jun`
- Result View 應能用既有 artifact contract 呈現：
  - `fit` category 下的 `Mode vs L_jun`
  - `Resonator Summary`
  - `Fit Parameters`

輸入/執行邊界：

- `sweep-ready`：2D `S21`，且第二軸為 `L_jun`
- `partial`：2D 單軸 sweep，但第二軸不是 `L_jun`；允許 per-slice fit，但不承諾 canonical `Mode vs L_jun` artifact
- `blocked`：>2D / multi-axis sweep

Persistence 最小契約：

- persisted method：沿用既有 `complex_notch_fit_S21` / `transmission_fit_S21` / `vector_fit_S21`
- 若為 2D `Freq x L_jun` sweep：
  - 每個 bias slice 的 mode / Q 參數仍以既有 `_b<idx>` suffix 寫入
  - 必須同時寫入對應 `L_jun_b<idx>`
  - `extra` 應保留 sweep provenance（至少 `sweep_axis`, `sweep_value`, `sweep_index`）

!!! important "S21 sweep 可視化契約"
    只要存在 `mode_*_ghz_b*` 與對應 `L_jun_b*`，Result View 就必須能重建 `Mode vs L_jun` artifact；
    不得再把 2D `Freq x L_jun` S21 sweep 僅視為看不到 sweep artifact 的 partial support。

### Run → Persistence → Artifact Mapping（SQUID / Y11）

下表為 Result View 可見性的正式資料契約（必須成立）：

- `squid_fitting`：
  - run 入口：`CharacterizationFittingService.run_squid_fitting()`
  - persisted method：`lc_squid_fit`
  - 最小 derived params：`Ls_nH`, `C_eff_pF`（`extra` 含 `mode`, `rmse`, `trace_mode_group`）
  - Result View：`fit` category，至少含 `fit_parameters` artifact
- `y11_fit`：
  - run 入口：`CharacterizationFittingService.run_y11_fitting()`
  - persisted method：`y11_fit`
  - 最小 derived params：`Ls1_nH`, `Ls2_nH`, `C_pF`, `RMSE`（`extra.trace_mode_group` 必填）
  - Result View：`fit` category，至少含 `fit_parameters` artifact

!!! important "method 對齊規則"
    `analysis_registry.completed_methods` 與 persistence `DerivedParameter.method` 必須字串完全一致（例如 `squid_fitting -> lc_squid_fit`）。
    任一字串不一致都會導致 Result View analysis tab/artifact 不可見。

### Empty Artifact 異常顯示契約

當「資料存在但 artifact 為空」時，UI 必須顯示可診斷訊息：

- 若目前分析/trace mode 下存在 persisted method groups，但 artifact builder 回傳空集合：
  - 顯示「Persisted results found but no renderable artifacts...」等級訊息
  - 訊息需包含 method key（供除錯）
- 若是 trace mode 過濾後為空：
  - 顯示目前 trace mode 下無 artifact（不得觸發 rerun）

!!! tip "Result View 承載方式"
    `squid_fitting` 與 `y11_fit` 均屬 `fit` category。
    category 下透過 tabs 分隔各 artifact；切換 tabs/filter 只刷新 payload，不可重跑 solver。

!!! note "擴充規則"
    新增 analysis 類型（A...K）時，只新增/調整 registry 與 artifact 映射。
    不應改動核心 renderer 主流程。

!!! note "與 /simulation 的重疊"
    `/simulation` 的 quick-inspect result view 可保留。
    `/characterization` 負責正式分析 run 與 provenance 管理。

## Availability Contract

analysis 可用性必須以「當前 design scope 的 compatible traces」為準。

!!! warning "compatible traces = 0"
    Availability 必須顯示 `Unavailable for current design scope`，且 `Run Selected Analysis` 必須 disabled。
    此狀態下不可執行 run（即使使用者嘗試觸發，也必須被 guard 阻擋）。

!!! important "compatible traces > 0 但 selected traces = 0"
    Availability 可顯示 `Available for current design scope`（或明確標示尚未選取）。
    但 Run 按鈕仍必須 disabled，直到至少選取 1 條 trace。
    UI 必須顯示明確提示：`Select at least one trace to run.`。

!!! tip "compatible traces > 0 且 selected traces > 0"
    Availability 應顯示 `Available for current design scope`，且 Run 按鈕應可啟用。

!!! note "禁止雙重判定分歧"
    Availability 文案、Run 按鈕狀態、實際執行前檢查必須共用同一 compatibility evaluator。

## Performance SLO (Result View)

- 首屏只載入 artifact manifest（不載完整 payload）
- 切換 category/tab 才載入對應 artifact payload
- `ui.table` 一律 server-side pagination/sort/filter
- 大型資料（含 sideband）不可一次性讀全量至前端

## Provenance Contract

每次 run 完成後，必須建立新的 `Trace Batch`：

- phase-2 相容層目前仍落在 `ResultBundleRecord(bundle_type=characterization, role=analysis_run)`
- `config_snapshot` 應包含本次 analysis config 與 selected trace ids
- `summary_payload` 應至少保留：
  - `selected_trace_count`
  - `selected_trace_mode_group`
  - selected trace 的 source summary（例如 circuit/layout/measurement 各自用了多少 compatible traces）
  - 若可得，對應 provenance batch ids / stage kinds

!!! important "analysis-run boundary 不可退回 generic batch semantics"
    Characterization history / provenance 必須以 `AnalysisRunRecord` 語意呈現，
    至少能區分：
    - 哪次 analysis run
    - 用了哪些 selected traces
    - input scope 是 design-level trace scope
    - 來源組成與 provenance 是什麼
    不可只剩下模糊的 batch label 或 generic bundle list。

若輸入 traces 來自 sweep design，`config_snapshot` 還應保留足以回推 sweep slice 的資訊
（例如選到的 trace ids、trace mode group，以及 trace 自身攜帶的 sweep axes metadata）。

## Phase-3 Cross-Source Reuse Expectations

- `layout` saved traces -> characterize：必須視為正式 trace-first reuse path
- `measurement` saved traces -> characterize：必須視為正式 trace-first reuse path
- `circuit` saved traces -> characterize：必須視為正式 trace-first reuse path
- 同一個 `Design` 若同時存在上述來源：
  - availability 仍只由 compatible traces 決定
  - UI 應清楚標示 source coverage / provenance
  - run history 應保留這次 run 實際用了哪些來源

## Admittance Output Replacement Rule

`admittance_zero_crossing` 每次執行時，必須先清掉同 design 舊的同 method 輸出，再寫入新結果，避免舊 sideband / 舊 sweep 殘留造成 mode rows 無限膨脹。

## Runtime Contract Snapshot

### Input

- active `Design`（phase-2 相容層目前仍由 `DatasetRecord` 承載）
- trace metadata index（scope-filtered）
- analysis config + selected trace ids

### Output

- 新的 analysis `Trace Batch`（phase-2 相容層目前仍落在 `ResultBundleRecord`）
- 對應 `DerivedParameter` / artifact payload（依 analysis type）
- 可追蹤 status log（start / heartbeat / success / failure）

### Invariants

1. trace-first authority：`compatible traces + selected trace ids` 是唯一 run gate
2. design profile（phase-2 相容層目前仍是 `dataset_profile`）僅提供 hint/recommendation，不可 hard-block
3. Result View 只讀 artifact contract，不直接依賴派生參數命名字串

### Failure Modes

- `compatible traces = 0` -> `Unavailable for current design scope`
- `selected trace ids = 0` -> Run disabled + `Select at least one trace to run.`
- persistence method 與 registry `completed_methods` 不一致 -> 結果 tab/artifact 不可見

## Code Reference Map

- Page orchestration:
  - [`characterization/__init__.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/characterization/__init__.py)
- Runtime state:
  - [`characterization/state.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/characterization/state.py)
- Trace-scope query service:
  - [`characterization_trace_scope.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/services/characterization_trace_scope.py)
- Analysis metadata/hints:
  - [`analysis_registry.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/services/analysis_registry.py)
  - [`analysis_capability_evaluator.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/services/analysis_capability_evaluator.py)

## Runtime Parity Checklist

release 前至少確認：

1. availability label / run enable / pre-run guard 共用同一 evaluator
2. trace mode filter（All/Base/Sideband）在 Run Analysis 與 Result View 語義一致
3. analysis trace batch 的 `config_snapshot` 含 selected trace ids + mode group
4. artifact manifest 與 payload query 由同一 trace scope 過濾結果驅動
