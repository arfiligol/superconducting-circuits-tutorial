from dataclasses import replace

from sc_core.circuit_definitions import (
    DEFAULT_PREVIEW_ARTIFACTS,
    inspect_circuit_definition_source,
)
from sc_core.circuit_definitions import (
    ValidationNotice as CoreValidationNotice,
)

from src.app.domain.circuit_definitions import (
    CircuitDefinitionDetail,
    CircuitDefinitionDraft,
    CircuitDefinitionSummary,
    CircuitDefinitionUpdate,
    ValidationLevel,
    ValidationNotice,
)
from src.app.domain.datasets import DatasetDetail, DatasetMetadataUpdate, DatasetSummary
from src.app.infrastructure.storage_reference_factory import (
    build_metadata_record_ref,
    build_result_handle_ref,
    build_result_provenance_ref,
    build_trace_payload_ref,
)


class InMemoryRewriteCatalogRepository:
    def __init__(self) -> None:
        self._datasets = {dataset.dataset_id: dataset for dataset in _seed_datasets()}
        self._circuit_definitions = {
            definition.definition_id: definition for definition in _seed_circuit_definitions()
        }
        self._next_definition_id = max(self._circuit_definitions) + 1

    def list_datasets(self) -> list[DatasetSummary]:
        return [
            DatasetSummary(
                dataset_id=dataset.dataset_id,
                name=dataset.name,
                family=dataset.family,
                owner=dataset.owner,
                updated_at=dataset.updated_at,
                device_type=dataset.device_type,
                source=dataset.source,
                samples=dataset.samples,
                status=dataset.status,
                capability_count=len(dataset.capabilities),
                tag_count=len(dataset.tags),
            )
            for dataset in self._datasets.values()
        ]

    def get_dataset(self, dataset_id: str) -> DatasetDetail | None:
        return self._datasets.get(dataset_id)

    def update_dataset_metadata(
        self,
        dataset_id: str,
        update: DatasetMetadataUpdate,
    ) -> DatasetDetail | None:
        dataset = self._datasets.get(dataset_id)
        if dataset is None:
            return None

        updated_dataset = replace(
            dataset,
            device_type=update.device_type,
            capabilities=update.capabilities,
            source=update.source,
        )
        self._datasets[dataset_id] = updated_dataset
        return updated_dataset

    def list_circuit_definitions(self) -> list[CircuitDefinitionSummary]:
        return [
            CircuitDefinitionSummary(
                definition_id=definition.definition_id,
                name=definition.name,
                created_at=definition.created_at,
                element_count=definition.element_count,
                validation_status=_validation_status(definition.validation_notices),
                preview_artifact_count=len(definition.preview_artifacts),
            )
            for definition in self._circuit_definitions.values()
        ]

    def get_circuit_definition(self, definition_id: int) -> CircuitDefinitionDetail | None:
        return self._circuit_definitions.get(definition_id)

    def create_circuit_definition(
        self,
        draft: CircuitDefinitionDraft,
    ) -> CircuitDefinitionDetail:
        definition = _build_circuit_definition_detail(
            definition_id=self._next_definition_id,
            name=draft.name,
            created_at="2026-03-11 23:30:00",
            source_text=draft.source_text,
        )
        self._circuit_definitions[definition.definition_id] = definition
        self._next_definition_id += 1
        return definition

    def update_circuit_definition(
        self,
        definition_id: int,
        update: CircuitDefinitionUpdate,
    ) -> CircuitDefinitionDetail | None:
        definition = self._circuit_definitions.get(definition_id)
        if definition is None:
            return None

        inspection = inspect_circuit_definition_source(update.source_text)

        updated_definition = replace(
            definition,
            name=update.name,
            source_text=update.source_text,
            element_count=inspection.element_count,
            normalized_output=inspection.normalized_output,
            validation_notices=_to_domain_validation_notices(inspection.validation_notices),
        )
        self._circuit_definitions[definition_id] = updated_definition
        return updated_definition

    def delete_circuit_definition(self, definition_id: int) -> bool:
        existing = self._circuit_definitions.pop(definition_id, None)
        return existing is not None


