"""Mathematical models for S-parameter analysis and resonance fitting."""

import numpy as np


def notch_s21(
    f: np.ndarray,
    fr: float,
    Ql: float,
    Qc_real: float,
    Qc_imag: float,
    a: float,
    alpha: float,
    tau: float,
) -> np.ndarray:
    """
    Compute the complex S21 transmission of a notch-type resonator.

    This function uses the standard Closest Pole and Zero Method (CPZM) approximation
    combined with environmental baselines (delay, gain, phase, asymmetry).

    Arguments:
        f: Frequency array (Hz).
        fr: Resonance frequency (Hz).
        Ql: Loaded quality factor.
        Qc_real: Real part of the complex coupling quality factor.
        Qc_imag: Imaginary part of the complex coupling quality factor.
        a: Amplitude scaling factor.
        alpha: Constant phase shift (radians).
        tau: Electrical delay (seconds).

    Returns:
        Complex S21 array.
    """
    # Complex coupling quality factor
    Qc_complex = Qc_real + 1j * Qc_imag

    # Fractional detuning
    x = (f - fr) / fr

    # Environmental baseline: delay + complex gain
    baseline = a * np.exp(1j * alpha) * np.exp(-2j * np.pi * f * tau)

    # Resonance dip
    dip = 1 - (Ql / Qc_complex) / (1 + 2j * Ql * x)

    return baseline * dip


