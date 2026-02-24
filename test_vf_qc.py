import warnings

import numpy as np

from core.analysis.domain.math.s_parameters import MultiResonanceVectorFitter, notch_s21


def test_extraction():
    f = np.linspace(6.2e9, 6.3e9, 2000)
    # Notch resonance: fr=6.25 GHz, Ql=1000, Qc=1200 => Qi = (1/1000 - 1/1200)^-1 = 6000
    w_r = 2 * np.pi * 6.25e9

    Q_l_target = 1000
    Q_c_target = 1200
    Q_i_target = 1 / (1 / Q_l_target - 1 / Q_c_target)

    # We will test a purely hanger model (tau=0, a=1.0)
    s21 = notch_s21(
        f, fr=6.25e9, Ql=Q_l_target, Qc_real=Q_c_target, Qc_imag=0, a=1.0, alpha=0, tau=0
    )

    fitter = MultiResonanceVectorFitter(f, s21)
    # Filter deprecation warnings from scikit-rf
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = fitter.fit(n_resonators=1, bg_poles=0)

    vf = fitter.vf_engine
    poles = vf.poles
    residues = vf.residues[
        2, :
    ]  # Index 2 corresponds to S21 when flattened (S11=0, S12=1, S21=2, S22=3)

    print(f"Target Ql: {Q_l_target}, Qc: {Q_c_target}, Qi: {Q_i_target:.0f}")

    for i, p in enumerate(poles):
        omega = np.imag(p)
        sigma = -np.real(p)
        if omega <= 0:
            continue

        Q_l = omega / (2 * sigma)
        c = residues[i]

        print(f"\nPole {i}: fr={omega / (2 * np.pi) / 1e9:.6f} GHz, Ql={Q_l:.2f}")
        if np.abs(c) > 0:
            Qc_mag = omega / (2 * np.abs(c))

            inv_Qc = np.real(-2 * c / omega)
            Qc_approx = 1 / inv_Qc if inv_Qc != 0 else float("inf")

            # Note: For our formula S21 = 1 - (Ql/Qc)/(1+2j Ql dw/wr)
            # 1/Qc = -2 Re(c) / wr

            inv_Qi = (1 / Q_l) - inv_Qc
            Qi_approx = 1 / inv_Qi if inv_Qi != 0 else float("inf")

            print(f"  c = {c:.3e}")
            print(f"  Extracted Qc_mag = {Qc_mag:.2f}")
            print(f"  Extracted Qc_real= {Qc_approx:.2f}")
            print(f"  Extracted Qi     = {Qi_approx:.2f}")


test_extraction()
