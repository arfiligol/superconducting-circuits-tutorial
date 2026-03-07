---
aliases:
- Circuit Simulation UI
- 電路模擬介面
tags:
- diataxis/reference
- audience/team
- sot/true
- topic/ui
status: draft
owner: docs-team
audience: team
scope: /simulation 頁面的 Expanded Netlist、Simulation Setup、Load-or-Run 與 Result 檢視契約
version: v0.14.0
last_updated: 2026-03-07
updated_by: codex
---

# Circuit Simulation

本頁描述 `/simulation` 的正式 UI 契約。

## Page Sections

1. `Active Circuit`
2. `Netlist Configuration`
3. `Simulation Setup`
4. `Logs`
5. `Simulation Results`
6. `Post Processing`
7. `Post Processing Results`

## Client Lifecycle Contract

`/simulation` 的 UI refresh 必須綁定目前仍存活的 NiceGUI client。

!!! important "禁止 stale client rerender"
    當使用者在模擬進行中發生 page reload、navigate away，或超過 `reconnect_timeout` 後斷線刪除 client，
    shell-level 與 page-level refresh path 都不得再對舊 client 建立新 element。

!!! note "Background work 可持續，UI refresh 不可誤送"
    server-side simulation / post-processing 可以依既有流程繼續執行或完成，
    但任何之後的 UI rerender 都必須先確認 refresh target 的 owner client 仍然 connected；
    若 owner client 已 stale / deleted，該 refresh 必須直接停止。

## Result View 互動契約（Raw vs Post-Processed）

`Simulation Results` 與 `Post Processing Results` 必須是兩個獨立區塊，但互動能力要對齊。

| 區塊 | 資料來源 | 必須具備的共通互動 | 區塊差異 |
|---|---|---|---|
| `Simulation Results` | 最近一次成功 `Run Simulation` 的 raw result bundle | `family tabs`、`metric selector`、`Add Trace`、trace cards、單一 shared plot | 保留 Raw 結果語義與 `Save Raw Simulation Results` |
| `Post Processing Results` | 最近一次成功 `Run Post Processing` 的 output node | `family tabs`、`metric selector`、`Add Trace`、trace cards、單一 shared plot | 資料來源為 pipeline output；保存動作為 `Save Post-Processed Results` |

!!! important "區塊分離，不可合併"
    `Raw Simulation Results` 與 `Post Processing Results` 必須維持分開渲染與分開狀態管理，
    不可收斂成單一 result 卡片。

!!! note "Result View 互動不重跑"
    在 Result View 內切換 family/metric、增減 trace card、調整 trace selector，
    僅更新同一張 shared plot，不得觸發 solver 或 post-processing rerun。

### Result View 標題與軸標同步契約

任何 `family` / `metric` / `trace` 切換後，圖表必須同步更新：

- `figure title`
- `y-axis title`（含單位）

!!! important "禁止 stale label"
    不得出現沿用上一個 family/metric 的軸標題。
    至少需滿足 `Y -> Z -> Y` 循環切換後，y-axis 標示可正確回復。

`Impedance (Z)` / `Admittance (Y)` 最低要求：

- `Z + Real/Imaginary/Magnitude` -> `Real (Ohm)` / `Imaginary (Ohm)` / `Magnitude (Ohm)`
- `Y + Real/Imaginary/Magnitude` -> `Real (S)` / `Imaginary (S)` / `Magnitude (S)`

### Raw Simulation Results Family 語義（固定）

- `S`：永遠顯示 solver-native raw `S`，不可套用 Port Termination Compensation（PTC）
- `Y`：必須提供 `Raw Y` / `PTC Y` 切換
- `Z`：必須提供 `Raw Z` / `PTC Z` 切換

!!! important "PTC 作用域（Raw View）"
    在 `Simulation Results` 中，PTC 只允許作用於 `Y/Z` 路徑。
    `S` 必須維持 raw 語義，避免與 solver 原生輸出混淆。

