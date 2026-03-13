"""Structured backend error helpers for non-HTTP consumers."""

from dataclasses import dataclass

from fastapi import HTTPException
from src.app.api.errors import normalize_http_exception_payload, normalize_service_error_payload
from src.app.api.schemas.errors import ApiErrorBodyResponse
from src.app.services.service_errors import ServiceError


@dataclass(frozen=True)
class BackendContractError(Exception):
    error: ApiErrorBodyResponse

    def __str__(self) -> str:
        return self.error.message


def backend_contract_error(exc: ServiceError | HTTPException) -> BackendContractError:
    if isinstance(exc, ServiceError):
        return BackendContractError(normalize_service_error_payload(exc))
    return BackendContractError(normalize_http_exception_payload(exc))
