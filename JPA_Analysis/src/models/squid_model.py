import numpy as np
from typing import Union

def squid_lc_frequency(L_jun: Union[float, np.ndarray], Ls_nH: float, C_pF: float) -> Union[float, np.ndarray]:
    L_sq = L_jun / 2.0
    L_tot_nH = L_sq + Ls_nH
    L_tot_nH = np.maximum(L_tot_nH, 1e-15)
    L_tot_H = L_tot_nH * 1e-9
    C_tot_F = C_pF * 1e-12
    f_Hz = 1 / (2 * np.pi * np.sqrt(L_tot_H * C_tot_F))
    return f_Hz / 1e9