!!! note "Y-domain first"
    PTC 定義為 `Y_clean = Y_raw - diag(1/R_i)`。
    `PTC Z` 需由補償後 `Y` 導出；不得直接在 `S` 上施作補償。

### Post-Processed 命名一致性契約

!!! note "Current behavior（2026-03-04）"
    某些視圖可能回退到 index-only 命名（例如 `Z11`），與 Trace Card 選單文案不一致。

!!! important "Contract"
    `Post-Processed Result View` 的 title / legend / trace label（含 hover 中可見名稱）必須與
    Trace Card `Output Port` / `Input Port` 一致。命名格式：
    `<MatrixSymbol>_<OutputPortLabel>_<InputPortLabel>`。

!!! warning "禁止退回 index-only"
    在 basis 轉換場景（例如 `dm(1,2)`、`cm(1,2)`）不得顯示 `Z11`、`Y21`、`S12` 這類僅 index 命名。
    僅當 output/input 全為原始數字 port 且未經 basis 轉換時，才可接受 index-only 變體。

## Netlist Configuration

!!! note "Live Preview"
    Schemdraw Live Preview 仍維持停用，不在本頁恢復。

`Netlist Configuration` 必須顯示真正送入模擬器的 Expanded Form：

- expanded `components`
- expanded `topology`
- expanded `parameters`（若 schema 有使用）

!!! important "單一 expansion pipeline"
    `/simulation` 的 `Netlist Configuration` 與 `/schemas/{id}` 的 `Expanded Netlist Preview`
    必須共用同一條 parse/validate/expand pipeline。

### 顯示與儲存邊界

- DB 只存 source-form `Circuit Definition`
- 本卡片顯示唯讀 Expanded Form
- solver 執行內容必須與本卡片一致

## Simulation Setup

!!! important "Boundary"
    Source Port、Source Mode、pump frequency、harmonics、hbsolve 選項屬於 Simulation Setup，
    不屬於 Circuit Netlist 語法。

### 三層卡片結構契約

`Simulation Setup` 必須採用三層結構：

1. 第一層：`Simulation Setup` 主卡片
2. 第二層：固定區塊（順序不可更動）
   - `Signal Frequency Sweep Range`
   - `Parameter Sweeps`
   - `HB Solve Setting`
   - `Sources`
   - `Port Termination Compensation`
   - `Advanced hbsolve Options`
3. 第三層：可增減子卡
   - `Parameter Sweeps` 下可 `Add Axis` / `Remove Axis`
   - `Sources` 下可 `Add Source` / `Remove Source`

### Setup Persistence Contract（Dialog-based Manager）

`Simulation Setup` 必須保留既有 `Saved Setup` 下拉，並新增 `Manage Setups` 入口（Dialog）。

`Manage Setups` Dialog 最少要支援：

1. `Add New`（以目前表單建立新 setup）
2. `Rename`（重新命名既有 setup）
3. `Delete`（刪除既有 setup）
4. `Load`（載入選取 setup 到表單）
5. `Save As`（將目前表單另存為新名稱）

!!! important "可見回饋"
    所有 CRUD 動作都必須給使用者可見通知（success/failure）。

!!! warning "相容性邊界"
    `Saved Setup` 下拉的既有載入行為必須維持不變；
    `Manage Setups` 只是擴充入口，不可改變原有 schema+setup 契約與求解流程。

### Parameter Sweep（Multi-Axis MVP）

Sweep 軸 target 來源至少需同時涵蓋：

- expanded netlist 的 `components[*].value_ref`（去重後）
- Simulation Setup 已配置 source 的 bias/pump 相關連續參數（例如 `sources[1].current_amp`、`sources[1].pump_freq_ghz`）

!!! note "Target key namespace"
    Sweep target key 允許混合 netlist 與 source namespace。
    建議格式：
    - netlist：`<value_ref>`（例如 `Lj`）
    - source：`sources[<1-based index>].<field>`（例如 `sources[1].current_amp`）