def _build_circuit_definition_detail(
    definition_id: int,
    name: str,
    created_at: str,
    source_text: str,
    *,
    element_count: int | None = None,
) -> CircuitDefinitionDetail:
    inspection = inspect_circuit_definition_source(source_text)
    return CircuitDefinitionDetail(
        definition_id=definition_id,
        name=name,
        created_at=created_at,
        element_count=inspection.element_count if element_count is None else element_count,
        source_text=source_text,
        normalized_output=inspection.normalized_output,
        validation_notices=_to_domain_validation_notices(inspection.validation_notices),
        preview_artifacts=DEFAULT_PREVIEW_ARTIFACTS,
    )


def _to_domain_validation_notices(
    notices: tuple[CoreValidationNotice, ...],
) -> tuple[ValidationNotice, ...]:
    return tuple(ValidationNotice(level=notice.level, message=notice.message) for notice in notices)


def _validation_status(notices: tuple[ValidationNotice, ...]) -> ValidationLevel:
    if any(notice.level == "warning" for notice in notices):
        return "warning"
    return "ok"


def _seed_datasets() -> tuple[DatasetDetail, ...]:
    return (
        DatasetDetail(
            dataset_id="fluxonium-2025-031",
            name="Fluxonium sweep 031",
            family="Fluxonium",
            owner="Device Lab",
            updated_at="2026-02-26 13:40",
            device_type="Unspecified",
            capabilities=(),
            source="inferred",
            samples=184,
            status="Ready",
            tags=("sweet-spot", "multi-tone", "validated"),
            preview_columns=("frequency", "bias", "T1", "fit"),
            preview_rows=(
                ("5.812 GHz", "0.120", "18.4 us", "pass"),
                ("5.824 GHz", "0.126", "17.8 us", "pass"),
                ("5.839 GHz", "0.132", "16.2 us", "review"),
            ),
            artifacts=("raw.h5", "metadata.yaml", "fit-summary.json", "plot-bundle.zip"),
            lineage=(
                "capture/2026-02-25",
                "normalize/v2",
                "fit/transmon-loss",
                "review/device-lab",
            ),
            metadata_record=build_metadata_record_ref(
                "dataset",
                "dataset:fluxonium-2025-031",
                version=3,
            ),
            primary_trace=build_trace_payload_ref(
                payload_role="dataset_primary",
                store_key="datasets/fluxonium-2025-031/trace-batches/88.zarr",
                store_uri="trace_store/datasets/fluxonium-2025-031/trace-batches/88.zarr",
                group_path="trace_batches/88",
                array_path="signals/iq_real",
                dtype="float64",
                shape=(184, 1024),
                chunk_shape=(16, 1024),
            ),
            result_handles=(
                build_result_handle_ref(
                    handle_id="result:fluxonium-2025-031:fit-summary",
                    kind="fit_summary",
                    status="materialized",
                    label="Fluxonium fit summary",
                    metadata_record=build_metadata_record_ref(
                        "result_handle",
                        "result_handle:501",
                        version=2,
                    ),
                    payload_backend="json_artifact",
                    payload_format="json",
                    payload_role="report_artifact",
                    payload_locator="artifacts/fit-summary.json",
                    provenance_task_id=303,
                    provenance=build_result_provenance_ref(
                        source_dataset_id="fluxonium-2025-031",
                        source_task_id=303,
                        trace_batch_record=build_metadata_record_ref(
                            "trace_batch",
                            "trace_batch:88",
                            version=1,
                        ),
                    ),
                ),
                build_result_handle_ref(
                    handle_id="result:fluxonium-2025-031:plot-bundle",
                    kind="plot_bundle",
                    status="materialized",
                    label="Fluxonium plot bundle",
                    metadata_record=build_metadata_record_ref(
                        "result_handle",
                        "result_handle:502",
                        version=1,
                    ),
                    payload_backend="bundle_archive",
                    payload_format="zip",
                    payload_role="bundle_artifact",
                    payload_locator="artifacts/plot-bundle.zip",
                    provenance_task_id=303,
                    provenance=build_result_provenance_ref(
                        source_dataset_id="fluxonium-2025-031",
                        source_task_id=303,
                        trace_batch_record=build_metadata_record_ref(
                            "trace_batch",
                            "trace_batch:88",
                            version=1,
                        ),
                    ),
                ),
            ),
        ),
        DatasetDetail(
            dataset_id="transmon-coupler-014",
            name="Coupler detuning 014",
            family="Transmon",
            owner="Modeling",
            updated_at="2026-02-24 09:15",
            device_type="Transmon",
            capabilities=("cross-resonance",),
            source="imported",
            samples=76,
            status="Review",
            tags=("coupler", "cross-resonance"),
            preview_columns=("bias", "coupling", "chi", "note"),
            preview_rows=(
                ("-0.280", "11.2 MHz", "0.41", "re-fit"),
                ("-0.265", "10.8 MHz", "0.39", "queued"),
            ),
            artifacts=("detuning.csv", "fit-report.md"),
            lineage=("import/legacy", "regrid/v1", "fit/manual"),
            metadata_record=build_metadata_record_ref(
                "dataset",
                "dataset:transmon-coupler-014",
                version=5,
            ),
            primary_trace=build_trace_payload_ref(
                payload_role="dataset_primary",
                store_key="datasets/transmon-coupler-014/analysis-runs/12.zarr",
                store_uri="trace_store/datasets/transmon-coupler-014/analysis-runs/12.zarr",
                group_path="analysis_runs/12",
                array_path="derived/chi_fit",
                dtype="float64",
                shape=(76, 64),
                chunk_shape=(16, 64),
            ),
            result_handles=(
                build_result_handle_ref(
                    handle_id="result:transmon-coupler-014:characterization-report",
                    kind="characterization_report",
                    status="materialized",
                    label="Coupler characterization report",
                    metadata_record=build_metadata_record_ref(
                        "result_handle",
                        "result_handle:612",
                        version=3,
                    ),
                    payload_backend="markdown_artifact",
                    payload_format="markdown",
                    payload_role="report_artifact",
                    payload_locator="artifacts/fit-report.md",
                    provenance_task_id=305,
                    provenance=build_result_provenance_ref(
                        source_dataset_id="transmon-coupler-014",
                        source_task_id=305,
                        analysis_run_record=build_metadata_record_ref(
                            "analysis_run",
                            "analysis_run:12",
                            version=4,
                        ),
                    ),
                ),
            ),
        ),
    )


