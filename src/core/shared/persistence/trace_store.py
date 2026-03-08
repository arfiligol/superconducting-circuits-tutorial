"""TraceStore abstractions for chunked numeric payload persistence."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Literal, NotRequired, Protocol, TypedDict, cast, runtime_checkable
from urllib.parse import urlparse

import numpy as np
from numpy.typing import ArrayLike, NDArray

from core.shared.persistence.database import DATABASE_PATH

TRACE_STORE_SCHEMA_VERSION = "1.0"
TRACE_STORE_PATH = DATABASE_PATH.parent / "trace_store"

TraceStoreBackend = Literal["local_zarr", "s3_zarr"]
TraceSelectionItem = int | slice
TraceSelection = tuple[TraceSelectionItem, ...]


class TraceAxisMetadata(TypedDict):
    """Axis metadata kept in the metadata DB."""

    name: str
    unit: str
    length: int


class TraceStoreRef(TypedDict):
    """Location reference for one trace payload inside a TraceStore backend."""

    backend: TraceStoreBackend
    store_key: str
    store_uri: NotRequired[str]
    group_path: str
    array_path: str
    dtype: str
    shape: list[int]
    chunk_shape: list[int]
    schema_version: str


@dataclass(frozen=True)
class TraceStoreRuntimeConfig:
    """Runtime configuration for backend selection and locator resolution."""

    default_backend: TraceStoreBackend
    local_root_path: Path
    s3_bucket: str | None = None
    s3_prefix: str = ""
    s3_endpoint_url: str | None = None


@dataclass(frozen=True)
class TraceWriteResult:
    """Metadata returned after materializing one trace payload."""

    axes: list[TraceAxisMetadata]
    store_ref: TraceStoreRef


@runtime_checkable
class TraceStoreBackendBinding(Protocol):
    """Backend-specific locator contract kept inside persistence."""

    backend: TraceStoreBackend

    def build_store_key(self, *, design_id: int, batch_id: int) -> str: ...

    def build_store_uri(self, *, store_key: str) -> str: ...


@runtime_checkable
class TraceStore(Protocol):
    """Slice-first contract for numeric trace payload storage."""

    @property
    def backend(self) -> TraceStoreBackend: ...

    def write_trace(
        self,
        *,
        design_id: int,
        batch_id: int,
        trace_id: int,
        values: ArrayLike,
        axes: Sequence[Mapping[str, object]],
        chunk_shape: Sequence[int] | None = None,
        array_path: str = "values",
    ) -> TraceWriteResult: ...

    def read_trace_slice(
        self,
        ref: Mapping[str, object],
        *,
        selection: TraceSelection,
    ) -> NDArray[np.generic]: ...

    def read_axis_slice(
        self,
        ref: Mapping[str, object],
        *,
        axis_name: str,
        selection: TraceSelectionItem = slice(None),
    ) -> NDArray[np.generic]: ...

    def read_trace_shape(self, ref: Mapping[str, object]) -> tuple[int, ...]: ...


class MissingTraceStoreDependencyError(RuntimeError):
    """Raised when optional TraceStore runtime dependencies are unavailable."""


@dataclass(frozen=True)
class LocalZarrTraceStoreBackend:
    """Backend-specific locator logic for local filesystem Zarr stores."""

    root_path: Path
    backend: Literal["local_zarr"] = "local_zarr"

    def build_store_key(self, *, design_id: int, batch_id: int) -> str:
        return _build_store_key(design_id=design_id, batch_id=batch_id)

    def build_store_uri(self, *, store_key: str) -> str:
        store_path = self.resolve_store_path(store_key=store_key)
        project_root = DATABASE_PATH.parent.parent
        try:
            return store_path.relative_to(project_root).as_posix()
        except ValueError:
            return str(store_path)

    def resolve_store_path(self, *, store_key: str) -> Path:
        return self.root_path / _normalize_store_key(store_key)


@dataclass(frozen=True)
class S3ZarrTraceStoreBackend:
    """Contract-only locator logic for a future S3-compatible Zarr backend."""

    bucket: str
    prefix: str = ""
    backend: Literal["s3_zarr"] = "s3_zarr"
    endpoint_url: str | None = None

    def __post_init__(self) -> None:
        if not self.bucket.strip():
            raise ValueError("S3ZarrTraceStoreBackend.bucket is required.")

    def build_store_key(self, *, design_id: int, batch_id: int) -> str:
        base_key = _build_store_key(design_id=design_id, batch_id=batch_id)
        if not self.prefix.strip():
            return base_key
        return _normalize_store_key(f"{self.prefix}/{base_key}")

    def build_store_uri(self, *, store_key: str) -> str:
        normalized_key = _normalize_store_key(store_key)
        return f"s3://{self.bucket}/{normalized_key}"


def get_trace_store_path() -> Path:
    """Return the configured local TraceStore root path."""
    override = str(os.getenv("SC_TRACE_STORE_ROOT", "")).strip()
    if override:
        path = Path(override).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    TRACE_STORE_PATH.mkdir(parents=True, exist_ok=True)
    return TRACE_STORE_PATH


def get_trace_store_runtime_config() -> TraceStoreRuntimeConfig:
    """Return the configured TraceStore runtime boundary."""
    default_backend = str(os.getenv("SC_TRACE_STORE_BACKEND", "local_zarr")).strip() or "local_zarr"
    if default_backend not in {"local_zarr", "s3_zarr"}:
        raise ValueError(f"Unsupported TraceStore backend: {default_backend}")
    return TraceStoreRuntimeConfig(
        default_backend=cast(TraceStoreBackend, default_backend),
        local_root_path=get_trace_store_path(),
        s3_bucket=(str(os.getenv("SC_TRACE_STORE_S3_BUCKET", "")).strip() or None),
        s3_prefix=str(os.getenv("SC_TRACE_STORE_S3_PREFIX", "")).strip(),
        s3_endpoint_url=(str(os.getenv("SC_TRACE_STORE_S3_ENDPOINT_URL", "")).strip() or None),
    )


def get_trace_store_backend_binding(
    *,
    backend: TraceStoreBackend | None = None,
    config: TraceStoreRuntimeConfig | None = None,
) -> TraceStoreBackendBinding:
    """Return the backend-owned locator binding for the requested backend."""
    runtime_config = config or get_trace_store_runtime_config()
    resolved_backend = backend or runtime_config.default_backend
    if resolved_backend == "local_zarr":
        return LocalZarrTraceStoreBackend(root_path=runtime_config.local_root_path)
    if resolved_backend == "s3_zarr":
        if not runtime_config.s3_bucket:
            raise ValueError("SC_TRACE_STORE_S3_BUCKET is required for s3_zarr backend.")
        return S3ZarrTraceStoreBackend(
            bucket=runtime_config.s3_bucket,
            prefix=runtime_config.s3_prefix,
            endpoint_url=runtime_config.s3_endpoint_url,
        )
    raise ValueError(f"Unsupported TraceStore backend: {resolved_backend}")


def coerce_trace_store_ref(ref: Mapping[str, object]) -> TraceStoreRef:
    """Validate and normalize one persisted store-ref mapping."""
    backend = str(ref.get("backend", "")).strip()
    if backend not in {"local_zarr", "s3_zarr"}:
        raise ValueError(f"Unsupported TraceStore backend: {backend or '<missing>'}")

    store_uri = str(ref.get("store_uri", "")).strip()
    store_key = _coerce_store_key(
        backend=cast(TraceStoreBackend, backend),
        raw_store_key=str(ref.get("store_key", "")).strip(),
        raw_store_uri=store_uri,
    )
    if store_uri:
        inferred_store_key = _coerce_store_key(
            backend=cast(TraceStoreBackend, backend),
            raw_store_key="",
            raw_store_uri=store_uri,
        )
        if inferred_store_key and inferred_store_key != store_key:
            raise ValueError("TraceStoreRef.store_key does not match TraceStoreRef.store_uri.")
    group_path = _normalize_group_path(str(ref.get("group_path", "")).strip())
    array_path = str(ref.get("array_path", "")).strip()
    dtype = str(ref.get("dtype", "")).strip()
    schema_version = str(ref.get("schema_version", "")).strip() or TRACE_STORE_SCHEMA_VERSION
    shape = _coerce_int_list(ref.get("shape"), field_name="shape")
    chunk_shape = _coerce_int_list(ref.get("chunk_shape"), field_name="chunk_shape")

    normalized_store_uri = _normalize_store_uri(
        backend=cast(TraceStoreBackend, backend),
        store_key=store_key,
        raw_store_uri=store_uri,
    )
    if not store_key:
        raise ValueError("TraceStoreRef.store_key is required.")
    if not group_path:
        raise ValueError("TraceStoreRef.group_path is required.")
    if not array_path:
        raise ValueError("TraceStoreRef.array_path is required.")
    if not dtype:
        raise ValueError("TraceStoreRef.dtype is required.")
    if not shape:
        raise ValueError("TraceStoreRef.shape is required.")
    if len(chunk_shape) != len(shape):
        raise ValueError("TraceStoreRef.chunk_shape must match shape dimensionality.")

    return TraceStoreRef(
        backend=cast(TraceStoreBackend, backend),
        store_key=store_key,
        store_uri=normalized_store_uri,
        group_path=group_path,
        array_path=array_path,
        dtype=dtype,
        shape=shape,
        chunk_shape=chunk_shape,
        schema_version=schema_version,
    )


def resolve_trace_store_path(
    ref: Mapping[str, object],
    *,
    config: TraceStoreRuntimeConfig | None = None,
) -> Path:
    """Resolve a local TraceStore path via the backend-owned binding."""
    normalized_ref = coerce_trace_store_ref(ref)
    binding = get_trace_store_backend_binding(
        backend=normalized_ref["backend"],
        config=config,
    )
    if not isinstance(binding, LocalZarrTraceStoreBackend):
        raise NotImplementedError(
            "Filesystem path resolution is only available for local_zarr refs."
        )
    return binding.resolve_store_path(store_key=normalized_ref["store_key"])


class LocalZarrTraceStore:
    """Local-filesystem TraceStore backed by Zarr."""

    def __init__(self, root_path: Path | None = None):
        resolved_root = Path(root_path) if root_path is not None else get_trace_store_path()
        resolved_root.mkdir(parents=True, exist_ok=True)
        self._backend_binding = LocalZarrTraceStoreBackend(root_path=resolved_root)

    @property
    def backend(self) -> TraceStoreBackend:
        """Return the backend identifier for this TraceStore implementation."""
        return self._backend_binding.backend

    @property
    def root_path(self) -> Path:
        """Expose the resolved local root path for local-backend tests."""
        return self._backend_binding.root_path

    def write_trace(
        self,
        *,
        design_id: int,
        batch_id: int,
        trace_id: int,
        values: ArrayLike,
        axes: Sequence[Mapping[str, object]],
        chunk_shape: Sequence[int] | None = None,
        array_path: str = "values",
    ) -> TraceWriteResult:
        """Write one ND trace and its axis arrays to local Zarr storage."""
        zarr = _require_zarr()
        payload = np.asarray(values)
        if payload.ndim == 0:
            raise ValueError("Trace values must be at least 1D.")

        normalized_axes = _normalize_axes(axes, expected_shape=payload.shape)
        normalized_chunk_shape = _normalize_chunk_shape(payload.shape, chunk_shape)
        store_key = self._backend_binding.build_store_key(design_id=design_id, batch_id=batch_id)
        store_path = self._backend_binding.resolve_store_path(store_key=store_key)

        root = zarr.open_group(store=store_path, mode="a")
        trace_group = _require_group(root, f"/traces/{trace_id}")
        trace_group.create_array(
            name=array_path,
            data=payload,
            chunks=tuple(normalized_chunk_shape),
            overwrite=True,
        )
        axes_group = trace_group.require_group("axes")
        for axis in normalized_axes:
            axis_values = np.asarray(axis["values"])
            axes_group.create_array(
                name=axis["name"],
                data=axis_values,
                chunks=(int(axis_values.shape[0]),),
                overwrite=True,
                attributes={"unit": axis["unit"], "length": int(axis_values.shape[0])},
            )
        trace_group.attrs["axes"] = [
            {"name": axis["name"], "unit": axis["unit"], "length": axis["length"]}
            for axis in normalized_axes
        ]

        return TraceWriteResult(
            axes=[
                TraceAxisMetadata(name=axis["name"], unit=axis["unit"], length=axis["length"])
                for axis in normalized_axes
            ],
            store_ref=TraceStoreRef(
                backend="local_zarr",
                store_key=store_key,
                store_uri=self._backend_binding.build_store_uri(store_key=store_key),
                group_path=f"/traces/{trace_id}",
                array_path=array_path,
                dtype=str(payload.dtype),
                shape=[int(dimension) for dimension in payload.shape],
                chunk_shape=normalized_chunk_shape,
                schema_version=TRACE_STORE_SCHEMA_VERSION,
            ),
        )

    def read_trace_slice(
        self,
        ref: Mapping[str, object],
        *,
        selection: TraceSelection,
    ) -> NDArray[np.generic]:
        """Read one slice directly from the stored Zarr array."""
        array = self._open_trace_array(ref)
        normalized_selection = _normalize_selection(selection, ndim=int(array.ndim))
        return np.asarray(array[normalized_selection])

    def read_axis_slice(
        self,
        ref: Mapping[str, object],
        *,
        axis_name: str,
        selection: TraceSelectionItem = slice(None),
    ) -> NDArray[np.generic]:
        """Read one axis array slice without materializing the main trace payload."""
        normalized_ref = coerce_trace_store_ref(ref)
        trace_group = self._open_trace_group(normalized_ref)
        axes_group = trace_group["axes"]
        return np.asarray(axes_group[str(axis_name)][selection])

    def read_trace_shape(self, ref: Mapping[str, object]) -> tuple[int, ...]:
        """Return stored shape metadata for one trace payload."""
        normalized_ref = coerce_trace_store_ref(ref)
        return tuple(int(dimension) for dimension in normalized_ref["shape"])

    def _resolve_store_path(self, normalized_ref: TraceStoreRef) -> Path:
        if normalized_ref["backend"] != "local_zarr":
            raise NotImplementedError(
                "LocalZarrTraceStore only handles local_zarr refs. "
                "s3_zarr remains contract-safe only."
            )
        return self._backend_binding.resolve_store_path(store_key=normalized_ref["store_key"])

    def _open_trace_group(self, ref: Mapping[str, object]):
        zarr = _require_zarr()
        normalized_ref = coerce_trace_store_ref(ref)
        root = zarr.open_group(store=self._resolve_store_path(normalized_ref), mode="r")
        return _get_group(root, normalized_ref["group_path"])

    def _open_trace_array(self, ref: Mapping[str, object]):
        trace_group = self._open_trace_group(ref)
        normalized_ref = coerce_trace_store_ref(ref)
        return trace_group[normalized_ref["array_path"]]


def _require_group(root_group: Any, group_path: str):
    group = root_group
    for segment in _split_group_path(group_path):
        group = group.require_group(segment)
    return group


def _get_group(root_group: Any, group_path: str):
    group = root_group
    for segment in _split_group_path(group_path):
        group = group[segment]
    return group


def _split_group_path(group_path: str) -> list[str]:
    normalized = _normalize_group_path(group_path)
    return [segment for segment in normalized.strip("/").split("/") if segment]


def _normalize_group_path(group_path: str) -> str:
    segments = [segment for segment in group_path.split("/") if segment]
    if not segments:
        return ""
    return "/" + "/".join(segments)


def _normalize_axes(
    axes: Sequence[Mapping[str, object]],
    *,
    expected_shape: tuple[int, ...],
) -> list[dict[str, object]]:
    if len(axes) != len(expected_shape):
        raise ValueError("Axis metadata count must match trace dimensionality.")

    normalized_axes: list[dict[str, object]] = []
    for axis_index, axis in enumerate(axes):
        axis_name = str(axis.get("name", "")).strip()
        axis_unit = str(axis.get("unit", "")).strip()
        if not axis_name:
            raise ValueError(f"Axis {axis_index} is missing a name.")
        if "/" in axis_name:
            raise ValueError(f"Axis {axis_name!r} cannot contain '/'.")

        raw_values = axis.get("values")
        if raw_values is None:
            raise ValueError(f"Axis {axis_name!r} requires explicit values for Zarr writes.")
        axis_values = np.asarray(raw_values)
        if axis_values.ndim != 1:
            raise ValueError(f"Axis {axis_name!r} values must be 1D.")
        if int(axis_values.shape[0]) != int(expected_shape[axis_index]):
            raise ValueError(
                f"Axis {axis_name!r} length {int(axis_values.shape[0])} does not match "
                f"trace shape {int(expected_shape[axis_index])} at dim {axis_index}."
            )

        normalized_axes.append(
            {
                "name": axis_name,
                "unit": axis_unit,
                "length": int(axis_values.shape[0]),
                "values": axis_values,
            }
        )
    return normalized_axes


def _normalize_chunk_shape(
    shape: tuple[int, ...],
    chunk_shape: Sequence[int] | None,
) -> list[int]:
    if chunk_shape is None:
        return [int(shape[0]), *[1 for _ in shape[1:]]]

    normalized = [int(dimension) for dimension in chunk_shape]
    if len(normalized) != len(shape):
        raise ValueError("chunk_shape must match trace dimensionality.")
    if any(dimension <= 0 for dimension in normalized):
        raise ValueError("chunk_shape must contain positive integers only.")
    if any(chunk > size for chunk, size in zip(normalized, shape, strict=False)):
        raise ValueError("chunk_shape values cannot exceed the trace shape.")
    return normalized


def _normalize_selection(selection: TraceSelection, *, ndim: int) -> TraceSelection:
    if len(selection) > ndim:
        raise ValueError("Slice selection has more dimensions than the trace shape.")
    return (*selection, *([slice(None)] * (ndim - len(selection))))


def _build_store_key(*, design_id: int, batch_id: int) -> str:
    return f"designs/{int(design_id)}/batches/{int(batch_id)}.zarr"


def _coerce_store_key(
    *,
    backend: TraceStoreBackend,
    raw_store_key: str,
    raw_store_uri: str,
) -> str:
    if raw_store_key:
        return _normalize_store_key(raw_store_key)

    if not raw_store_uri:
        return ""

    if backend == "local_zarr":
        return _infer_local_store_key(raw_store_uri)
    if backend == "s3_zarr":
        return _infer_s3_store_key(raw_store_uri)
    raise ValueError(f"Unsupported TraceStore backend: {backend}")


def _normalize_store_uri(
    *,
    backend: TraceStoreBackend,
    store_key: str,
    raw_store_uri: str,
) -> str:
    if raw_store_uri:
        return raw_store_uri

    binding = get_trace_store_backend_binding(backend=backend)
    return binding.build_store_uri(store_key=store_key)


def _normalize_store_key(store_key: str) -> str:
    normalized = str(PurePosixPath(store_key.replace("\\", "/"))).strip()
    if not normalized or normalized == ".":
        return ""

    segments = [segment for segment in normalized.split("/") if segment and segment != "."]
    if any(segment == ".." for segment in segments):
        raise ValueError("TraceStoreRef.store_key cannot traverse parent directories.")
    return "/".join(segments)


def _infer_local_store_key(store_uri: str) -> str:
    candidate = Path(store_uri)
    trace_store_root = get_trace_store_path()
    if candidate.is_absolute():
        try:
            return candidate.relative_to(trace_store_root).as_posix()
        except ValueError:
            pass

    normalized_uri = store_uri.replace("\\", "/").strip("/")
    for marker in ("/trace_store/", "trace_store/"):
        if marker in normalized_uri:
            return _normalize_store_key(normalized_uri.split(marker, 1)[1])
    return _normalize_store_key(normalized_uri)


def _infer_s3_store_key(store_uri: str) -> str:
    parsed = urlparse(store_uri)
    if parsed.scheme == "s3":
        return _normalize_store_key(parsed.path.lstrip("/"))
    if parsed.scheme == "trace-store":
        backend = parsed.netloc.strip()
        if backend != "s3_zarr":
            raise ValueError(
                "TraceStoreRef.store_uri trace-store backend mismatch; expected s3_zarr."
            )
        return _normalize_store_key(parsed.path.lstrip("/"))
    return _normalize_store_key(store_uri)


def _coerce_int_list(raw_value: object, *, field_name: str) -> list[int]:
    if not isinstance(raw_value, Sequence) or isinstance(raw_value, (str, bytes)):
        raise ValueError(f"TraceStoreRef.{field_name} must be a sequence of integers.")
    return [int(item) for item in raw_value]


def _require_zarr():
    try:
        import zarr
    except ImportError as exc:  # pragma: no cover - exercised only in missing-dependency envs
        raise MissingTraceStoreDependencyError(
            "zarr is required for TraceStore operations. "
            "Install it before using LocalZarrTraceStore."
        ) from exc
    return zarr


__all__ = [
    "TRACE_STORE_PATH",
    "TRACE_STORE_SCHEMA_VERSION",
    "LocalZarrTraceStore",
    "LocalZarrTraceStoreBackend",
    "MissingTraceStoreDependencyError",
    "S3ZarrTraceStoreBackend",
    "TraceAxisMetadata",
    "TraceSelection",
    "TraceSelectionItem",
    "TraceStore",
    "TraceStoreBackend",
    "TraceStoreBackendBinding",
    "TraceStoreRef",
    "TraceStoreRuntimeConfig",
    "TraceWriteResult",
    "coerce_trace_store_ref",
    "get_trace_store_backend_binding",
    "get_trace_store_path",
    "get_trace_store_runtime_config",
    "resolve_trace_store_path",
]
