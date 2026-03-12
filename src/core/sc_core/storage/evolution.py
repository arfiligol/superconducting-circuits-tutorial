from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sc_core.storage.contracts import TraceStoreBackend

TRACE_STORE_SCHEMA_BASELINE_VERSION = "1.0"
TRACE_STORE_EVOLUTION_CONTRACT_VERSION = "sc_tracestore_evolution.v1"
TraceStorePayloadRole = Literal["raw", "processed", "analysis", "export"]


@dataclass(frozen=True)
class TraceStoreVersionMarkers:
    """Canonical version markers stamped onto persisted TraceStore payloads."""

    schema_version: str
    backend: TraceStoreBackend
    payload_role: TraceStorePayloadRole
    writer_version: str | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "contract_version": TRACE_STORE_EVOLUTION_CONTRACT_VERSION,
            "schema_version": self.schema_version,
            "backend": self.backend,
            "payload_role": self.payload_role,
        }
        if self.writer_version is not None:
            payload["writer_version"] = self.writer_version
        return payload
