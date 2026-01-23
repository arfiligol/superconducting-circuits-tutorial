#!/usr/bin/env python3
"""CLI wrapper for SQUID model fitting."""

import argparse
from typing import NamedTuple

from sc_analysis.application.services.squid_fitting import (
    FitModel,
    analyze_file,
    resolve_component_path,
)
from sc_analysis.infrastructure.visualization.plot_utils import plot_json_results

DEFAULT_COMPONENT_IDS = [
    "PF6FQ_Q0_Readout",
    "PF6FQ_Q0_XY",
]
DEFAULT_MODES_TO_PLOT = ["Mode 1"]
DEFAULT_PLOT_TITLE = "Q0 Mode Fits (by Admittance)"
DEFAULT_FIT_BOUNDS = {
    "Ls_nH": (0.0, None),
    "C_pF": (0.0, None),
}
DEFAULT_FIT_WINDOW = (15.0, 30.0)


class AdmittanceFitArgs(NamedTuple):
    components: list[str]
    modes: list[str] | None
    title: str
    ls_min: float | None
    ls_max: float | None
    c_min: float | None
    c_max: float | None
    fixed_c: float | None
    fit_min: float | None
    fit_max: float | None
    matplotlib: bool


def parse_args() -> AdmittanceFitArgs:
    parser = argparse.ArgumentParser(description="Batch analysis of admittance datasets.")
    parser.add_argument("components", nargs="*", help="Component IDs matching preprocessed JSONs.")
    parser.add_argument("--modes", nargs="+", help="Modes to fit/plot (e.g. 'Mode 1').")
    parser.add_argument("--title", default=DEFAULT_PLOT_TITLE)
    parser.add_argument("--ls-min", type=float)
    parser.add_argument("--ls-max", type=float)
    parser.add_argument("--c-min", type=float)
    parser.add_argument("--c-max", type=float)
    parser.add_argument("--fixed-c", type=float)
    parser.add_argument("--fit-min", type=float, default=DEFAULT_FIT_WINDOW[0])
    parser.add_argument("--fit-max", type=float, default=DEFAULT_FIT_WINDOW[1])
    parser.add_argument("--matplotlib", action="store_true")

    args = parser.parse_args()
    return AdmittanceFitArgs(
        components=args.components,
        modes=args.modes,
        title=args.title,
        ls_min=args.ls_min,
        ls_max=args.ls_max,
        c_min=args.c_min,
        c_max=args.c_max,
        fixed_c=args.fixed_c,
        fit_min=args.fit_min,
        fit_max=args.fit_max,
        matplotlib=args.matplotlib,
    )


def build_bounds(args: AdmittanceFitArgs) -> dict[str, tuple[float | None, float | None]]:
    """Build parameter bounds dictionary from CLI args."""

    def resolve(
        key: str, override_min: float | None, override_max: float | None
    ) -> tuple[float | None, float | None]:
        d_min, d_max = DEFAULT_FIT_BOUNDS[key]
        return (
            override_min if override_min is not None else d_min,
            override_max if override_max is not None else d_max,
        )

    return {
        "Ls_nH": resolve("Ls_nH", args.ls_min, args.ls_max),
        "C_pF": resolve("C_pF", args.c_min, args.c_max),
    }


def main():
    args = parse_args()
    file_list = args.components if args.components else DEFAULT_COMPONENT_IDS
    fit_model = FitModel.FIXED_C if args.fixed_c is not None else FitModel.WITH_LS

    entries = []
    for comp in file_list:
        path = resolve_component_path(comp)
        if not path:
            continue

        entry = analyze_file(
            path,
            args.modes,
            build_bounds(args),
            fit_model,
            args.fixed_c,
            (args.fit_min, args.fit_max),
        )
        if entry:
            entries.append(entry)

    if entries:
        plot_json_results(
            entries,
            target_modes=args.modes or DEFAULT_MODES_TO_PLOT,
            title=args.title,
            use_matplotlib=args.matplotlib,
        )


if __name__ == "__main__":
    main()
