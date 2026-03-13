# TraceStore Schema Evolution Plan

最後更新：2026-03-12

本文件定義 Zarr / TraceStore payload 的 schema evolution 策略，讓 numeric payload 與 SQLite metadata 一樣具備版本化與可回讀能力。

## Goals

1. TraceStore payload 不因欄位或 layout 調整而靜默壞掉
2. backend / worker / CLI 能辨識當前 TraceStore contract version
3. schema 變更時，要有 read-compat、migration、或 rebuild 策略
4. provenance 必須能指出 payload 是用哪個 schema 寫出的

## Scope

適用於：

- `data/trace_store/` 下的 Zarr payload layout
- trace batch metadata 與 payload locator
- result linkage 與 persisted output handle 指向的 TraceStore object

不適用於：

- 單純 in-memory preview payload
- frontend local cache

## Required Version Markers

每個 persisted TraceStore payload 至少要能追到：

| 欄位 | 說明 |
|---|---|
| `schema_version` | TraceStore payload schema version |
| `backend` | storage backend，例如 `local_zarr` |
| `payload_role` | raw / processed / analysis / export |
| `writer_version` | 可選；標示產生 payload 的 app/component version |

版本標記可以存在：

- Zarr group attrs
- 或 metadata DB 對應 row
- 最佳情況是兩邊都可追到且互相對照

## Compatibility Modes

### Additive

- 新增 attrs / metadata
- 新增可選 dataset
- 不改現有 key 語意

預設要求：

- 舊 reader 繼續可讀
- 新 reader 需能容忍缺少新欄位

### Soft-Breaking

- reshape / rechunk 但可透過 adapter 重建等價 view
- payload role 細分，但仍可映射回舊角色

預設要求：

- 寫明 read-compat 規則
- 至少有 rebuild path

### Breaking

- 改核心 group/dataset key
- 改數值排列語意
- 改 result linkage 所依賴的 identifier 規則

預設要求：

- migration script
- 或一次性 rebuild strategy
- 或 read-compat adapter
- 並在 parity matrix / contract registry 記錄影響

## Evolution Strategy

### Preferred Order

1. additive-first
2. 若不能 additive，先提供 read-compat
3. 若 read-compat 成本過高，再定 rebuild strategy

### Rebuild Strategy Minimum Requirements

- 說明 rebuild input source
- 說明哪些 result / trace 會失效
- 說明如何驗證 rebuilt payload 與原 contract 等價

## Verification

每次 schema 演進至少驗證：

- current writer 能產出正確 version marker
- current reader 能讀 current schema
- current reader 能處理至少一個舊 schema sample，或明確 fail with structured error
- provenance / result linkage 仍能追到 payload

## Mapping To Phases

| 階段 | 要求 |
|---|---|
| Phase 5A | 定義 version marker、compatibility classes、baseline verification |
| Phase 5B | worker/runtime 寫入 payload 時附帶 version/provenance |
| Phase 6 | workflow/result recovery 依賴 persisted TraceStore contract 成功重建 |
| Phase 7 | migration / rebuild tooling 與 long-lived data policy 完整化 |

## Checklist

- [ ] TraceStore `schema_version` 欄位已定義
- [ ] version marker 的保存位置已定義（Zarr attrs / metadata DB / both）
- [ ] additive / soft-breaking / breaking 規則已採納
- [ ] 舊 payload read-compat 或 rebuild strategy 已定義
- [ ] TraceStore schema verification tests 已建立
- [ ] provenance / result linkage 可追到 payload schema version
- [ ] breaking 變更的 migration / rebuild policy 已記錄