- 只有有 `value_ref` 的 component 可被 netlist sweep 選取；`default`-only component 不可作為 netlist sweep target
- 支援多軸（Multi-Axis）
- 執行模式先支援 `cartesian`（可保留 `paired` 欄位但可不實作）
- `Sweep disabled` 時，`Run Simulation` 必須與既有 single-run 路徑完全一致

Sweep Setup 最小欄位：

- `enabled: bool`
- `mode: "cartesian"`（預設）
- `axes[]`
  - `target_value_ref: str`（target key，可為 value_ref 或 source target）
  - `start / stop / points`
  - `unit`（可由 parameter spec 或 source 欄位語義提示）

!!! note "舊 payload 相容"
    仍需可讀舊單軸 payload（例如 `axis_1` 或單一 axis 寫法）並 normalize 成 `axes[]`。

### Sweep Cache / Provenance 契約

當 sweep 啟用時：

1. normalized simulation setup 必須包含 `sweep` 區塊
2. 必須從該 `sweep` 區塊計算 `sweep_setup_hash`
3. result cache identity 仍走 `schema_source_hash + simulation_setup_hash`，其中 `simulation_setup_hash` 已含 sweep 設定
4. `source_meta` 與 `config_snapshot` 必須保存 `sweep_setup_hash` 與 sweep 軸摘要（含 target key）

### Sweep Logs 契約

`Logs` 必須額外可追蹤：

- sweep 維度（N 軸）
- 總點數
- 每個 sweep 點的進度（例如 `point 3/11`）

### Sweep 結果結構契約（供後續 pipeline/analysis）

sweep run 成功後，bundle `result_payload` 需包含：

- `run_kind = "parameter_sweep"`
- `sweep_axes` metadata（target、unit、values、point_count）
- `sweep_mode`（目前至少 `cartesian`）
- `points[]`（每點至少含 `axis_indices`、`axis_values`、該點 simulation result）
- `representative_point_index`（供 Result View quick-inspect）

匯出為 `DataRecord` 時，應在 `axes` 中明確附帶 sweep 軸 metadata，避免與 single-run traces 混淆。

!!! important "Current vs Target（2026-03-07）"
    - `Current`: raw parameter sweep 的 canonical source of truth 已是 `circuit_simulation` bundle 的完整 `result_payload`。
    - `Target`: `representative_point_index` 只能作 quick-inspect projection，不可把代表點 trace 或 UI materialized view 當成唯一 SoT。

### Sweep Result View 契約（Simulation Results 區內）

當最近一次成功 run 為 `run_kind=parameter_sweep` 時，`Simulation Results` 必須額外顯示 `Sweep Result View`：

- 區塊抬頭需顯示：
  - sweep 維度（N）
  - 總點數
  - 目前 compare axis 與固定切片摘要
- `Selectors`（最少）：
  - `family`
  - `metric`
  - `compare axis`（選擇哪一條 sweep 軸用來展開多條 trace）
  - `fixed axis selectors`（其餘 N-1 軸固定 index/value）
  - `Add Trace` + 多個 trace card
  - 每個 trace card 必須能選 `sweep value`
  - `Output Port` / `Input Port`
  - `Output Mode` / `Input Mode`
- `Outputs`（最少）：
  - `單一 shared plot`：`X = Frequency`、`Y = selected metric`
  - `多條 traces`：每條 trace 代表同一 compare axis 上不同的 sweep value
  - 若 sweep 維度 > 1，必須允許固定其餘軸後比較目前 compare axis 的多條頻率響應

!!! important "trace-first"
    Sweep 視圖的 selector 必須沿用現有 trace-first 設計。
    不可硬編碼成單一 trace（例如只支援 `S11`）。

!!! important "Simulation focus"
    `Sweep Result View` 應優先呈現基礎 `S / Y / Z / QE / CM` 對 Frequency 的響應比較。
    `metric vs parameter`、`mode vs L_jun` 之類較偏分析性的圖，不應成為
    `Simulation Results` 的主要視覺路徑。

