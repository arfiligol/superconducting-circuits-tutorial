from dataclasses import dataclass, field
from typing import Literal

ApiErrorCategory = Literal["not_found", "validation", "forbidden", "conflict"]


@dataclass(frozen=True)
class ServiceFieldError:
    field: str
    message: str


@dataclass(frozen=True)
class ServiceError(Exception):
    status_code: int
    code: str
    category: ApiErrorCategory
    message: str
    field_errors: tuple[ServiceFieldError, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return self.message


def service_error(
    status_code: int,
    *,
    code: str,
    category: ApiErrorCategory,
    message: str,
    field_errors: tuple[ServiceFieldError, ...] = (),
) -> ServiceError:
    return ServiceError(
        status_code=status_code,
        code=code,
        category=category,
        message=message,
        field_errors=field_errors,
    )
