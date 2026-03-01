"""Tests for simulation result view helpers."""

from app.pages.simulation import (
    _build_result_bundle_data_records,
    _build_s_parameter_data_records,
    _build_simulation_result_figure,
    _result_metric_options_for_family,
    _result_mode_options,
    _result_port_options,
    _result_trace_options_for_family,
)
from core.simulation.domain.circuit import SimulationResult


def _sample_result() -> SimulationResult:
    return SimulationResult(
        frequencies_ghz=[4.9, 5.0, 5.1],
        s11_real=[0.2, 0.0, -0.2],
        s11_imag=[0.0, 0.1, 0.0],
        port_indices=[1, 2],
        mode_indices=[(0,), (1,)],
        s_parameter_real={
            "S11": [0.2, 0.0, -0.2],
            "S21": [1.5, 1.6, 1.7],
            "S22": [0.1, 0.1, 0.1],
        },
        s_parameter_imag={
            "S11": [0.0, 0.1, 0.0],
            "S21": [0.0, 0.0, 0.0],
            "S22": [0.0, 0.0, 0.0],
        },
        s_parameter_mode_real={
            "om=0|op=1|im=0|ip=1": [0.2, 0.0, -0.2],
            "om=0|op=2|im=0|ip=1": [1.5, 1.6, 1.7],
            "om=1|op=2|im=0|ip=1": [0.9, 1.0, 1.1],
            "om=0|op=2|im=0|ip=2": [0.1, 0.1, 0.1],
        },
        s_parameter_mode_imag={
            "om=0|op=1|im=0|ip=1": [0.0, 0.1, 0.0],
            "om=0|op=2|im=0|ip=1": [0.0, 0.0, 0.0],
            "om=1|op=2|im=0|ip=1": [0.1, 0.0, -0.1],
            "om=0|op=2|im=0|ip=2": [0.0, 0.0, 0.0],
        },
        z_parameter_mode_real={"om=0|op=2|im=0|ip=2": [100.0, 110.0, 120.0]},
        z_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [0.0, 1.0, 2.0]},
        y_parameter_mode_real={"om=0|op=2|im=0|ip=2": [0.01, 0.009, 0.008]},
        y_parameter_mode_imag={"om=0|op=2|im=0|ip=2": [0.0, -0.001, -0.002]},
        qe_parameter_mode={"om=1|op=2|im=0|ip=1": [0.8, 0.82, 0.84]},
        qe_ideal_parameter_mode={"om=1|op=2|im=0|ip=1": [0.9, 0.91, 0.92]},
        cm_parameter_mode={"om=1|op=2": [1.0, 1.0, 1.0]},
    )


def test_result_metric_options_for_family_exposes_multiple_result_families() -> None:
    assert "magnitude_db" in _result_metric_options_for_family("s")
    assert "gain_db" in _result_metric_options_for_family("gain")
    assert "magnitude" in _result_metric_options_for_family("impedance")
    assert "magnitude" in _result_metric_options_for_family("admittance")
    assert "linear" in _result_metric_options_for_family("qe")
    assert "value" in _result_metric_options_for_family("cm")
    assert "trajectory" in _result_metric_options_for_family("complex")


def test_result_trace_options_for_complex_family_supports_s_z_y_traces() -> None:
    trace_options = _result_trace_options_for_family("complex")

    assert trace_options == {
        "s": "S",
        "z": "Z",
        "y": "Y",
    }


def test_result_port_options_follow_result_bundle() -> None:
    assert _result_port_options(_sample_result()) == {1: "1", 2: "2"}


def test_result_mode_options_follow_result_bundle() -> None:
    assert _result_mode_options(_sample_result()) == {
        "0": "Signal (0)",
        "1": "Sideband (1)",
    }


def test_build_simulation_result_figure_builds_impedance_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="impedance",
        metric="real",
        trace="z",
        output_mode=(0,),
        output_port=2,
        input_mode=(0,),
        input_port=2,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "Z22 Real Part"
    assert figure.layout.yaxis.title.text == "Real (Ohm)"
    assert len(figure.data) == 1


def test_build_simulation_result_figure_builds_complex_plane_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="complex",
        metric="trajectory",
        trace="y",
        output_mode=(0,),
        output_port=2,
        input_mode=(0,),
        input_port=2,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "Y22 Complex Plane"
    assert figure.layout.xaxis.title.text == "Real"
    assert figure.layout.yaxis.title.text == "Imaginary"
    assert len(figure.data) == 1


def test_build_simulation_result_figure_builds_selected_s_parameter_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="s",
        metric="magnitude_linear",
        trace="s",
        output_mode=(0,),
        output_port=2,
        input_mode=(0,),
        input_port=1,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "S21 Magnitude"
    assert figure.data[0].name == "S21"


def test_build_simulation_result_figure_builds_sideband_qe_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="qe",
        metric="linear",
        trace="qe",
        output_mode=(1,),
        output_port=2,
        input_mode=(0,),
        input_port=1,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "QE 21 [om=(1,), im=(0,)]"
    assert list(figure.data[0].y) == [0.8, 0.82, 0.84]


def test_build_simulation_result_figure_builds_cm_view() -> None:
    figure = _build_simulation_result_figure(
        result=_sample_result(),
        view_family="cm",
        metric="value",
        trace="cm",
        output_mode=(1,),
        output_port=2,
        input_mode=(1,),
        input_port=2,
        reference_impedance_ohm=50.0,
        dark_mode=True,
    )

    assert figure.layout.title.text == "CM2 [om=(1,)]"
    assert list(figure.data[0].y) == [1.0, 1.0, 1.0]


def test_build_s_parameter_data_records_exports_all_cached_s_traces() -> None:
    records = _build_s_parameter_data_records(dataset_id=7, result=_sample_result())

    summary = {(record.parameter, record.representation): record.values for record in records}

    assert len(records) == 6
    assert summary[("S11", "real")] == [0.2, 0.0, -0.2]
    assert summary[("S21", "imaginary")] == [0.0, 0.0, 0.0]
    assert summary[("S22", "real")] == [0.1, 0.1, 0.1]


def test_build_result_bundle_data_records_exports_mode_bundles() -> None:
    records = _build_result_bundle_data_records(dataset_id=7, result=_sample_result())

    summary = {(record.data_type, record.parameter, record.representation) for record in records}

    assert ("s_params", "S21", "real") in summary
    assert ("s_params", "S21 [om=(1,), im=(0,)]", "imaginary") in summary
    assert ("z_params", "Z22", "real") in summary
    assert ("y_params", "Y22", "imaginary") in summary
    assert ("qe", "QE21 [om=(1,), im=(0,)]", "value") in summary
    assert ("qe_ideal", "QEideal21 [om=(1,), im=(0,)]", "value") in summary
    assert ("commutation", "CM2 [om=(1,)]", "value") in summary