!!! note "保存一致性"
    `Save Raw Simulation Results` 對 sweep run 必須保存完整 sweep payload 與 provenance
    （含 `sweep_setup_hash` 與 `sweep_axes`），確保可回放。

### Sweep Result View 失敗模式（最低要求）

- 無 sweep payload：顯示 empty state，不得崩潰
- selector 與當前 payload 不相容：自動回退到可用預設值，並保留 warning log
- 單點結果缺資料（缺某 trace 或某 representation）：該點顯示 `NaN`/`N/A`，整體視圖仍可用
- Cartesian 點數超門檻：顯示明確 warning，並阻止 `Run Simulation`
- 無效 target（schema/setup 變更後失效）：自動 fallback 到可用 target 或阻止執行並通知

### Flux-Pumped JPA Bias Sweep（可重現步驟）

以下流程用於重現官方 `Flux-pumped JPA` bias sweep 語義（bias 軸）：

1. 選擇 `Flux-pumped Josephson Parametric Amplifier (JPA)`（或等價 schema）
2. 在 `Simulation Setup` 開啟 `Enable Sweep`
3. `Sweep Target` 選擇 bias 對應 source 參數（建議 `sources[1].current_amp`；若 schema 以等效參數表示也可用 `Lj`）
4. 在 `Parameter Sweeps` 新增至少一個 axis，設定 `Sweep Start / Stop / Points`（可再新增第二軸做切片分析）
5. 執行 `Run Simulation`
6. 在 `Simulation Results` 的 `Sweep Result View` 選擇 `Compare Axis`、固定其餘軸，再為各 trace 選擇不同的 `sweep value`
7. 驗證單一 shared plot 會以 `Frequency` 為 X 軸，並疊加目前 compare axis 下不同值的多條 traces

## Run Simulation 契約（Load-or-Run）

`Run Simulation` 的正式語義是：

1. 以 source-form schema 建立 snapshot/hash
2. 以 normalized simulation setup 建立 snapshot/hash
3. 先查 result cache（schema + setup 完全相同）
4. cache miss 才提交 Julia solver

## Logs 契約

`Logs` 至少要可追蹤：

- schema 載入
- setup 正規化摘要
- cache lookup（hit/miss）
- solver 啟動
- 長時間執行 heartbeat/progress
- 成功或失敗摘要

!!! note "長時間求解"
    對 multi-pump 或高 harmonics case，Logs 必須持續顯示 still running 訊息，
    避免 UI 呈現靜止假象。

## Save Results to Dataset

`Save Results to Dataset` 是手動匯出，不是 cache key 的來源。

建議落地模型：

1. 選擇目標 `DatasetRecord`
2. 建立可見 `ResultBundleRecord`
3. 將此 run 產生的 `DataRecord` 綁到該 bundle

## Simulation -> Characterization Bridge Contract

!!! note "Current implementation（2026-03-04）"
    `Save Raw Simulation Results` 與 `Save Post-Processed Results` 都會建立 `ResultBundleRecord`，
    並使用 `ResultBundleDataLink` 關聯該次輸出的 traces。

!!! important "Contract"
    Characterization `Source Scope` 選到特定 bundle 時，只能分析該 bundle linked traces。
    `All Dataset Records` 可混合多來源 records，但仍由 trace-first 相容性決定可執行分析。

!!! important "Provenance"
    Simulation 端建立 bundle 時，`source_meta` + `config_snapshot` 必須足以回推上游輸入：
    至少包含 `origin`、來源 bundle（若有）、flow/setup snapshot。

## Dataset Metadata Boundary

!!! important "Dashboard-only"
    `/simulation` 不得顯示 `Dataset Metadata Summary` 卡片。
    dataset metadata 相關資訊與編輯入口只留在 `Pipeline Dashboard`。

