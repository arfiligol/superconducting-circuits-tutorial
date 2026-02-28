"""Tests for simulation-page harmonic/grid coincidence helpers."""

from app.pages.simulation import (
    _detect_harmonic_grid_coincidences,
    _format_harmonic_grid_hint,
)
from core.simulation.domain.circuit import DriveSourceConfig, FrequencyRange


def test_detect_harmonic_grid_coincidences_hits_2fp_at_endpoint():
    freq_range = FrequencyRange(start_ghz=1.0, stop_ghz=10.0, points=1001)
    sources = [DriveSourceConfig(pump_freq_ghz=5.0, port=1, current_amp=0.0)]

    hits = _detect_harmonic_grid_coincidences(
        freq_range=freq_range,
        sources=sources,
        max_pump_harmonic=20,
    )

    assert (1, 2, 10.0, 1000) in hits


def test_detect_harmonic_grid_coincidences_no_hit_when_pump_shifted():
    freq_range = FrequencyRange(start_ghz=1.0, stop_ghz=10.0, points=1001)
    sources = [DriveSourceConfig(pump_freq_ghz=4.999, port=1, current_amp=0.0)]

    hits = _detect_harmonic_grid_coincidences(
        freq_range=freq_range,
        sources=sources,
        max_pump_harmonic=20,
    )

    assert hits == []


def test_format_harmonic_grid_hint_includes_source_and_harmonic():
    hint = _format_harmonic_grid_hint([(1, 2, 10.0, 1000)])

    assert "S1" in hint
    assert "2*fp=10.000000 GHz" in hint
    assert "sweep index=1000" in hint
