using Symbolics, LinearAlgebra

# ---------- Variables (node fluxes & their 'velocities') ----------
@variables Phi_1 Phi_2 Phi_3            # qubit pads 1,2; XY-line node 3
@variables Phi_1d Phi_2d Phi_3d         # time-derivatives, treated as independent symbols

# ---------- Parameters (capacitors present in this case) ----------
@variables C_01 C_02 C_12 C_13 C_23     # to ground & couplings (0-1, 0-2, 1-2, 1-3, 2-3)

# ---------- Weighted common/diff definition for the qubit pair (1,2) ----------
# Total "to-ground-ish" weights for each qubit pad: include its own C0i, mutual C12, and to-XY C i3
w1 = C_01 + C_12 + C_13
w2 = C_02 + C_12 + C_23

# Treat α, β as independent symbols to avoid heavy rational algebra; we'll substitute later.
@variables α β

# ---------- Mode variables (coordinates) ----------
@variables Phi_cm1 Phi_dm1 Phi_xy       # positions: weighted common of (1,2), diff of (1,2), XY node
@variables Phi_cmd1 Phi_dmd1 Phi_xyd    # their 'velocities'

# ---------- Build linear transforms ψ = M * φ (and same for velocities) ----------
φ = [Phi_1; Phi_2; Phi_3]
φd = [Phi_1d; Phi_2d; Phi_3d]
ψ = [Phi_cm1; Phi_dm1; Phi_xy]
ψd = [Phi_cmd1; Phi_dmd1; Phi_xyd]

# M rows implement:
#   Phi_cm1 = α*Phi_1 + β*Phi_2
#   Phi_dm1 = 1*Phi_1 - 1*Phi_2
#   Phi_xy  = Phi_3
M = [
    α β 0;
    1 -1 0;
    0 0 1
]

# Closed-form inverse using α + β = 1 (holds after substitution α=w1/(w1+w2), β=w2/(w1+w2))
Minv = [
    1 β 0;
    1 -α 0;
    0 0 1
]
# Optional sanity check: M*Minv should be I when α+β=1
# println(Symbolics.simplify.(M * Minv))

φ_from_modes = Symbolics.simplify.(Minv * ψ)
φd_from_modes = Symbolics.simplify.(Minv * ψd)

# Sanity checks: should get back ψ and ψd
ψ_check = Symbolics.simplify.(M * φ_from_modes)
ψd_check = Symbolics.simplify.(M * φd_from_modes)

println("M = ");
println(M);
println("\nMinv = ");
println(Minv);
println("\nφ from modes = ");
println(φ_from_modes);
println("\nφ̇ from modes = ");
println(φd_from_modes);
println("\nBack-check ψ   = ");
println(ψ_check);
println("Back-check ψ̇  = ");
println(ψd_check);

# --- Derive C_node from the Lagrangian via Hessian (no hand-written C) ---
# Kinetic energy (3 floating nodes 1,2,3 with ground 0):
#   T = 1/2 [ C01*v1^2 + C02*v2^2
#             + C12*(v1 - v2)^2 + C13*(v1 - v3)^2 + C23*(v2 - v3)^2 ]
T = 0.5 * (
    C_01 * Phi_1d^2 +
    C_02 * Phi_2d^2 +
    C_12 * (Phi_1d - Phi_2d)^2 +
    C_13 * (Phi_1d - Phi_3d)^2 +
    C_23 * (Phi_2d - Phi_3d)^2
)

# Potential energy U can be added if needed; for extracting C it is not required
U = 0
L = T - U

# C_node = ∂²L / ∂v ∂v  (Hessian w.r.t. [Phi_1d, Phi_2d, Phi_3d])
C_node = Symbolics.hessian(L, [Phi_1d, Phi_2d, Phi_3d])
C_node = Symbolics.simplify.(Symbolics.expand.(C_node))

println("\nC_node (from Hessian, nodes [1,2,3]) =")
println(C_node)

# --- Transform to weighted (cm, dm, xy) mode basis ---
# You defined ψ̇ = M φ̇  ⇒  φ̇ = M^{-1} ψ̇
# Therefore,  T = 1/2 φ̇ᵀ C φ̇ = 1/2 ψ̇ᵀ (M^{-1})ᵀ C M^{-1} ψ̇  ⇒  C_mode = (M^{-1})ᵀ * C_node * M^{-1}
C_mode = Symbolics.expand.(transpose(Minv) * C_node * Minv)
C_mode = Symbolics.simplify.(C_mode; simplify_fractions=false)
# Late substitution of α,β definitions to keep expressions small
C_mode = Symbolics.substitute.(C_mode, Ref(Dict(
    α => w1 / (w1 + w2),
    β => w2 / (w1 + w2)
)))
C_mode = Symbolics.simplify.(C_mode; simplify_fractions=false)

println("\nC_mode = (M^{-1})ᵀ * C_node * M^{-1} =")
println(C_mode)

# Optional LaTeX pretty-print (uncomment in a notebook)
# using Latexify
# latexify(C_node)
# latexify(C_mode)