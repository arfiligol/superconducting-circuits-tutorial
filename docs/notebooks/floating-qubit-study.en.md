# Floating Qubit Study

!!! note "Research Notebook"
    This page documents exploration and analysis of the Floating Qubit circuit model.

## Background

Floating Qubit is a transmon design that is not directly grounded, capacitively coupled to a readout resonator and XY control lines.

## Model Files

- `circuit_model_analysis/floating_1Q_coupled_XY.jl`
- `circuit_model_analysis/floating_1Q_coupled_Readout.jl`

## Topics to Explore

- [ ] Effect of different coupling strengths on mode frequencies
- [ ] Comparison with HFSS simulation results
- [ ] Applicability conditions for Kron reduction

## Related Resources

- Q3D capacitance matrix: `data/q3d_exports/PF6FQ_C_Matrix.csv`