!!! warning "與 Run 行為邊界"
    dataset metadata 不得影響本頁 solver setup 提交流程；
    本頁不可提供任何 metadata 寫入按鈕或表單。

## Cross-source Design Workflow Visibility

`/simulation` 不需要重寫 page hierarchy，但結果區與 save flow 必須清楚顯示：

- `Current Design Scope`
- 目前 trace 的 `source_kind`
- 目前 trace batch 的 provenance / stage
- 這條路徑是 `inspect-only` 還是已可進入 cross-source design workflow

!!! important "Inspect-first boundary"
    simulation runtime result view 可以維持 inspect-first；
    但若 cross-source compare 尚未直接在 `/simulation` fully expose，
    必須明確顯示 blocked-state，告知 compare 需在 save 到同一個 design scope 後，
    由 trace-first / TraceStore-first path 於 `Raw Data` / `Characterization` 進行。

!!! warning "No backend locator leakage"
    本頁可顯示 TraceStore-first authority 已啟用，但不可把 backend-specific
    `store_uri` / local path layout 當成使用者可理解的主要 provenance UI。

## Post Processing

`Post Processing` 是 simulation 後處理管線，必須遵守：

- 不重跑 solver
- 僅使用已完成 simulation 的結果矩陣
- 每個 flow 可由多個 steps 組成（step chain）

!!! important "M1 邊界"
    第一版僅支援 `Port-level` 後處理，不支援 `Nodal-level`（內部節點）矩陣消元。

### Pipeline 佈局契約

`Post Processing` 區塊採「大卡 + 小卡串接」：

- 大卡：`Post Processing`
- 固定小卡：
  - `Input Node`
  - `Output Node`
- 動態 Step 小卡：
  - 使用者透過 `Add Step` 新增 step
  - 每張 step card 可指定 type（M1: `Coordinate Transformation` / `Kron Reduction`）
  - step 可刪除與重設，執行時依卡片順序串接

!!! important "串接語義"
    每個 Kron step 的 keep labels 必須來自它「上游 step 鏈」的輸出基底。
    例如先做 cm/dm 轉換後，後續 Kron keep 選項應顯示 `cm(...)`、`dm(...)`，而不是原始 port 編號。

!!! note "Kron Keep Basis 互動"
    `Keep Basis Labels` 必須支援連續多選，不可每點一次就關閉選單。
    可採 chip-toggle / top-nav 式選取，並提供 `Select All` / `Clear` 快速操作。

### Post-Processing Input Source 契約

`Input Node` 必須提供 `Input Y Source` 選擇：

- `Raw Y`
- `PTC Y`

!!! important "來源可見性"
    `Post Processing Results` 必須能明確顯示目前輸出來自 `Raw Y` 或 `PTC Y`。
    保存時的 flow snapshot 也必須包含此來源欄位。

### Scope 與輸入矩陣

- 後處理的基礎矩陣以 port-space `Y(ω)` 為主
- 若來源僅提供 `Z(ω)`，需先轉成 `Y(ω)=Z(ω)^{-1}`
- `Mode Filter` 預設 `Base`；`Sideband` 可作為進階選項

!!! note "Z 與 Y 的關係"
    `Z ↔ Y` 是矩陣反矩陣關係，不是單純差一個 `jω` 係數。

### Step Types (M1)

1. `Coordinate Transformation`
2. `Kron Reduction`

### Coordinate Transformation 契約

對 port 矩陣做座標轉換時，必須使用：

`Y_m = A^{-T} · Y · A^{-1}`

其中：

- `V_m = A · V`
- `I_m = A^{-T} · I`

!!! warning "禁止 direct S-domain CT"
    Coordinate Transformation 與 Kron Reduction 只允許在 `Y/Z` 域執行。
    禁止直接對 `S` 施作座標變換。

#### cm/dm 模板與正規化

M1 必須提供 `common/differential` 模板，且支援：

- `Auto (Electrical Centroid)`：自動計算 `α, β`
- `Manual`：手動輸入 `α, β`