def estimate_notch_initial_guess(f: np.ndarray, s21_complex: np.ndarray) -> dict[str, float]:
    """
    Estimate the initial guess parameters for a notch-type resonator S21 fit.

    This provides a robust starting point for gradient-based optimization algorithms.

    Arguments:
        f: Frequency array (Hz).
        s21_complex: Complex S21 data array.

    Returns:
        Dictionary of initial parameter guesses: fr, Ql, Qc_real, Qc_imag, a, alpha, tau.
    """
    s21_mag = np.abs(s21_complex)
    s21_phase = np.unwrap(np.angle(s21_complex))

    # 1. Estimate resonance frequency (minimum amplitude)
    # Ignore DC components (f <= 0) which can artificially drop to 0 in simulations
    valid_f = f > 0
    if not np.any(valid_f):
        valid_f = np.ones_like(f, dtype=bool)

    min_idx_valid = np.argmin(s21_mag[valid_f])
    fr_guess = float(f[valid_f][min_idx_valid])
    min_mag = s21_mag[valid_f][min_idx_valid]

    # 2. Estimate baselines (using endpoints assuming they are far from resonance)
    # Average amplitude of the first and last few points
    num_bg_points = max(1, len(f) // 20)
    bg_mag_start = np.mean(s21_mag[:num_bg_points])
    bg_mag_end = np.mean(s21_mag[-num_bg_points:])
    a_guess = float(np.mean([bg_mag_start, bg_mag_end]))

    # Estimate phase slope (tau) and offset (alpha) from unwrapped phase endpoints
    phase_start = np.mean(s21_phase[:num_bg_points])
    phase_end = np.mean(s21_phase[-num_bg_points:])
    f_start = np.mean(f[:num_bg_points])
    f_end = np.mean(f[-num_bg_points:])

    df = f_end - f_start
    if df != 0:
        # Phase = -2 * pi * f * tau + alpha
        # Slope = -2 * pi * tau  =>  tau = -Slope / (2 * pi)
        phase_slope = (phase_end - phase_start) / df
        tau_guess = -phase_slope / (2 * np.pi)
        alpha_guess = phase_start - phase_slope * f_start
    else:
        tau_guess = 0.0
        alpha_guess = float(np.mean(s21_phase))

    # 3. Estimate Quality Factors
    # FWHM for Ql: find frequencies where mag approaches sqrt( (min_mag^2 + a_guess^2)/2 )
    # A simple heuristic for notch: width of points roughly 3dB above the minimum
    # (relative to the bottom of the dip)

    # 3dB threshold magnitude
    # For a deep notch, the 3dB point from the baseline is approx a_guess / sqrt(2)
    # However, if it's shallow, a better robust guess is halfway between baseline and minimum (in power)
    threshold_power = (min_mag**2 + a_guess**2) / 2
    threshold_mag = np.sqrt(threshold_power)

    # find indices where mag < threshold_mag
    dip_indices = np.where(s21_mag < threshold_mag)[0]

    if len(dip_indices) > 1:
        f_low = f[dip_indices[0]]
        f_high = f[dip_indices[-1]]
        fwhm = f_high - f_low
        if fwhm == 0:
            fwhm = fr_guess * 1e-4  # fallback narrow bandwidth
    else:
        # Fallback if threshold is not crossed well
        fwhm = fr_guess * 1e-4

    Ql_guess = fr_guess / fwhm

    # Ensure strictly positive values for initial Q guesses to prevent zero-division
    if Ql_guess <= 0:
        Ql_guess = 100.0

    depth = 1.0 - (min_mag / a_guess)
    if depth <= 0:
        depth = 0.01  # avoid division by zero
    Qc_real_guess = Ql_guess / depth

    if Qc_real_guess <= 0:
        Qc_real_guess = Ql_guess * 10.0

    return {
        "fr": fr_guess,
        "Ql": Ql_guess,
        "Qc_real": Qc_real_guess,
        "Qc_imag": 0.0,
        "a": a_guess,
        "alpha": alpha_guess,
        "tau": float(tau_guess),
    }


def fit_notch_s21(
    f: np.ndarray, s21_complex: np.ndarray, initial_guess: dict[str, float] | None = None
) -> dict[str, float]:
    """
    Fits the Complex S21 notch resonator model to data using least squares.
    """
    from scipy.optimize import least_squares

    if initial_guess is None:
        initial_guess = estimate_notch_initial_guess(f, s21_complex)

    # Unpack guess into an array: [fr, Ql, Qc_real, Qc_imag, a, alpha, tau]
    print(f"DEBUG: initial_guess = {initial_guess}")
    p0 = [
        initial_guess["fr"],
        initial_guess["Ql"],
        initial_guess["Qc_real"],
        initial_guess["Qc_imag"],
        initial_guess["a"],
        initial_guess["alpha"],
        initial_guess["tau"],
    ]

    # Define residual function
    # return array of Re/Im flattened since least_squares expects real residuals,
    # or just abs() the complex diff. We'll use abs() for a real-valued absolute residual.
    # Alternatively, concat real and imag parts:
    def residual(p, f_data, s21_data):
        fr, Ql, Qc_real, Qc_imag, a, alpha, tau = p
        s21_model = notch_s21(f_data, fr, Ql, Qc_real, Qc_imag, a, alpha, tau)
        diff = s21_model - s21_data
        # Return a 1D real array of length 2*N (Re and Im stacked) for robust optimization
        return np.concatenate((np.real(diff), np.imag(diff)))

    # Bounds to prevent unphysical regimes
    # fr > 0, Ql > 0, a > 0
    bounds = (
        [0, 0, -np.inf, -np.inf, 0, -np.inf, -np.inf],
        [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
    )

    result = least_squares(residual, p0, args=(f, s21_complex), bounds=bounds, loss="soft_l1")

    if not result.success:
        raise ValueError(f"S21 Fit Failed: {result.message}")

    p_opt = result.x

    # Optional: Calculate Qi
    Ql_opt = p_opt[1]
    Qc_complex_opt = p_opt[2] + 1j * p_opt[3]

    # The actual coupling Q magnitude (often used)
    Qc_opt_mag = abs(Qc_complex_opt)

    # 1/Ql = 1/Qi + Re(1/Qc) is commonly used for asymmetric fits,
    # but the simplest derived scalar Qi uses the magnitude 1/Ql = 1/Qi + 1/|Qc|
    # Or specifically Re(1/Qc) as per some literature. Let's use Re(1/Qc):
    # 1/Qi = 1/Ql - Re(1/Qc)
    re_inv_qc = np.real(1.0 / Qc_complex_opt)
    inv_qi = 1.0 / Ql_opt - re_inv_qc
    qi_opt = 1.0 / inv_qi if inv_qi > 0 else np.inf

    return {
        "fr": p_opt[0],
        "Ql": Ql_opt,
        "Qc_real": p_opt[2],
        "Qc_imag": p_opt[3],
        "Qc_mag": Qc_opt_mag,
        "Qi": qi_opt,
        "a": p_opt[4],
        "alpha": p_opt[5],
        "tau": p_opt[6],
        "cost": result.cost,
    }
