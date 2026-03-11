from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.app.services.service_errors import ServiceError


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ServiceError, _service_error_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _request_validation_handler)


async def _service_error_handler(_: Request, exc: Exception) -> JSONResponse:
    service_exc = exc if isinstance(exc, ServiceError) else _unexpected_service_error(exc)
    return JSONResponse(
        status_code=service_exc.status_code,
        content={
            "error": {
                "code": service_exc.code,
                "category": service_exc.category,
                "message": service_exc.message,
                "status": service_exc.status_code,
                "field_errors": [
                    {"field": field_error.field, "message": field_error.message}
                    for field_error in service_exc.field_errors
                ],
            }
        },
    )


async def _http_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    http_exc = (
        exc
        if isinstance(exc, HTTPException)
        else HTTPException(status_code=500, detail=str(exc))
    )
    payload = _normalize_http_exception_payload(http_exc)
    return JSONResponse(status_code=http_exc.status_code, content={"error": payload})


async def _request_validation_handler(_: Request, exc: Exception) -> JSONResponse:
    validation_exc = exc if isinstance(exc, RequestValidationError) else RequestValidationError([])
    field_errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in validation_exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "request_validation_failed",
                "category": "validation",
                "message": "Request validation failed.",
                "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "field_errors": field_errors,
            }
        },
    )


def _normalize_http_exception_payload(exc: HTTPException) -> dict[str, Any]:
    detail = exc.detail
    if isinstance(detail, dict):
        raw_payload = dict(detail)
        payload: dict[str, Any] = {
            "code": raw_payload.get("code", _default_error_code(exc.status_code)),
            "category": raw_payload.get("category", _default_error_category(exc.status_code)),
            "message": raw_payload.get("message", "Request failed."),
            "status": exc.status_code,
            "field_errors": raw_payload.get("field_errors", []),
        }
        return payload

    return {
        "code": _default_error_code(exc.status_code),
        "category": _default_error_category(exc.status_code),
        "message": str(detail),
        "status": exc.status_code,
        "field_errors": [],
    }


def _default_error_code(status_code: int) -> str:
    if status_code == status.HTTP_404_NOT_FOUND:
        return "resource_not_found"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "forbidden"
    if status_code == status.HTTP_409_CONFLICT:
        return "conflict"
    if status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
        return "validation_error"
    return "request_failed"


def _default_error_category(status_code: int) -> str:
    if status_code == status.HTTP_404_NOT_FOUND:
        return "not_found"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "forbidden"
    if status_code == status.HTTP_409_CONFLICT:
        return "conflict"
    return "validation"


def _unexpected_service_error(exc: Exception) -> ServiceError:
    return ServiceError(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="request_failed",
        category="validation",
        message=str(exc),
    )
