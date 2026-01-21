from __future__ import annotations

from typing import Literal, TypedDict


class ModeFitSeries(TypedDict):
    L_jun: list[float]
    Freq: list[float]


class ModeFitParams(TypedDict):
    Ls_nH: float
    C_eff_pF: float


class ModeFitMetrics(TypedDict):
    RMSE: float


class ModeFitSuccess(TypedDict):
    status: Literal["success"]
    params: ModeFitParams
    metrics: ModeFitMetrics
    raw_data: ModeFitSeries
    fit_curve: ModeFitSeries


class ModeFitFailure(TypedDict):
    status: Literal["failed"]
    reason: str


from typing import TypedDict, Union

ModeFitResult = Union[ModeFitSuccess, ModeFitFailure]


FitResultsByMode = dict[str, ModeFitResult]


class AnalysisEntry(TypedDict):
    filename: str
    fits: FitResultsByMode


class Y11FitParams(TypedDict):
    Ls1_nH: float
    Ls2_nH: float
    C_pF: float


class Y11FitMetrics(TypedDict):
    RMSE: float


class Y11FitSeries(TypedDict):
    freq_ghz: list[float]
    imag_y: list[float]
    L_jun: list[float]


class Y11FitSuccess(TypedDict):
    status: Literal["success"]
    params: Y11FitParams
    metrics: Y11FitMetrics
    raw_data: Y11FitSeries
    fit_curve: Y11FitSeries


class Y11FitFailure(TypedDict):
    status: Literal["failed"]
    reason: str


Y11FitResult = Union[Y11FitSuccess, Y11FitFailure]


__all__ = [
    "AnalysisEntry",
    "FitResultsByMode",
    "ModeFitFailure",
    "ModeFitMetrics",
    "ModeFitParams",
    "ModeFitResult",
    "ModeFitSeries",
    "ModeFitSuccess",
    "Y11FitFailure",
    "Y11FitMetrics",
    "Y11FitParams",
    "Y11FitResult",
    "Y11FitSeries",
    "Y11FitSuccess",
]
