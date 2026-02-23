---
aliases:
  - "Resonance Frequency Extraction via Complex S-Parameters"
tags:
  - diataxis/explanation
  - audience/team
  - sot/true
  - topic/physics
  - topic/simulation
status: provisional
owner: docs-team
audience: team
scope: "Theoretical foundations for fitting notch/hanger-type microwave resonators using complex $S_{21}$ data"
version: v0.1.0
last_updated: 2026-02-23
updated_by: docs-team
---

# How is the Resonance Frequency Extracted from S-Parameters?

In superconducting quantum circuits, we typically deduce critical system parameters—such as the resonance frequency ($f_r$) and quality factor ($Q$)—by measuring the transmission or reflection spectrum of a Microwave Resonator. This Explanation explores how **Notch (Hanger) type resonators** theoretically map to S-parameters and explains why, in engineering practice, fitting using the "Complex $S_{21}$" is far more stable and precise than relying solely on magnitude ($|S_{21}|$) or phase.

---

## Prerequisites

Before reading this page, it is recommended that you have a basic understanding of the following:

*   **Electromagnetics / Circuit Theory**: Transmission Line Theory, Impedance Matching.
*   **Microwave Engineering**: Scattering Parameters ($S$-parameters), specifically $S_{21}$ (Transmission Coefficient).
*   **Signals and Systems**: Pole-Zero Models, and how Time Delay manifests as phase changes in the frequency domain.

---

## Theoretical Model: $S_{21}(f)$ of a Notch-Type Resonator

### Notch (Hanger) Geometry

