from __future__ import annotations

from __future__ import annotations

import numpy as np


def y11_imaginary(
    L_jun: float | np.ndarray,
    freq_ghz: float | np.ndarray,
    Ls1_nH: float,
    Ls2_nH: float,
    C_pF: float,
) -> float | np.ndarray:
    """
    Imaginary part of the Y11 admittance model:

    Y11(jω) = 1 / (jω(L_sq + Ls1)) + j ω C / (1 - ω^2 Ls2 C)
    """
    l_jun_array = np.asarray(L_jun, dtype=float)
    freq_array = np.asarray(freq_ghz, dtype=float) * 1e9

    l_sq_h = (l_jun_array / 2.0) * 1e-9
    ls1_h = Ls1_nH * 1e-9
    ls2_h = Ls2_nH * 1e-9
    total_inductance = l_sq_h + ls1_h
    capacitance_f = C_pF * 1e-12

    omega = 2.0 * np.pi * freq_array
    omega = np.where(omega == 0.0, 1e-30, omega)

    # Pure inductive branch
    imaginary_inductive = -1.0 / (omega * total_inductance)

    # Resonant branch
    denom = 1.0 - (omega ** 2) * ls2_h * capacitance_f
    denom = np.where(np.abs(denom) < 1e-21, np.sign(denom) * 1e-21, denom)
    imaginary_resonant = (omega * capacitance_f) / denom

    return imaginary_inductive + imaginary_resonant
