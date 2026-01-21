import numpy as np

from src.models.squid_model import squid_lc_frequency


def test_squid_lc_frequency_scalar():
    """Test frequency calculation with scalar inputs."""
    # Example values: L_jun=0.2nH, Ls=0.1nH, C=10pF
    # L_tot = 0.2/2 + 0.1 = 0.2 nH = 2e-10 H
    # C = 10pF = 1e-11 F
    # f = 1 / (2*pi * sqrt(LC))
    # LC = 2e-21
    # sqrt(LC) ~= 4.472e-11
    # f ~= 1 / (2.81e-10) ~= 3.558 GHz

    L_jun = 0.2
    Ls = 0.1
    C = 10.0

    freq = squid_lc_frequency(L_jun, Ls, C)

    # Expected value calculation
    expected = 1 / (2 * np.pi * np.sqrt((0.2 / 2 + 0.1) * 1e-9 * 10 * 1e-12)) / 1e9

    assert np.isclose(freq, expected, rtol=1e-5)


def test_squid_lc_frequency_array():
    """Test frequency calculation with numpy array inputs."""
    L_jun = np.array([0.2, 0.4])
    Ls = 0.1
    C = 10.0

    freqs = squid_lc_frequency(L_jun, Ls, C)

    assert isinstance(freqs, np.ndarray)
    assert len(freqs) == 2
    assert freqs[0] > freqs[1]  # Higher inductance -> Lower frequency


def test_l_jun_zero_handling():
    """Test that zero or negative inductance doesn't cause division by zero."""
    # If L_jun is 0 and Ls is 0, L_tot is 0 -> sqrt(0) -> div by zero.
    # The function should clamp L_tot.

    freq = squid_lc_frequency(0.0, 0.0, 10.0)
    assert np.isfinite(freq)

    # It should result in a very large frequency (due to 1e-15 clamp)
    # L=1e-15 H (actually 1e-15 nH * 1e-9 = 1e-24 H)
    # This is an implementation detail constraint test
