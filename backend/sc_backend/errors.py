"""Structured backend error helpers for non-HTTP consumers."""

from fastapi import HTTPException
from src.app.api.errors import normalize_http_exception_payload
from src.app.api.schemas.errors import ApiErrorBodyResponse


def normalize_cli_error(exc: HTTPException) -> ApiErrorBodyResponse:
    return normalize_http_exception_payload(exc)
