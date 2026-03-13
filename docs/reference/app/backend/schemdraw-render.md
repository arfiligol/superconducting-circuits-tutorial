---
aliases:
  - Backend Schemdraw Render
  - Schemdraw Render Service
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/app-reference
status: draft
owner: docs-team
audience: team
scope: Schemdraw render service 的 transport、request/response、diagnostics 與 execution boundary 契約。
version: v0.3.0
last_updated: 2026-03-13
updated_by: team
---

# Schemdraw Render

本頁定義 `Schemdraw` workspace 依賴的 backend render service 契約。

!!! info "Surface Boundary"
    本契約負責接收 Schemdraw Python source 與 relation config、執行受控 render，並回傳 SVG preview、diagnostics 與 preview metadata。
    寫回 canonical circuit definition、保存 editor draft、建立 simulation task、或以 streaming transport 提供進度事件都不屬於本頁責任。

!!! tip "Primary Consumer"
    主要消費者是 [Schemdraw](../frontend/research-workflow/schemdraw.md)。

---

## Transport

| 項目 | 規則 |
|---|---|
| Method | `POST` |
| Endpoint | `/api/backend/schemdraw/render` |
| Content Type | `application/json` |
| Response Type | `application/json` |
| Transport Style | request / response |

!!! warning "Transport Persistence"
    本契約以 **HTTP request / response** 為正式 transport。
    `WebSocket` 不是本契約成立的必要條件。

!!! info "Frontend Pairing"
    frontend 對應頁面是 [Schemdraw](../frontend/research-workflow/schemdraw.md)。
    這頁定義 transport 與 payload；editor interaction state 由 frontend page spec 定義。

---

## Request Contract

request body 至少必須包含：

| 欄位 | 型別 | 必要性 | 說明 |
|---|---|---|---|
| `source_text` | `string` | required | Schemdraw Python source |
| `relation_config` | `object` | required | relation config JSON object |
| `linked_schema` | `object | null` | optional | linked schema 的最小 metadata snapshot |
| `document_version` | `integer` | required | editor 每次變更遞增的版本號 |
| `request_id` | `string` | required | 單次 render request 的唯一識別 |
| `render_mode` | `string` | optional | `debounced` 或 `manual` |

### `linked_schema`

若 request 帶入 linked schema，shape 應為：

| 欄位 | 型別 | 必要性 | 說明 |
|---|---|---|---|
| `id` | `string | integer | null` | optional | schema identity |
| `name` | `string | null` | optional | schema display name |

??? example "Payload 範例 (Request)"
    ```json
    {
      "source_text": "import schemdraw\nimport schemdraw.elements as elm\n\ndef build_drawing(relation):\n    d = schemdraw.Drawing()\n    d += elm.Resistor()\n    return d\n",
      "relation_config": {
        "tag": "draft",
        "labels": { "P1": "input" }
      },
      "linked_schema": {
        "id": 12,
        "name": "Series LC"
      },
      "document_version": 18,
      "request_id": "req_20260313_0018",
      "render_mode": "debounced"
    }
    ```

---

## Validation & Execution Phases

backend render service 依序執行：

1. request envelope validation
2. `relation_config` shape validation
3. Python source parse / syntax validation
4. render entrypoint validation
5. controlled render execution
6. preview metadata extraction
7. response assembly

!!! info "Execution Layering"
    request validation、syntax validation、runtime execution 是不同層次。
    frontend 應能根據 `diagnostics` 區分是 request blocked、syntax error，還是 runtime error。

---

### Render Entrypoint Rule

backend render service 應要求 source 提供穩定 entrypoint。

| 項目 | 規則 |
|---|---|
| Entrypoint name | `build_drawing` |
| Input | `relation` object |
| Output | Schemdraw drawing object 或可轉成 SVG 的 render result |

### Relation Contract

render 時注入的 `relation` object 至少必須包含：

```python
relation = {
    "schema": {
        "id": int | str | None,
        "name": str | None,
    },
    "config": {...},
}
```

---

## Response Contract

成功建立 response envelope 時，backend 應回傳：

| 欄位 | 型別 | 必要性 | 說明 |
|---|---|---|---|
| `request_id` | `string` | required | 對應 request |
| `document_version` | `integer` | required | 對應 editor version |
| `status` | `string` | required | `rendered` / `syntax_error` / `runtime_error` / `blocked` |
| `svg` | `string | null` | optional | 成功 render 後的 SVG 字串 |
| `diagnostics` | `array` | required | syntax / validation / runtime diagnostics |
| `cursor_position` | `object | null` | optional | 最後 cursor / pen 位置 |
| `probe_points` | `array` | optional | probe point metadata |
| `render_time_ms` | `number | null` | optional | render 花費時間 |

### Diagnostics Item

`diagnostics` 陣列中的單筆項目至少必須包含：

| 欄位 | 型別 | 必要性 | 說明 |
|---|---|---|---|
| `severity` | `string` | required | `error` / `warning` / `info` |
| `code` | `string` | required | 穩定的 machine-readable code |
| `message` | `string` | required | 使用者可讀訊息 |
| `source` | `string` | required | `request` / `relation_config` / `python_syntax` / `render_runtime` |
| `blocking` | `boolean` | required | 是否阻止 render |
| `line` | `integer | null` | optional | source line |
| `column` | `integer | null` | optional | source column |

??? example "Payload 範例 (Response)"
    ```json
    {
      "request_id": "req_20260313_0018",
      "document_version": 18,
      "status": "rendered",
      "svg": "<svg><!-- ... --></svg>",
      "diagnostics": [],
      "cursor_position": {
        "x": 9.2,
        "y": 3.0
      },
      "probe_points": [
        { "name": "input", "x": 0.0, "y": 0.0 }
      ],
      "render_time_ms": 42.8
    }
    ```

---

## Error Model

| 情況 | HTTP Status | Response Rule |
|---|---|---|
| Request body 缺必要欄位 | `400` | 回傳標準 error envelope；不進入 render |
| Request body 格式合法，但 render blocked | `200` | 回傳正式 render response，`status = blocked` |
| Python syntax error | `200` | 回傳正式 render response，`status = syntax_error` |
| Render runtime error | `200` | 回傳正式 render response，`status = runtime_error` |
| Service unavailable | `503` | 回傳標準 error envelope |

!!! warning "Envelope 封裝規則"
    只要 request body 已通過基本結構檢查，frontend 就應收到正式 render response envelope。
    syntax error 與 runtime error 不應退化成 transport-level 失敗。

---

## Delivery Rules

| 項目 | 規則 |
|---|---|
| Latest-only apply | frontend 只採用 `request_id` 與 `document_version` 對應最新版本的 response |
| Stale preview | backend 不負責標示 stale；stale 狀態由 frontend 依 editor state 與 latest response 推導 |
| Cancellation | frontend 可取消進行中的 request；backend 應 best-effort 停止不再需要的 render |
| No implicit persistence | backend render service 不得隱式保存 source、relation config 或 SVG |
| No task semantics | 本契約不建立 task id，也不附著到 task lifecycle |

---

## Related SoT

- [Schemdraw](../frontend/research-workflow/schemdraw.md)
- [Schema Editor](../frontend/definition/schema-editor.md)
- [Circuit Netlist](../../data-formats/circuit-netlist.md)
- [Canonical Contract Registry](../../architecture/canonical-contract-registry.md)