!!! important "Weight Mode 與可編輯性"
    - `Auto`：`alpha` / `beta` 欄位必須 disabled（不可手動編輯）
    - `Manual`：`alpha` / `beta` 欄位必須可編輯
    - 執行層在 `Auto` 模式必須使用 schema 的 C-to-ground 權重來源，不可採用 UI 殘留手動值

cm/dm 定義：

- `V_cm = αV1 + βV2`
- `V_dm = V1 - V2`
- 約束：`α + β = 1`

!!! important "正規化語義"
    這裡的正規化是電氣質心權重（`α+β=1`），不是量子矩陣元素修正因子。

#### Auto αβ（Electrical Centroid）提取規則

M1 預設用電容權重：

- `w1 = Σ C(node1 ↔ reference_set)`
- `w2 = Σ C(node2 ↔ reference_set)`
- `α = w1 / (w1 + w2)`
- `β = w2 / (w1 + w2)`

M1 先採 `reference_set={0}`（ground-only）。
自訂 reference set（例如 `{0, drive_line}`）列為後續版本。

### Kron Reduction 契約

Kron Reduction 必須使用 Schur complement：

`Y_red = Y_bb - Y_bi · Y_ii^{-1} · Y_ib`

且 API 必須以 `keep set` 為主，`drop set` 可由補集推導。

!!! warning "數值穩定性"
    實作必須用 `solve`，不得直接計算 `inv`。若 `Y_ii` 條件數過高，必須回報 warning。

## Post Processing 與儲存

後處理可選擇保存為新 bundle。

UI 必須在 `Run Post Processing` 成功後提供 `Save Post-Processed Results` 動作，且：

- 按鈕位置必須在 `Post Processing Results` 區塊（對齊 `Simulation Results` 的 save 位置）
- `Post Processing` 輸入區塊不得放置此保存按鈕
- 未執行後處理前，保存按鈕必須 disabled
- 調整 pipeline 參數使輸出失效後，保存按鈕必須回到 disabled
- 保存期間按鈕必須顯示 loading state
- 允許 `Create New` 與 `Append to Existing` dataset 模式

### Post-Processing Setup（流程設定保存）

`Post Processing` 的 Input Node 必須提供 setup 保存能力（比照 `Simulation Setup`）：

- `Post-Processing Setup` selector（可載入既有設定）
- `Save Setup` 動作（可命名並覆寫同名/同 id 設定）
- `Delete Setup` 動作（刪除目前選取設定）

保存內容至少包含：

- `Mode Filter`
- `Mode`
- `Z0`
- step chain（type / enabled / 參數 / 順序）

!!! important "套用與失效規則"
    載入 setup 或修改 pipeline 參數後，先前 post-processed output 視為失效，
    `Post Processing Results` 需等待重新 `Run Post Processing` 才可再保存結果。

建議資料模型：

- `bundle_type=simulation_postprocess`
- `role=derived_from_simulation`
- `source_meta` 記錄來源 simulation bundle id
- `config_snapshot` 記錄 flow spec（mode filter、A、keep/drop、step 順序）
- bundle 需綁定本次後處理輸出的 `DataRecord`（至少 `y_params` 的 `real/imaginary`）

### Parameter Sweep 輸入下的 Post Processing（Current Contract）

!!! important "Current contract（2026-03-07）"
    若 `simulation_postprocess` 的輸入是 parameter sweep：
    1. canonical source of truth 仍必須是完整 post-processed sweep bundle payload，而不是代表點
    2. `representative_point_index` 只能作 `Post Processing Results` 的 quick-inspect projection
    3. `Post Processing Results` 可以先顯示代表點/切片，但不得把該投影誤寫為整個後處理 sweep 的 authority
    4. raw simulation bundle 與 post-processed sweep bundle 必須維持兩個不同節點，各自保存 provenance

### Post-Processed Sweep 保存最低契約（Current）

