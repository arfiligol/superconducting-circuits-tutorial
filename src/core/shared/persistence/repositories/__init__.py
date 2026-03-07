"""Repositories for the persistence layer."""

from core.shared.persistence.repositories.analysis_run_repository import AnalysisRunRepository
from core.shared.persistence.repositories.circuit_repository import CircuitRepository
from core.shared.persistence.repositories.contracts import (
    AnalysisRunPersistenceContract,
    AnalysisRunSummary,
    DataRecordCharacterizationContract,
    ResultBundleAnalysisRunSummary,
    ResultBundleCharacterizationContract,
    ResultBundleDatasetSummaryContract,
    ResultBundleSnapshotContract,
    TraceBatchCharacterizationContract,
    TraceBatchDesignSummaryContract,
    TraceBatchSnapshotContract,
    TraceCharacterizationContract,
)
from core.shared.persistence.repositories.data_record_repository import (
    DataRecordRepository,
    TraceRepository,
)
from core.shared.persistence.repositories.dataset_repository import (
    DatasetRepository,
    DesignRepository,
)
from core.shared.persistence.repositories.derived_parameter_repository import (
    DerivedParameterRepository,
)
from core.shared.persistence.repositories.query_objects import TraceIndexPageQuery
from core.shared.persistence.repositories.result_bundle_repository import (
    ResultBundleRepository,
    TraceBatchRepository,
)
from core.shared.persistence.repositories.tag_repository import TagRepository

__all__ = [
    "AnalysisRunPersistenceContract",
    "AnalysisRunRepository",
    "AnalysisRunSummary",
    "CircuitRepository",
    "DataRecordCharacterizationContract",
    "DataRecordRepository",
    "DatasetRepository",
    "DerivedParameterRepository",
    "DesignRepository",
    "ResultBundleAnalysisRunSummary",
    "ResultBundleCharacterizationContract",
    "ResultBundleDatasetSummaryContract",
    "ResultBundleRepository",
    "ResultBundleSnapshotContract",
    "TagRepository",
    "TraceBatchCharacterizationContract",
    "TraceBatchDesignSummaryContract",
    "TraceBatchRepository",
    "TraceBatchSnapshotContract",
    "TraceCharacterizationContract",
    "TraceIndexPageQuery",
    "TraceRepository",
]
