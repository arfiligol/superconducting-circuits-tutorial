# Frontend-Backend Contract Sync Plan

最後更新：2026-03-12

本文件定義 frontend (TypeScript) 和 backend (Python/Pydantic) 之間 API contract 的同步策略，避免型別 drift。

## 問題

Backend 用 Pydantic model 定義 API schema，frontend 用 TypeScript types。兩邊手動維護 = 必然 drift：

- 欄位改名只改一邊
- 新增可選欄位忘記同步
- enum 值不一致
- request/response shape 不匹配卻到 runtime 才炸

## 策略：OpenAPI-First Contract Sync

```text
Pydantic models (backend)
    → FastAPI auto-generates OpenAPI spec
        → CI 自動 export openapi.json
            → openapi-typescript 生成 TypeScript types
                → frontend import generated types
```

### 為什麼選 OpenAPI-First

| 方案 | 優點 | 缺點 |
|---|---|---|
| 手動同步 | 零工具成本 | drift 是必然的 |
| Shared schema package (JSON Schema) | 真正的 single source | 需要額外 build step + 維護成本高 |
| **OpenAPI-First** | FastAPI 已自動產生 spec、工具鏈成熟、零額外 schema 維護 | 需要 CI pipeline |
| gRPC / tRPC | type-safe RPC | 架構改動太大，不適合當前 migration |

## 技術選型

| 工具 | 用途 |
|---|---|
| FastAPI built-in | 從 Pydantic models 自動產生 OpenAPI 3.1 spec |
| `openapi-typescript` | 從 OpenAPI spec 生成 TypeScript types |
| CI script | 自動化 export → generate → diff check |

### 工具版本

```bash
# Backend (已有)
# FastAPI 自帶 /openapi.json endpoint

# Frontend
npm install -D openapi-typescript    # TypeScript type generation
```

## Workflow

### 開發流程

```text
1. 修改 backend Pydantic model
2. 啟動 backend dev server
3. 執行 type generation script
4. Frontend import 新 types → TypeScript compiler 自動報錯不匹配的地方
```

### CI 流程

```text
1. CI 啟動 backend（或用 pytest fixture export spec）
2. Export openapi.json
3. 執行 openapi-typescript 生成 types
4. git diff 檢查是否有未 commit 的 type 變更
5. 若有 diff → CI fail，提醒 contributor 重新 generate
```

## 檔案放置

```text
backend/
├── src/app/
│   └── openapi_export.py          # script to export openapi.json without running server

frontend/
├── src/lib/api/
│   ├── generated/
│   │   └── schema.d.ts            # auto-generated, DO NOT EDIT
│   ├── client.ts                  # API client using generated types
│   └── README.md                  # explains generation workflow
```

## OpenAPI Export Script

Backend 不需要啟動 server 就能 export spec：

```python
# backend/src/app/openapi_export.py
"""Export OpenAPI spec without starting the server."""
import json
from pathlib import Path
from app.main import app  # FastAPI app instance

def export_openapi(output: Path = Path("openapi.json")) -> None:
    spec = app.openapi()
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    print(f"OpenAPI spec exported to {output}")

if __name__ == "__main__":
    export_openapi()
```

## Type Generation Script

```bash
# scripts/sync_api_types.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Exporting OpenAPI spec from backend..."
cd "$REPO_ROOT"
uv run python -m backend.src.app.openapi_export

echo "==> Generating TypeScript types..."
cd "$REPO_ROOT/frontend"
npx openapi-typescript "$REPO_ROOT/openapi.json" \
  --output src/lib/api/generated/schema.d.ts

echo "==> Done. Check frontend/src/lib/api/generated/schema.d.ts"
```

## CI Gate

```yaml
# .github/workflows/contract-sync.yml (概念)
name: API Contract Sync Check
on: [push, pull_request]
jobs:
  contract-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install backend deps
        run: pip install uv && uv sync
      - name: Export OpenAPI spec
        run: uv run python -m backend.src.app.openapi_export
      - name: Setup Node
        uses: actions/setup-node@v4
      - name: Install frontend deps
        run: cd frontend && npm ci
      - name: Generate types
        run: cd frontend && npx openapi-typescript ../openapi.json --output src/lib/api/generated/schema.d.ts
      - name: Check for uncommitted type changes
        run: git diff --exit-code frontend/src/lib/api/generated/
```

## Contract Test 補充

除了 type sync，還建議加 contract test 驗證 runtime 行為：

```python
# tests/contract/test_api_contract.py
"""Verify API responses match OpenAPI spec at runtime."""
import pytest
from fastapi.testclient import TestClient

def test_openapi_spec_is_valid(client: TestClient):
    """Ensure the OpenAPI spec endpoint returns valid JSON."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "paths" in spec
    assert "components" in spec

def test_dataset_list_matches_schema(client: TestClient):
    """Example: verify response shape matches spec."""
    response = client.get("/api/datasets")
    assert response.status_code == 200
    data = response.json()
    # Structural assertion — details depend on actual schema
    assert isinstance(data, list) or "items" in data
```

## 導入 Phases

| 階段 | 範圍 | 對應 Migration Phase |
|---|---|---|
| C1: Baseline | export script + first type generation | Phase 3（完結前） |
| C2: CI Gate | contract-sync CI workflow | Phase 6 |
| C3: Contract Tests | runtime contract tests | Phase 6/7 |

## Checklist

- [ ] 建立 `backend/src/app/openapi_export.py`
- [ ] 安裝 `openapi-typescript` 到 `frontend/` devDependencies
- [ ] 首次生成 `frontend/src/lib/api/generated/schema.d.ts`
- [ ] 建立 `scripts/sync_api_types.sh`
- [ ] Frontend API client 改用 generated types
- [ ] `.gitignore` 不 ignore generated types（需要 commit 以便 CI diff check）
- [ ] 建立 CI workflow `contract-sync.yml`
- [ ] 建立基礎 contract tests
- [ ] 更新 `README.md` 或 contributor docs 說明 type sync workflow
- [ ] 在 `package.json` 加入 `sync:types` script
