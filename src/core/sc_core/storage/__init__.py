"""Framework-agnostic storage and provenance contracts shared across surfaces."""

from sc_core.storage.contracts import (
    STORAGE_CONTRACT_VERSION,
    StorageRecordHandle,
    StorageRecordKind,
    TraceBatchHandle,
    TraceBatchProvenance,
    TraceResultLinkage,
    TraceStoreBackend,
    TraceStoreLocator,
)
from sc_core.storage.evolution import (
    TRACE_STORE_EVOLUTION_CONTRACT_VERSION,
    TRACE_STORE_SCHEMA_BASELINE_VERSION,
    TraceStorePayloadRole,
    TraceStoreVersionMarkers,
)

__all__ = [
    "STORAGE_CONTRACT_VERSION",
    "TRACE_STORE_EVOLUTION_CONTRACT_VERSION",
    "TRACE_STORE_SCHEMA_BASELINE_VERSION",
    "StorageRecordHandle",
    "StorageRecordKind",
    "TraceBatchHandle",
    "TraceBatchProvenance",
    "TraceResultLinkage",
    "TraceStoreBackend",
    "TraceStoreLocator",
    "TraceStorePayloadRole",
    "TraceStoreVersionMarkers",
]