In a Notch geometry, the resonator is side-coupled to a through line. Microwave signals are injected upstream of the through line, and transmission is measured downstream. When sweeping the frequency, the transmission coefficient $S_{21}$ exhibits a distinct dip (notch) near the resonance frequency $f_r$. If the complex $S_{21}$ is plotted on the IQ plane (the Real-Imaginary plane), it traces out a "resonance circle" ([Probst et al., 2015](#references)).

### Closest Pole and Zero Method (CPZM) Approximation

Constructing an extremely precise full-band model (including the LC resonator, coupling capacitors, transmission lines, and all parasitic effects) yields a mathematical form that is highly complex and difficult to fit.

However, Deng–Otto–Lupascu (2013) demonstrated that under conditions of high $Q$, weak coupling, and a very narrow observation bandwidth (focused solely around $f \approx f_r$), the complete circuit model can be vastly simplified. By locating the "Closest Pole and Zero" to the resonance frequency, we arrive at a highly accurate effective model suitable for fitting, known as **CPZM** ([Deng, Otto, & Lupascu, 2013](#references)).

### $S_{21}$ in Real Environments: Why Consider the Baseline?

Ideally, CPZM perfectly describes a circle. But in reality, the $S_{21}$ we measure (or simulate via full-wave electromagnetic solvers like HFSS) is influenced by the external environment:

*   **Electrical Delay**: The length of the cables or feedlines introduces a time delay $\tau$, which manifests in the frequency domain as a linear phase slope ($e^{-2\pi i f \tau}$).
*   **Complex Gain / Rotation**: Overall attenuation or amplification of the system, combined with a constant phase shift ($a e^{i\alpha}$).
*   **Impedance Mismatch**: Impedance mismatches in peripheral circuits create a linear background and asymmetric resonance shapes (Fano-like asymmetry).

If the fitting model fails to account for these external environmental effects, the extracted $f_r$ and $Q$ will suffer from severe systematic deviations ([Probst et al., 2015](#references)).

---

## Engineering Mapping: The Standard Fit-ready Complex Model

Building upon CPZM and incorporating environmental baselines, the most widely adopted standard fitting model in the superconducting resonator community is ([Baity et al., 2024](#references)):

$$
\tilde S_{21}(f) = a e^{i\alpha} e^{-2\pi i f \tau} \left( 1 - \frac{Q_l/Q_c^\ast}{1 + 2i Q_l x} \right), \quad x = \frac{f - f_r}{f_r}
$$

These physical quantities map to engineering fitting parameters as follows:

*   **$a e^{i\alpha}$**: Complex gain / rotation (Amplitude scaling + Constant phase).
*   **$e^{-2\pi i f \tau}$**: Electrical delay, which is the primary source of the Phase baseline (the phase slope).
*   **$f_r$**: Resonance frequency — this is the parameter we most desire to extract accurately.
*   **$Q_l$**: Loaded Q-factor. In the ideal symmetric case: $1/Q_l = 1/Q_i + 1/Q_c$.
*   **$Q_c^\ast$**: Complex Coupling Q. This is a critical factor in practical fitting; allowing $Q_c$ to be complex (or equivalently defining an "asymmetry parameter") provides the flexibility to absorb Fano resonance asymmetry effects caused by impedance mismatches ([Khalil et al., 2012](#references); [Gao, 2008](#references)).

---

## Why Must We Fit Using "Complex Data (Re/Im)"?

When extracting data from HFSS, although it might seem most intuitive to export magnitude (dB) or phase, both theoretical and practical considerations strongly dictate using "Complex data (Real and Imaginary parts)" to solve the problem:

1.  **The Phase Unwrapping Dilemma**:
    Pure phase values (`ang_rad`) are strictly bounded between $[-\pi, \pi]$. When crossing this boundary, the graph experiences a discontinuous jump. Fitting solely against phase creates a highly non-smooth Loss function (e.g., in least squares optimization) due to these discontinuities, and even minor noise can cause automatic Unwrap algorithms to miscalculate. Using complex (Real/Imaginary) data entirely circumvents this issue.
2.  **The Risk of Delay Slopes Pulling $f_r$**:
    The $e^{-2\pi i f \tau}$ term discussed above manifests primarily as a slope in the phase. If you only search for the lowest point of $|S_{21}|$ or fit against phase without correcting the baseline, the position of $f_r$ can easily be "pulled out of alignment" by this slope. Probst notes that true $S_{21}$ contains environmental effects, which must be **explicitly corrected (Baseline removal) or fitted** within the model.
3.  **Circle Fit Geometric Constraints**:
    On the complex plane (IQ Plane), the data of a notch resonator strictly forms a circle near resonance. The robust fit algorithm proposed by Probst leverages the geometric properties of a circle to denoise, correct offsets, and accurately estimate the diameter. This powerful dimensionality reduction inherently relies on the full complex $S_{21}$ dataset ([Probst et al., 2015](#references)).

---

## Limits and Approximations

*   This model (`CPZM`) is strictly valid only in the immediate vicinity of the resonance frequency (typically within a range of several linewidths added or subtracted from $f_r$). If the fitting range is selected too broadly (e.g., spanning several GHz), the baseline characteristics become non-linear, rendering this simple formula invalid.
*   If the system contains extremely strong coupling (extremely low $Q_c$) such that the resonator mode and bus line coupling are severely distorted, one must revert to full ABCD matrix transmission line models for analysis.

---

## References

1.  Probst, S., Song, F. B., Bushev, P. A., Ustinov, A. V., & Weides, M. (2015). Efficient and robust analysis of complex scattering data under noise in microwave resonators. *Review of Scientific Instruments, 86*(2), 024706. [doi:10.1063/1.4907935](https://doi.org/10.1063/1.4907935) | [arXiv:1410.3365](https://arxiv.org/abs/1410.3365)
2.  Deng, C., Otto, M., & Lupascu, A. (2013). An analysis method for transmission measurements of superconducting resonators with applications to quantum-regime dielectric-loss measurements. *Journal of Applied Physics, 114*(5), 054504. [doi:10.1063/1.4817512](https://doi.org/10.1063/1.4817512) | [arXiv:1304.4533](https://arxiv.org/abs/1304.4533)
3.  Baity, P. G., et al. (2024). Circle fit optimization for resonator quality factor measurements. *Physical Review Research, 6*, 013329. [doi:10.1103/PhysRevResearch.6.013329](https://doi.org/10.1103/PhysRevResearch.6.013329)
4.  Gao, J. (2008). *The Physics of Superconducting Microwave Resonators* (Ph.D. thesis). California Institute of Technology. [CaltechTHESIS](https://thesis.library.caltech.edu/2530/)
5.  Rieger, D., et al. (2023). Fano interference in microwave resonator measurements. *Applied Physics Letters, 122*(6), 062601. [arXiv:2209.03036](https://arxiv.org/abs/2209.03036)
6.  Khalil, M. S., Stoutimore, M. J. A., Wellstood, F. C., & Osborn, K. D. (2012). An analysis method for asymmetric resonator transmission applied to superconducting devices. *Journal of Applied Physics, 111*(5), 054510. [doi:10.1063/1.3692073](https://doi.org/10.1063/1.3692073)
