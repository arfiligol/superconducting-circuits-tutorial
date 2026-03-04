"""Tests for dataset profile normalization and capability helpers."""

from app.services.dataset_profile import (
    CAPABILITY_SQUID_FIT,
    CAPABILITY_Y11_FIT,
    CAPABILITY_Y_PARAMETER,
    DEVICE_TYPE_UNSPECIFIED,
    normalize_dataset_profile,
    normalize_device_type,
    profile_summary_text,
    template_capabilities_for_device_type,
)


def test_normalize_device_type_falls_back_to_unspecified() -> None:
    assert normalize_device_type("SQUID") == "squid"
    assert normalize_device_type("unknown-device") == DEVICE_TYPE_UNSPECIFIED


def test_template_capabilities_for_squid_include_squid_fit() -> None:
    capabilities = template_capabilities_for_device_type("squid")
    assert CAPABILITY_Y_PARAMETER in capabilities
    assert CAPABILITY_Y11_FIT in capabilities
    assert CAPABILITY_SQUID_FIT in capabilities


def test_normalize_dataset_profile_prefers_explicit_capabilities() -> None:
    profile = normalize_dataset_profile(
        {
            "dataset_profile": {
                "schema_version": "1.0",
                "device_type": "squid",
                "capabilities": ["squid_characterization", "y_parameter_characterization"],
                "source": "manual_override",
            }
        }
    )

    assert profile["device_type"] == "squid"
    assert profile["capabilities"] == ["squid_characterization", "y_parameter_characterization"]
    assert profile["source"] == "manual_override"


def test_normalize_dataset_profile_infers_from_record_index_when_missing_profile() -> None:
    profile = normalize_dataset_profile(
        source_meta={},
        record_index=[
            {
                "id": 1,
                "data_type": "y_parameters",
                "parameter": "Y11",
                "representation": "imaginary",
            }
        ],
    )

    assert profile["device_type"] == DEVICE_TYPE_UNSPECIFIED
    assert profile["source"] == "inferred"
    assert CAPABILITY_Y_PARAMETER in profile["capabilities"]
    assert CAPABILITY_Y11_FIT in profile["capabilities"]


def test_profile_summary_text_includes_capability_labels() -> None:
    summary = profile_summary_text(
        {
            "device_type": "squid",
            "capabilities": ["squid_characterization", "y11_response_fitting"],
            "source": "template",
        }
    )

    assert "Device Type: squid" in summary
    assert "SQUID Characterization" in summary
    assert "Y11 Response Fitting" in summary
    assert "Source: template" in summary
