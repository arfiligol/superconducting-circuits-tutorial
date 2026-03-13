# Logging & Observability Plan

最後更新：2026-03-12

本文件定義 migration 期間與 post-migration 的 logging/observability 最低策略。

## 目標

讓 backend、worker、CLI、frontend 的 log 可以：

1. **可關聯**：一個 request/task 跨越多個 service 時，可用 correlation ID 串聯
2. **可過濾**：structured format + level 策略，讓 production 不被 debug noise 淹沒
3. **可追蹤**：task execution 的關鍵事件（submit → running → completed/failed）必須有明確 log points

## Structured Logging Format

統一使用 **JSON structured logging**，所有 service 的 log entry 至少包含：

| 欄位 | 說明 | 必要 |
|---|---|---|
| `timestamp` | ISO 8601 | ✅ |
| `level` | `debug` / `info` / `warning` / `error` / `critical` | ✅ |
| `logger` | module/component name | ✅ |
| `message` | human-readable message | ✅ |
| `correlation_id` | request ID / task ID | ✅ (if available) |
| `user_id` | 操作者 | optional |
| `workspace_id` | workspace context | optional |
| `task_id` | task context | optional |
| `duration_ms` | 操作耗時 | optional |
| `error_code` | 對應 error model category | optional |
| `extra` | 任意 structured data | optional |

## Redaction / Privacy Rules

觀測性不能以洩漏敏感資料為代價。下列內容不得直接寫入 logs：

- raw token / session secret / signing secret
- bootstrap admin password
- Redis/DB connection string 中的 credential
- desktop local credential cache
- 未經裁切的原始 trace payload / matrix numeric body
- 原始 request body 中的 secret fields

允許的替代方式：

- 記錄 redacted marker，例如 `***redacted***`
- 記錄 stable handle / id / debug_ref，而不是完整內容
- 對 trace payload 只記 metadata（shape、dtype、role、handle），不記完整數值

redaction 應在 logger boundary 完成，而不是期待呼叫端每次手動刪欄位。

## Log Level 策略

| Level | 使用場景 | Production 預設 |
|---|---|---|
| `debug` | 開發期間的詳細追蹤（SQL queries, Julia bridge calls, data shapes） | 關閉 |
| `info` | 關鍵業務事件（task submitted, dataset created, simulation completed） | 開啟 |
| `warning` | 非致命異常（deprecated usage, fallback triggered, slow query） | 開啟 |
| `error` | 可恢復的錯誤（API validation failure, worker retry） | 開啟 |
| `critical` | 不可恢復的系統錯誤（DB connection lost, worker crash） | 開啟 |

Production 預設 level：**`info`**，可透過環境變數覆寫。

## Correlation ID 傳遞策略

```text
Frontend (X-Request-ID header)
    → Backend API (middleware extracts, injects into context)
        → Worker (task payload carries correlation_id)
            → sc_core (logging context propagation)
```

### 實作方案

| Layer | 實作 |
|---|---|
| Backend (FastAPI) | middleware 自動生成 / 接收 `X-Request-ID`，注入 `contextvars` |
| Worker (RQ) | task payload 攜帶 `correlation_id`，worker 在 job context 設定 |
| CLI | 每次 command invocation 自動生成 `correlation_id` |
| Frontend | 在 API client 層自動附加 `X-Request-ID` header |
| sc_core | 透過 Python `logging` context filter 自動注入 |

## 技術選型

| 工具 | 用途 |
|---|---|
| Python `logging` + `structlog` | 結構化 log 產生（推薦 structlog 作為 processor pipeline） |
| `rich.logging.RichHandler` | 開發環境 console 美化（不用在 production） |
| `python-json-logger` | 備選方案（如不用 structlog） |

### 為什麼推薦 `structlog`

- 與 Python stdlib `logging` 完美整合
- processor pipeline 可插拔（dev 用 console renderer，prod 用 JSON renderer）
- 內建 `contextvars` 支援 → correlation ID propagation 開箱即用
- 與 FastAPI / RQ / pytest 都有成熟整合

## 各 Layer 的 Log Points

### Backend

| 事件 | Level | 必要欄位 |
|---|---|---|
| Request received | `info` | correlation_id, method, path, user_id |
| Request completed | `info` | correlation_id, status_code, duration_ms |
| Auth failure | `warning` | correlation_id, error_code |
| Validation error | `info` | correlation_id, error_code, field details |
| Task submitted | `info` | correlation_id, task_id, task_kind |
| DB query slow (> threshold) | `warning` | correlation_id, query, duration_ms |
| Unhandled exception | `error` | correlation_id, traceback |

### Worker

| 事件 | Level | 必要欄位 |
|---|---|---|
| Job received | `info` | task_id, task_kind, correlation_id |
| Execution started | `info` | task_id |
| Execution completed | `info` | task_id, duration_ms |
| Execution failed | `error` | task_id, error_code, retryable |
| Retry triggered | `warning` | task_id, retry_count |
| Julia bridge call | `debug` | task_id, function, duration_ms |

### CLI

| 事件 | Level | 必要欄位 |
|---|---|---|
| Command invoked | `debug` | command, correlation_id |
| API call | `debug` | method, path, duration_ms |
| Command completed | `info` | command, exit_code |
| Error | `error` | command, error_code |

## 環境配置

```bash
# .env.example additions
SC_LOG_LEVEL=info                    # debug / info / warning / error
SC_LOG_FORMAT=json                   # json (production) / console (dev)
SC_LOG_CORRELATION_HEADER=X-Request-ID
```

## 導入 Phases

| 階段 | 範圍 | 對應 Migration Phase |
|---|---|---|
| L1: Baseline | 選定 structlog、建立 shared logging config、backend middleware | Phase 5A/5B |
| L2: Correlation | correlation ID middleware + worker propagation + CLI | Phase 5B |
| L3: Enrichment | 補齊各 layer log points、slow query warning | Phase 6 |
| L4: Production Readiness | log level env config、console/JSON switch、docs | Phase 7 |

## Checklist

- [ ] 選定 logging library（推薦 structlog）
- [ ] 建立 shared logging config module（`sc_core` 或 `backend/src/app/infrastructure/`）
- [ ] Backend: correlation ID middleware
- [ ] Worker: correlation ID propagation
- [ ] CLI: auto correlation ID generation
- [ ] 定義必要 log points（上表）
- [ ] secret / token / credential / raw trace payload redaction policy 已實作
- [ ] 環境變數控制 log level + format
- [ ] 開發環境用 Rich console renderer
- [ ] Production 用 JSON renderer
- [ ] 加入 `pyproject.toml` dependency
- [ ] 更新 `docs/reference/guardrails/code-quality/logging.md`