def _seed_circuit_definitions() -> tuple[CircuitDefinitionDetail, ...]:
    floating_qubit_source = (
        "circuit:\n"
        "  name: fluxonium_reference_a\n"
        "  family: fluxonium\n"
        "  elements:\n"
        "    junction:\n"
        "      ej_ghz: 8.45\n"
        "    shunt_inductor:\n"
        "      el_ghz: 0.42\n"
        "    capacitance:\n"
        "      ec_ghz: 1.22\n"
        "  sweep:\n"
        "    flux_bias: [0.0, 0.5]\n"
        "    temperature_mk: 15\n"
    )
    readout_chain_source = (
        "circuit:\n"
        "  name: fluxonium_readout_chain\n"
        "  family: fluxonium\n"
        "  elements:\n"
        "    readout:\n"
        "      resonator_ghz: 6.81\n"
        "    coupling:\n"
        "      chi_mhz: 2.4\n"
    )
    coupler_demo_source = (
        "circuit:\n"
        "  name: coupler_detuning_demo\n"
        "  family: transmon\n"
        "  elements:\n"
        "    coupler:\n"
        "      g_mhz: 11.2\n"
        "    bus:\n"
        "      resonance_ghz: 7.05\n"
    )
    return (
        _build_circuit_definition_detail(
            definition_id=18,
            name="FloatingQubitWithXYLine",
            created_at="2026-03-08 18:19:42",
            element_count=12,
            source_text=floating_qubit_source,
        ),
        _build_circuit_definition_detail(
            definition_id=12,
            name="FluxoniumReadoutChain",
            created_at="2026-03-05 11:14:03",
            element_count=9,
            source_text=readout_chain_source,
        ),
        _build_circuit_definition_detail(
            definition_id=7,
            name="CouplerDetuningDemo",
            created_at="2026-02-25 09:43:18",
            element_count=8,
            source_text=coupler_demo_source,
        ),
    )