當 `bundle_type=simulation_postprocess` 且來源 simulation bundle 為 `run_kind=parameter_sweep`，保存結果至少需包含：

- `source_meta.source_simulation_bundle_id`
- `source_meta.source_run_kind = "parameter_sweep"`
- `config_snapshot.input_y_source`
- `config_snapshot` 的完整 post-processing flow spec
- `config_snapshot.sweep_setup_hash`（對應來源 sweep）
- `result_payload.sweep_axes`
- `result_payload.point_count`
- `result_payload.points[]`（每點至少含 `source_point_index`、`axis_indices`、`axis_values`、以及該點 post-processed result 或可穩定回推該點結果的 handle）
- `result_payload.representative_point_index`

!!! warning "不可偷換成單點輸出"
    若只保存代表點輸出而遺失 sweep 軸與 point metadata，該 bundle 不得宣稱自己是完整的 post-processed sweep authority。

!!! important "Post-Processed Sweep Save 語意"
    若來源是 sweep run，`Save Post-Processed Results` 目前保證的是 provenance、
    replayability 與 explorer 可讀的 projection。
    此動作本身不承諾每個 post-processed sweep 點都已作為 fully materialized
    processed-value snapshot 寫入 durable storage。

!!! note "Future full snapshot is additive"
    若未來需要 self-contained snapshot/export artifact，應以新增契約或 subtype
    另行批准；不要把目前的 save 動作文件化成「一定落盤所有 processed points」。

### HFSS Comparable 語意標記

`Post Processing Results` 必須提供 `HFSS Comparable` 狀態標記（badge/label）。

判定條件（同時滿足）：

1. `Port Termination Compensation` 已啟用
2. pipeline 內至少有一個啟用中的 `Coordinate Transformation`
3. `Input Y Source = PTC Y`

!!! warning "條件不足時必須可解釋"
    若 `HFSS Comparable` 不成立，UI 必須顯示明確 reason，
    例如「PTC 未啟用」或「缺少 Coordinate Transformation」或「Input Y Source 非 PTC Y」。

## Normalization 分域（避免混淆）

本頁只處理兩類概念中的第一類：

1. `Coordinate Transformation` 的權重正規化（本頁範圍）
   - `V_cm = αV1 + βV2`
   - 約束 `α + β = 1`
   - 物理意義：電氣質心權重，用於降低 cm/dm 串擾
2. 量子衰減公式中的矩陣元素正規化（不在本頁）
   - 例如 `Γ1 = Re{Y}/C_Q` 的量子修正因子（matrix-element normalization）
   - 常見寫法：`β_q = <0|n|1> / n_QHO^{01}`
   - 屬於 `/characterization` 與 physics explanation，不在 `/simulation` 內實作

!!! note "名稱相同但語義不同"
    上述兩者都常被稱為 normalization，但不是同一件事，不能混用。

## 與 Nodal 四步管線的對應

研究筆記中的四步管線為：

1. Raw Nodal `Y`
2. Topological Kron（消除內部節點）
3. Coordinate Transformation
4. Modal Kron

本頁 M1 只落地 `Port-level` 版本的 3/4。
Nodal internal-node elimination（步驟 1/2 的完整 UI 化）列為後續版本，不在 M1。

## 與 Characterization 的邊界

`/simulation` 的 Post Processing 僅負責矩陣轉換與降維。

`Physics Extraction`（例如 `C_eff`, `T1`）屬於 `/characterization`，不在本頁實作。

## Simulation Results 節點語義

`Simulation Results` 顯示「最近一次 Run Simulation」的原始 quick-inspect 視圖：

- 需在 Run Simulation 成功後立即可用（不需先跑 Post Processing）
- 保留 `S/Y/Z/QE/CM/Complex` family 切換、metric selector、Add Trace cards、shared plot

!!! important "Raw S 不可被 PTC 改寫"
    即使啟用 PTC，`Simulation Results` 的 `S` 仍必須是 solver-native raw `S`。
    Raw View 的 PTC 僅可影響 `Y/Z` family（含相依的顯示來源切換）。

