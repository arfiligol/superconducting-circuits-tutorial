from dataclasses import dataclass
from typing import Literal

from src.app.domain.storage import ResultHandleRef, TracePayloadRef

DatasetStatus = Literal["Ready", "Queued", "Review"]
DatasetVisibilityScope = Literal["private", "workspace"]
DatasetLifecycleState = Literal["active", "archived", "deleted"]
DatasetProfileField = Literal["device_type", "capabilities", "source"]
CompareReadiness = Literal["ready", "inspect_only", "blocked"]
TraceFamily = Literal["s_matrix", "y_matrix", "z_matrix"]
TraceModeGroup = Literal["base", "sideband", "all"]
TraceSourceKind = Literal["circuit_simulation", "layout_simulation", "measurement"]
TraceStageKind = Literal["raw", "preprocess", "postprocess"]


@dataclass(frozen=True)
class DatasetAllowedActions:
    select: bool
    update_profile: bool
    publish: bool
    archive: bool


@dataclass(frozen=True)
class DatasetCatalogRow:
    dataset_id: str
    name: str
    visibility_scope: DatasetVisibilityScope
    lifecycle_state: DatasetLifecycleState
    device_type: str
    updated_at: str
    allowed_actions: DatasetAllowedActions
    family: str
    owner_display_name: str


@dataclass(frozen=True)
class DatasetDetail:
    dataset_id: str
    name: str
    family: str
    owner: str
    owner_user_id: str
    workspace_id: str
    visibility_scope: DatasetVisibilityScope
    lifecycle_state: DatasetLifecycleState
    updated_at: str
    device_type: str
    capabilities: tuple[str, ...]
    source: str
    status: DatasetStatus
    allowed_actions: DatasetAllowedActions


@dataclass(frozen=True)
class DatasetProfileUpdate:
    device_type: str
    capabilities: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class DatasetProfileUpdateResult:
    dataset: DatasetDetail
    updated_fields: tuple[DatasetProfileField, ...]


@dataclass(frozen=True)
class TaggedCoreMetricSummary:
    metric_id: str
    label: str
    source_parameter: str
    designated_metric: str
    tagged_at: str


@dataclass(frozen=True)
class DesignBrowseRow:
    design_id: str
    dataset_id: str
    name: str
    source_coverage: dict[str, int]
    compare_readiness: CompareReadiness
    trace_count: int
    updated_at: str


@dataclass(frozen=True)
class DesignBrowseQuery:
    search: str | None = None


@dataclass(frozen=True)
class TraceMetadataSummary:
    trace_id: str
    dataset_id: str
    design_id: str
    family: TraceFamily
    parameter: str
    representation: str
    trace_mode_group: TraceModeGroup
    source_kind: TraceSourceKind
    stage_kind: TraceStageKind
    provenance_summary: str


@dataclass(frozen=True)
class TraceBrowseQuery:
    search: str | None = None
    family: TraceFamily | None = None
    representation: str | None = None
    source_kind: TraceSourceKind | None = None
    trace_mode_group: TraceModeGroup | None = None


@dataclass(frozen=True)
class TraceAxis:
    name: str
    unit: str
    length: int


@dataclass(frozen=True)
class TraceDetail:
    trace_id: str
    dataset_id: str
    design_id: str
    axes: tuple[TraceAxis, ...]
    preview_payload: dict[str, object]
    payload_ref: TracePayloadRef | None
    result_handles: tuple[ResultHandleRef, ...]
