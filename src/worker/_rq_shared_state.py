"""Shared in-process state for RQ test backends."""

from __future__ import annotations

from typing import Any

FAKE_SERVER_BY_URL: dict[str, Any] = {}