## Post Processing Results 節點語義

`Post Processing Results` 為獨立區塊，顯示「最近一次 Run Post Processing」輸出節點：

- 未執行 Post Processing：顯示等待提示
- 成功執行後：使用與 `Simulation Results` 對齊的 Result Family Explorer 互動（family/metric/trace cards/shared plot）
- 調整 pipeline step 參數後：舊輸出節點視為失效，需重新 Run Post Processing

### Post-Processed Sweep Result View 契約

當 `Post Processing Results` 的 canonical output 為 `run_kind=parameter_sweep` 時，
主結果視圖必須直接切到 canonical sweep compare surface，而不是再額外疊一張
代表點 quick preview 圖與另一張 sweep 圖：

- 區塊抬頭需清楚區分：
  - canonical full sweep payload
  - UI preview / projection（例如 representative point quick preview）
- `selectors`（最少）：
  - `family`
  - `metric`
  - `Compare Axis`
  - 其餘 `Fixed Axis` selectors
  - `Add Trace` + 多個 trace card
  - 每個 trace card 必須能選 `sweep value`
  - `Output Port` / `Input Port`
  - `Output Mode` / `Input Mode`
- `outputs`（最少）：
  - `單一 shared plot`：`X = Frequency`、`Y = selected metric`
  - `多條 traces`：每條 trace 代表不同的 post-processed sweep value
- representative point 不得升格為 authority；preview 只能是 quick-inspect projection
- 若目前 save/persistence 尚未支援 canonical post-processed full sweep，必須明示 limitation，不得把 preview 假裝成 canonical export

!!! note "Processed S 的來源"
    `Post Processing Results` 的 `S` 必須由 post-processed `Y/Z` 轉換得到，
    不得使用 direct S-domain transformation。

## Runtime Contract Snapshot

### Input

- active schema source-form definition（DB 持久化）
- normalized simulation setup
- optional post-processing flow spec（steps + input Y source）

### Output

- simulation raw result cache/bundle（含 raw `S/Y/Z` family）
- optional post-processed output node（matrix family explorer 可讀）
- optional post-processed sweep bundle（若輸入為 raw sweep，canonical authority 仍需保留全 sweep payload）
- 可追蹤 logs（cache hit/miss、solver run、post-processing run）

### Invariants

1. `Simulation Results` 與 `Post Processing Results` 狀態分離，但互動能力對齊
2. raw `S` 永遠保持 solver-native，不受 PTC 改寫
3. PTC 僅允許在 `Y` 域先施作，再導出 `Z`（與可選的 post-processed `S`）
4. coordinate transform / kron reduction 僅允許在 `Y/Z` 域執行

### Failure Modes

- schema parse/validation failure -> run 被拒絕並給 field-level 錯誤
- solver long-running / timeout -> log heartbeat + warning，不靜默
- invalid post-processing step chain（basis label 不可用）-> run 被拒絕
- HFSS comparable 條件不足 -> 需顯示 `Not comparable` 與可解釋原因

## Code Reference Map

- page orchestration + sections:
  - [`simulation/__init__.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/simulation/__init__.py)
- simulation runtime state:
  - [`simulation/state.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/app/pages/simulation/state.py)
- post-processing application:
  - [`post_processing.py`](/Users/arfiligol/Github/superconducting-circuits-tutorial/src/core/simulation/application/post_processing.py)

## Runtime Parity Checklist

release 前至少確認：

1. Schema Editor Expanded Preview 與 Simulation Netlist Configuration 使用同一 expansion pipeline
2. `Simulation Results` family source 切換契約一致（`S=raw only`, `Y/Z=raw|PTC`）
3. `Post Processing Results` 命名、title、y-axis label 與 trace card output/input 一致
4. save raw/save post-processed 都寫入 bundle provenance（origin/source/config snapshot）
