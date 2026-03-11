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

__all__ = [
    "STORAGE_CONTRACT_VERSION",
    "StorageRecordHandle",
    "StorageRecordKind",
    "TraceBatchHandle",
    "TraceBatchProvenance",
    "TraceResultLinkage",
    "TraceStoreBackend",
    "TraceStoreLocator",
]
