"""WS6 simulation-page client wrappers over the persisted task/result authority."""

from __future__ import annotations

import json
from typing import Any

from nicegui import ui

from app.api.schemas import (
    DesignTasksResponse,
    LatestTraceBatchResponse,
    SimulationTaskCreateRequest,
    TaskDispatchResponse,
    TaskResponse,
)


class ApiClientError(RuntimeError):
    """Raised when a same-origin `/api/v1` call returns an error payload."""

    def __init__(self, *, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = int(status_code)
        self.detail = str(detail)


async def _fetch_json(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
) -> Any:
    request_body = "undefined" if body is None else json.dumps(body, separators=(",", ":"))
    result = await ui.run_javascript(
        f"""
        const response = await fetch({json.dumps(path)}, {{
          method: {json.dumps(method)},
          headers: {{ 'Content-Type': 'application/json' }},
          credentials: 'same-origin',
          body: {request_body},
        }});
        let body = null;
        try {{
          body = await response.json();
        }} catch (_error) {{
          body = null;
        }}
        return {{ status: response.status, body }};
        """,
        timeout=30.0,
    )
    if not isinstance(result, dict):
        raise ApiClientError(status_code=500, detail="Invalid API client result.")
    status_code = int(result.get("status", 500))
    response_body = result.get("body")
    if status_code >= 400:
        detail = "API request failed"
        if isinstance(response_body, dict):
            if isinstance(response_body.get("detail"), str):
                detail = str(response_body["detail"])
            else:
                detail = json.dumps(response_body.get("detail", response_body))
        raise ApiClientError(status_code=status_code, detail=detail)
    return response_body


async def submit_simulation_task(payload: SimulationTaskCreateRequest) -> TaskDispatchResponse:
    """Submit one real simulation task through the public v1 API."""
    response_body = await _fetch_json(
        "POST",
        "/api/v1/tasks/simulation",
        body=payload.model_dump(mode="json"),
    )
    return TaskDispatchResponse.model_validate(response_body)


async def get_task(task_id: int) -> TaskResponse:
    """Fetch one persisted task through the public v1 API."""
    response_body = await _fetch_json("GET", f"/api/v1/tasks/{int(task_id)}")
    return TaskResponse.model_validate(response_body)


async def get_design_tasks(design_id: int) -> DesignTasksResponse:
    """Fetch persisted design tasks through the public v1 API."""
    response_body = await _fetch_json("GET", f"/api/v1/designs/{int(design_id)}/tasks")
    return DesignTasksResponse.model_validate(response_body)


async def get_latest_simulation_result(design_id: int) -> LatestTraceBatchResponse | None:
    """Fetch the latest completed raw simulation batch for one design."""
    try:
        response_body = await _fetch_json(
            "GET",
            f"/api/v1/designs/{int(design_id)}/simulation/latest",
        )
    except ApiClientError as exc:
        if exc.status_code == 404:
            return None
        raise
    return LatestTraceBatchResponse.model_validate(response_body)
