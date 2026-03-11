"""CLI-facing error translation helpers."""

from typing import NoReturn

import typer
from fastapi import HTTPException
from sc_backend import normalize_cli_error

from sc_cli.presenters import render_api_error


def exit_with_usage_error(message: str) -> NoReturn:
    _exit_with_message(f"error: {message}", exit_code=2)


def exit_with_runtime_error(message: str) -> NoReturn:
    _exit_with_message(f"error: {message}", exit_code=1)


def exit_for_http_exception(error: HTTPException) -> NoReturn:
    payload = normalize_cli_error(error)
    _exit_with_message(render_api_error(payload), exit_code=2 if error.status_code < 500 else 1)


def _exit_with_message(message: str, *, exit_code: int) -> NoReturn:
    typer.echo(message, err=True)
    raise typer.Exit(code=exit_code)
