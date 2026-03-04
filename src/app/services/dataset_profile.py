"""Dataset profile normalization and capability templates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

DATASET_PROFILE_SCHEMA_VERSION = "1.0"

DEVICE_TYPE_UNSPECIFIED = "unspecified"

DATASET_DEVICE_TYPES: tuple[str, ...] = (
    DEVICE_TYPE_UNSPECIFIED,
    "single_junction",
    "squid",
    "traveling_wave",
    "resonator",
    "other",
)

CAPABILITY_Y_PARAMETER = "y_parameter_characterization"
CAPABILITY_S_PARAMETER = "s_parameter_characterization"
CAPABILITY_Y11_FIT = "y11_response_fitting"
CAPABILITY_SQUID_FIT = "squid_characterization"
CAPABILITY_TWPA_GAIN = "traveling_wave_gain"

CAPABILITY_LABELS: dict[str, str] = {
    CAPABILITY_Y_PARAMETER: "Y-parameter Characterization",
    CAPABILITY_S_PARAMETER: "S-parameter Characterization",
    CAPABILITY_Y11_FIT: "Y11 Response Fitting",
    CAPABILITY_SQUID_FIT: "SQUID Characterization",
    CAPABILITY_TWPA_GAIN: "Traveling-wave Gain Characterization",
}

DEVICE_TYPE_CAPABILITY_TEMPLATES: dict[str, tuple[str, ...]] = {
    DEVICE_TYPE_UNSPECIFIED: (),
    "single_junction": (
        CAPABILITY_Y_PARAMETER,
        CAPABILITY_Y11_FIT,
    ),
    "squid": (
        CAPABILITY_Y_PARAMETER,
        CAPABILITY_Y11_FIT,
        CAPABILITY_SQUID_FIT,
    ),
    "traveling_wave": (
        CAPABILITY_S_PARAMETER,
        CAPABILITY_TWPA_GAIN,
    ),
    "resonator": (
        CAPABILITY_S_PARAMETER,
        CAPABILITY_Y_PARAMETER,
    ),
    "other": (),
}

PROFILE_SOURCES: tuple[str, ...] = ("inferred", "template", "manual_override")


def normalize_device_type(raw_value: object) -> str:
    """Normalize dataset profile device_type."""
    normalized = str(raw_value or "").strip().lower()
    if normalized in DATASET_DEVICE_TYPES:
        return normalized
    return DEVICE_TYPE_UNSPECIFIED


def normalize_capabilities(raw_values: object) -> list[str]:
    """Normalize, deduplicate, and sort capability keys."""
    if not isinstance(raw_values, Sequence) or isinstance(raw_values, (str, bytes)):
        return []

    normalized: set[str] = set()
    for raw in raw_values:
        capability = str(raw or "").strip().lower()
        if not capability:
            continue
        normalized.add(capability)
    return sorted(normalized)


def capability_label(capability_key: str) -> str:
    """Resolve a user-facing label for one capability key."""
    return CAPABILITY_LABELS.get(capability_key, capability_key.replace("_", " ").title())


def template_capabilities_for_device_type(device_type: str) -> list[str]:
    """Return template capabilities for one canonical device_type."""
    canonical_device_type = normalize_device_type(device_type)
    template = DEVICE_TYPE_CAPABILITY_TEMPLATES.get(canonical_device_type, ())
    return sorted(template)


def infer_capabilities_from_record_index(
    record_index: Sequence[Mapping[str, object]] | None,
) -> list[str]:
    """Infer baseline capabilities from dataset record metadata only."""
    if not record_index:
        return []

    capabilities: set[str] = set()
    for record in record_index:
        data_type = str(record.get("data_type", "")).strip().lower()
        parameter = str(record.get("parameter", "")).strip().upper()

        if data_type in {"y_parameters", "y_params"}:
            capabilities.add(CAPABILITY_Y_PARAMETER)
            if parameter.startswith("Y11"):
                capabilities.add(CAPABILITY_Y11_FIT)
        elif data_type in {"s_parameters", "s_params"}:
            capabilities.add(CAPABILITY_S_PARAMETER)
    return sorted(capabilities)


def normalize_profile_source(raw_value: object, *, default: str) -> str:
    """Normalize dataset profile source marker."""
    normalized = str(raw_value or "").strip().lower()
    if normalized in PROFILE_SOURCES:
        return normalized
    return default


def normalize_dataset_profile(
    source_meta: Mapping[str, object] | None,
    *,
    record_index: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, Any]:
    """Return one canonical dataset profile with backward-compatible fallback."""
    profile_payload = {}
    if isinstance(source_meta, Mapping):
        profile_raw = source_meta.get("dataset_profile")
        if isinstance(profile_raw, Mapping):
            profile_payload = dict(profile_raw)

    device_type = normalize_device_type(profile_payload.get("device_type"))
    template_capabilities = template_capabilities_for_device_type(device_type)
    inferred_capabilities = infer_capabilities_from_record_index(record_index)
    explicit_capabilities = normalize_capabilities(profile_payload.get("capabilities", []))

    if explicit_capabilities:
        capabilities = explicit_capabilities
        default_source = "manual_override"
    else:
        capabilities = sorted(set(template_capabilities) | set(inferred_capabilities))
        default_source = "template" if template_capabilities else "inferred"

    source = normalize_profile_source(profile_payload.get("source"), default=default_source)
    schema_version = str(
        profile_payload.get("schema_version") or DATASET_PROFILE_SCHEMA_VERSION
    ).strip()
    if not schema_version:
        schema_version = DATASET_PROFILE_SCHEMA_VERSION

    return {
        "schema_version": schema_version,
        "device_type": device_type,
        "capabilities": capabilities,
        "source": source,
    }


def profile_summary_text(profile: Mapping[str, object]) -> str:
    """Build a compact summary text for one normalized profile."""
    device_type = normalize_device_type(profile.get("device_type"))
    capabilities = normalize_capabilities(profile.get("capabilities", []))
    if capabilities:
        capability_text = ", ".join(capability_label(item) for item in capabilities)
    else:
        capability_text = "None"
    source = normalize_profile_source(profile.get("source"), default="inferred")
    return (
        f"Device Type: {device_type} | "
        f"Capabilities: {capability_text} | "
        f"Source: {source}"
    )
