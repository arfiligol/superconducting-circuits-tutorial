"""TraceStore abstractions for chunked numeric payload persistence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol, TypedDict, cast, runtime_checkable

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
    store_uri: str
    group_path: str
    array_path: str
    dtype: str
    shape: list[int]
    chunk_shape: list[int]
    schema_version: str


@dataclass(frozen=True)
class TraceWriteResult:
    """Metadata returned after materializing one trace payload."""

    axes: list[TraceAxisMetadata]
    store_ref: TraceStoreRef


@runtime_checkable
class TraceStore(Protocol):
    """Slice-first contract for numeric trace payload storage."""

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


def get_trace_store_path() -> Path:
    """Return the configured local TraceStore root path."""
    TRACE_STORE_PATH.mkdir(parents=True, exist_ok=True)
    return TRACE_STORE_PATH


def coerce_trace_store_ref(ref: Mapping[str, object]) -> TraceStoreRef:
    """Validate and normalize one persisted store-ref mapping."""
    backend = str(ref.get("backend", "")).strip()
    if backend not in {"local_zarr", "s3_zarr"}:
        raise ValueError(f"Unsupported TraceStore backend: {backend or '<missing>'}")

    store_uri = str(ref.get("store_uri", "")).strip()
    group_path = _normalize_group_path(str(ref.get("group_path", "")).strip())
    array_path = str(ref.get("array_path", "")).strip()
    dtype = str(ref.get("dtype", "")).strip()
    schema_version = str(ref.get("schema_version", "")).strip() or TRACE_STORE_SCHEMA_VERSION
    shape = _coerce_int_list(ref.get("shape"), field_name="shape")
    chunk_shape = _coerce_int_list(ref.get("chunk_shape"), field_name="chunk_shape")

    if not store_uri:
        raise ValueError("TraceStoreRef.store_uri is required.")
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
        store_uri=store_uri,
        group_path=group_path,
        array_path=array_path,
        dtype=dtype,
        shape=shape,
        chunk_shape=chunk_shape,
        schema_version=schema_version,
    )


class LocalZarrTraceStore:
    """Local-filesystem TraceStore backed by Zarr."""

    def __init__(self, root_path: Path | None = None):
        self._root_path = Path(root_path) if root_path is not None else get_trace_store_path()
        self._root_path.mkdir(parents=True, exist_ok=True)

    @property
    def root_path(self) -> Path:
        """Expose the resolved local root path for tests and callers."""
        return self._root_path

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
        store_path = self._store_path(design_id=design_id, batch_id=batch_id)

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
                store_uri=self._store_uri_for_path(store_path),
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

    def _store_path(self, *, design_id: int, batch_id: int) -> Path:
        return (
            self.root_path
            / "designs"
            / str(int(design_id))
            / "batches"
            / f"{int(batch_id)}.zarr"
        )

    def _store_uri_for_path(self, store_path: Path) -> str:
        project_root = DATABASE_PATH.parent.parent
        try:
            return str(store_path.relative_to(project_root))
        except ValueError:
            return str(store_path)

    def _resolve_store_path(self, normalized_ref: TraceStoreRef) -> Path:
        if normalized_ref["backend"] != "local_zarr":
            raise NotImplementedError(
                "LocalZarrTraceStore only handles local_zarr refs. "
                "s3_zarr remains contract-safe only."
            )
        store_uri = normalized_ref["store_uri"]
        candidate = Path(store_uri)
        if candidate.is_absolute():
            return candidate
        return DATABASE_PATH.parent.parent / store_uri

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
    "MissingTraceStoreDependencyError",
    "TraceAxisMetadata",
    "TraceSelection",
    "TraceSelectionItem",
    "TraceStore",
    "TraceStoreBackend",
    "TraceStoreRef",
    "TraceWriteResult",
    "coerce_trace_store_ref",
    "get_trace_store_path",
]
