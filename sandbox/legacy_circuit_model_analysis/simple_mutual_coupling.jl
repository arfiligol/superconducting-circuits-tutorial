using JosephsonCircuits
using LinearAlgebra
using Printf
using ModelingToolkit: Num

# ------------------------------------------------------------
# Minimal transformer-style test bench to inspect mutual coupling
# ------------------------------------------------------------
@variables L1 L2 M Rsrc Rload

circuit = Tuple{String,String,String,Num}[
    ("P_src", "1", "0", 1),      # drive port
    ("R_src", "1", "0", Rsrc),
    ("L1", "1", "2", L1),          # primary inductor
    ("P_load", "3", "0", 2),       # measurement port on secondary side
    ("L2", "3", "4", L2),          # secondary inductor
    ("R_load", "4", "0", Rload),
    ("K_12", "L1", "L2", M),       # mutual inductance element
]

# Choose convenient numbers: 50 Ω source/load, K = 0.5
L1_val = 2e-9
L2_val = 3e-9
K_coup = 0.5
M_val = K_coup * sqrt(L1_val * L2_val)

circuitdefs = Dict{Num, Float64}(
    L1 => L1_val,
    L2 => L2_val,
    M => M_val,
    Rsrc => 50.0,
    Rload => 50.0,
)

# Harmonic-balance sweep around 5 GHz
freq = 4.0:0.02:6.0
ws = 2π .* freq .* 1e9
wp = (2π * 5.0e9,)
sources = [(mode=(1,), port=1, current=1.0)]
Npumpharmonics = (1,)
Nmodulationharmonics = (1,)

@time sol = hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics,
    circuit, circuitdefs; sorting=:name, returnZ=true, returnS=true)

# Extract S-parameters: forward gain from port 1 to port 2
freq_GHz = sol.linearized.w ./ (2π * 1e9)
S21 = sol.linearized.S(
    outputmode=(0,), outputport=2,
    inputmode=(0,), inputport=1,
    freqindex=:
)

# Compare against analytic expectation for a lossless transformer
# |V2/V1| ≈ K * sqrt(L2/L1) when both sides are matched
expected_ratio = K_coup * sqrt(L2_val / L1_val)

@printf "Expected |V2/V1| from transformer theory: %.3f\n" expected_ratio

mag = abs.(S21)
peak_mag, idx = findmax(mag)
@printf "Simulated peak |S21|: %.3f at %.3f GHz\n" peak_mag freq_GHz[idx]

println("First few points (GHz, |S21|):")
for n in 1:5
    @printf "  %.3f  %.3f\n" freq_GHz[n] mag[n]
end

# Optional: simple ASCII plot aid
println("\nFrequency sweep summary (every 10th point):")
for n in 1:10:length(freq_GHz)
    @printf "  %.3f GHz  |S21| = %.3f\n" freq_GHz[n] mag[n]
end
