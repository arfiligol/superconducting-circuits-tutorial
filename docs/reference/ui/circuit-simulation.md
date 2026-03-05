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
version: v0.10.0
last_updated: 2026-03-05
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

### Parameter Sweep（MVP）

Sweep 軸的 target 來源必須固定為 expanded netlist 的 `components[*].value_ref`（去重後）。

- 只有有 `value_ref` 的 component 可被 sweep 選取；`default`-only component 不可作為 sweep target
- MVP 先支援單軸（Single Axis）
- `Sweep disabled` 時，`Run Simulation` 必須與既有 single-run 路徑完全一致

Sweep Setup 最小欄位：

- `enabled: bool`
- `axis_1.target_value_ref: str`（來自 `components[*].value_ref`）
- `axis_1.start / stop / points`
- `axis_1.unit`（可由 parameter spec 提示）

### Sweep Cache / Provenance 契約

當 sweep 啟用時：

1. normalized simulation setup 必須包含 `sweep` 區塊
2. 必須從該 `sweep` 區塊計算 `sweep_setup_hash`
3. result cache identity 仍走 `schema_source_hash + simulation_setup_hash`，其中 `simulation_setup_hash` 已含 sweep 設定
4. `source_meta` 與 `config_snapshot` 必須保存 `sweep_setup_hash` 與 sweep 軸摘要

### Sweep Logs 契約

`Logs` 必須額外可追蹤：

- sweep 維度（MVP=1）
- 總點數
- 每個 sweep 點的進度（例如 `point 3/11`）

### Sweep 結果結構契約（供後續 pipeline/analysis）

sweep run 成功後，bundle `result_payload` 需包含：

- `run_kind = "parameter_sweep"`
- `sweep_axes` metadata（target、unit、values、point_count）
- `points[]`（每點至少含 `axis_indices`、`axis_values`、該點 simulation result）
- `representative_point_index`（供 Result View quick-inspect）

匯出為 `DataRecord` 時，應在 `axes` 中明確附帶 sweep 軸 metadata，避免與 single-run traces 混淆。

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
