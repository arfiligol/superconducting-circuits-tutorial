from dataclasses import replace

from src.app.domain.circuit_definitions import (
    CircuitDefinitionDetail,
    CircuitDefinitionDraft,
    CircuitDefinitionSummary,
    CircuitDefinitionUpdate,
    ValidationLevel,
    ValidationNotice,
)
from src.app.domain.datasets import DatasetDetail, DatasetMetadataUpdate, DatasetSummary


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
        definition = CircuitDefinitionDetail(
            definition_id=self._next_definition_id,
            name=draft.name,
            created_at="2026-03-11 23:30:00",
            element_count=_estimate_element_count(draft.source_text),
            source_text=draft.source_text,
            normalized_output=_normalized_output_for(draft.source_text),
            validation_notices=(
                ValidationNotice(level="ok", message="Canonical schema matches rewrite draft v1."),
            ),
            preview_artifacts=(
                "definition.normalized.json",
                "schematic-input.yaml",
                "parameter-bundle.toml",
            ),
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

        updated_definition = replace(
            definition,
            name=update.name,
            source_text=update.source_text,
            element_count=_estimate_element_count(update.source_text),
            normalized_output=_normalized_output_for(update.source_text),
        )
        self._circuit_definitions[definition_id] = updated_definition
        return updated_definition

    def delete_circuit_definition(self, definition_id: int) -> bool:
        existing = self._circuit_definitions.pop(definition_id, None)
        return existing is not None


def _estimate_element_count(source_text: str) -> int:
    return max(1, sum(1 for line in source_text.splitlines() if ":" in line) - 3)


def _normalized_output_for(source_text: str) -> str:
    circuit_name = _extract_scalar(source_text, "name") or "pending_name"
    family = _extract_scalar(source_text, "family") or "pending_family"
    return (
        "{\n"
        f'  "circuit": "{circuit_name}",\n'
        f'  "family": "{family}",\n'
        f'  "elements": {_estimate_element_count(source_text)},\n'
        '  "ports": "pending migration",\n'
        '  "schemdraw_ready": true\n'
        "}"
    )


def _extract_scalar(source_text: str, field_name: str) -> str | None:
    for raw_line in source_text.splitlines():
        line = raw_line.strip()
        if not line.startswith(f"{field_name}:"):
            continue
        _, _, value = line.partition(":")
        cleaned = value.strip()
        if cleaned:
            return cleaned
    return None


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
        ),
    )


def _seed_circuit_definitions() -> tuple[CircuitDefinitionDetail, ...]:
    base_artifacts = (
        "definition.normalized.json",
        "schematic-input.yaml",
        "parameter-bundle.toml",
    )
    base_notices = (
        ValidationNotice(level="ok", message="Canonical schema matches rewrite draft v1."),
        ValidationNotice(level="ok", message="All required element blocks are present."),
        ValidationNotice(
            level="warning",
            message="Port mapping metadata still needs migration from legacy forms.",
        ),
    )
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
        CircuitDefinitionDetail(
            definition_id=18,
            name="FloatingQubitWithXYLine",
            created_at="2026-03-08 18:19:42",
            element_count=12,
            source_text=floating_qubit_source,
            normalized_output=_normalized_output_for(floating_qubit_source),
            validation_notices=base_notices,
            preview_artifacts=base_artifacts,
        ),
        CircuitDefinitionDetail(
            definition_id=12,
            name="FluxoniumReadoutChain",
            created_at="2026-03-05 11:14:03",
            element_count=9,
            source_text=readout_chain_source,
            normalized_output=_normalized_output_for(readout_chain_source),
            validation_notices=base_notices,
            preview_artifacts=base_artifacts,
        ),
        CircuitDefinitionDetail(
            definition_id=7,
            name="CouplerDetuningDemo",
            created_at="2026-02-25 09:43:18",
            element_count=8,
            source_text=coupler_demo_source,
            normalized_output=_normalized_output_for(coupler_demo_source),
            validation_notices=base_notices,
            preview_artifacts=base_artifacts,
        ),
    )
