from typing import Literal, TypedDict

from fastapi import HTTPException

ApiErrorCategory = Literal["not_found", "validation", "forbidden", "conflict"]


class ApiFieldErrorDetail(TypedDict):
    field: str
    message: str


class ApiErrorDetail(TypedDict, total=False):
    code: str
    category: ApiErrorCategory
    message: str
    field_errors: list[ApiFieldErrorDetail]


def api_error(
    status_code: int,
    *,
    code: str,
    category: ApiErrorCategory,
    message: str,
    field_errors: list[ApiFieldErrorDetail] | None = None,
) -> HTTPException:
    detail: ApiErrorDetail = {
        "code": code,
        "category": category,
        "message": message,
    }
    if field_errors is not None:
        detail["field_errors"] = field_errors
    return HTTPException(status_code=status_code, detail=detail)
