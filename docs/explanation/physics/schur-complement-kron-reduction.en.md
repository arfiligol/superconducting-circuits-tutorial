---
aliases:
  - Schur Complement and Kron Reduction
  - Network Reduction via Schur Complement
tags:
  - diataxis/explanation
  - audience/team
  - topic/physics
  - topic/simulation
  - node_type/method
status: stable
owner: docs-team
audience: team
scope: Physical meaning, derivation, and project usage boundaries of Kron reduction via Schur complement
version: v0.1.1
last_updated: 2026-03-05
updated_by: docs-team
---

# Schur Complement and Kron Reduction

If you are doing multi-port matrix analysis for superconducting circuits, this question appears quickly:  
"How do I eliminate ports/modes I do not care about while preserving the correct equivalent I-V relation?"  
The core of Kron reduction is the Schur complement.

## Bottom line first

Partition the admittance matrix into keep/drop sets. Under `I_drop = 0` (Neumann boundary), the equivalent admittance is:

```text
Y_eff = Y_kk - Y_kd * (Y_dd)^(-1) * Y_dk
```

- `k`: keep (ports/modes you retain)
- `d`: drop (ports/modes you eliminate)

This expression is exactly the Schur complement, and it is the computational core of Kron reduction.

## Why this is physically correct

Setting `I_drop = 0` means:

- no external current injection on dropped degrees of freedom
- those degrees of freedom still respond passively and feed back to kept variables

So elimination is not hard deletion.  
It is passive-response absorption into an equivalent matrix.  
That is why the result is not just `Y_kk`, but `Y_kk` minus a coupling-feedback term.

## Minimal derivation

Start from block form:

```text
[ I_k ]   [ Y_kk  Y_kd ] [ V_k ]
[ I_d ] = [ Y_dk  Y_dd ] [ V_d ]
```

Apply `I_d = 0`:

```text
0 = Y_dk V_k + Y_dd V_d
=> V_d = -(Y_dd)^(-1) Y_dk V_k
```

Substitute into `I_k`:

```text
I_k = (Y_kk - Y_kd (Y_dd)^(-1) Y_dk) V_k
```

So the equivalent matrix is `Y_eff`.

## Two-stage usage in this project

### 1) Port-space reduction (optional first stage)

Eliminate irrelevant physical ports first (for example environment ports).

### 2) Modal reduction after coordinate transform

Transform basis first (for example `1,2 -> cm,dm`), then eliminate non-target modes (for example `cm`) with the same Schur-complement operator.

!!! important "One reusable kernel"
    Port reduction and modal reduction are mathematically identical; only the basis differs.

## Relation to Floating-Qubit `Y_in`

A common target is differential-mode input admittance:

1. Build transformed matrix containing `dm`
2. Schur-reduce all other degrees of freedom
3. Read single-port equivalent `Y_dm,dm`
4. Use `Re(Y_dm,dm)` for downstream loss/T1 analysis

## Relation to Port Termination Compensation (PTC)

PTC and Kron reduction are different operations:

- PTC: remove selected shunt terminations in `Y` domain (for example `diag(1/R_i)`)
- Kron: eliminate degrees of freedom under explicit boundary conditions

You can apply PTC before Kron, or intentionally keep some port terminations before Kron, depending on analysis intent.

## Scope boundary (current project)

!!! warning "Current implementation is port-level, not nodal-level"
    Current WebUI post-processing works on simulator-returned port-space `Y(ω)`,  
    not a full internal-node (nodal) matrix. Arbitrary internal-node elimination is therefore out of scope.

!!! note "HFSS comparison context"
    For floating-port comparison with HFSS, you typically need:
    1. explicit coordinate transform (with normalization convention)
    2. consistent reference impedance assumptions
    3. explicit PTC port selection

## Common misconceptions

1. **Misconception: Kron reduction is row/column deletion**  
   Incorrect. That drops coupling feedback.
2. **Misconception: one reduction pass is always enough**  
   Not always. Port-space and mode-space reductions are often separate stages.
3. **Misconception: same transform applies directly in S-domain**  
   Be careful. Wave normalization/reference settings matter; Y/Z-domain operations are usually more stable.

## Related

- [Physics Overview](./)
- [Symbol Glossary](./symbol-glossary/)
- [Simulation Result Views](../architecture/circuit-simulation/simulation-result-views/)
- [Floating Qubit Real-Part Admittance Notebook](../../notebooks/floating-qubit-real-part-admittance-extraction/)

## References

1. Kron, G. (1939). *Tensor Analysis of Networks*. John Wiley & Sons.
2. Dorf, R. C., & Svoboda, J. A. (2018). *Introduction to Electric Circuits* (9th ed.). Wiley.
3. Zhang, F. (Ed.). (2005). *The Schur Complement and Its Applications*. Springer.
