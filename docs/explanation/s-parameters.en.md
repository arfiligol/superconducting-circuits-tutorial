# S/Z/Y Parameters

Understanding scattering (S), impedance (Z), and admittance (Y) parameters is fundamental to circuit analysis.

## S Parameters (Scattering Parameters)

S parameters describe power wave reflection and transmission between ports.

### $S_{11}$: Reflection Coefficient

$$S_{11} = \frac{b_1}{a_1}$$

- $|S_{11}| = 0$: Perfect match, no reflection
- $|S_{11}| = 1$: Total reflection

### Phase

The phase of $S_{11}$ undergoes a 180° jump at resonance frequency.

## Z Parameters (Impedance Parameters)

$$V = Z \cdot I$$

The impedance matrix describes the voltage-current relationship.

### In JosephsonCircuits.jl

```julia
sol = hbsolve(...; returnZ=true)
Z = sol.linearized.Z[1, :, 1, :, :]  # Extract Z matrix
```

## Y Parameters (Admittance Parameters)

$$I = Y \cdot V \quad \text{where} \quad Y = Z^{-1}$$

### Calculating Y11

```julia
Z_mat = sol.linearized.Z[1, :, 1, :, :]
Y_mat = inv.(Z_mat)
Y11 = Y_mat[1, 1, :]
```

The imaginary part $\text{Im}(Y_{11})$ crosses zero at resonance frequency.

## Conversion Relationships

| From | To S | To Z | To Y |
|------|------|------|------|
| S | - | $(1+S)(1-S)^{-1} Z_0$ | ... |
| Z | $(Z-Z_0)(Z+Z_0)^{-1}$ | - | $Z^{-1}$ |
| Y | ... | $Y^{-1}$ | - |

## Practical Example

Methods to find resonance frequency:

1. Find phase jump in $\angle S_{11}$
2. Find zero crossing in $\text{Im}(Y_{11}) = 0$
