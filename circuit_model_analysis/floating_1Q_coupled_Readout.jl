using LinearAlgebra
using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames

include("../utils.jl")
# using GLMakie

nH = 1e-9
GHz = 1e9
fF = 1e-15

df = CSV.read("/Users/arfiligol/Github/Lab/Quantum-Chip-Design-Julia/circuit_model_analysis/PF6FQ_Q3D_C_Matrix.csv", DataFrame)
qubit = "q0"
sub = df[df.qubit_id.==qubit, :]
sub.value_F = sub[!, "value(fF)"] .* 1e-15


# Single Floating Qubit Coupled To XY Line
@variables R_Big R50 C_01 C_02 C_12 L_12 C_13 C_23 C_r L_r L_03 L_04 K_34
# @variables R_Big R50 C_01 C_02 C_12 C_13 C_23


circuit = Tuple{String,String,String,Num}[]

# Qubit
push!(circuit, ("C_01", "1", "0", C_01))
push!(circuit, ("C_02", "2", "0", C_02))
push!(circuit, ("C_12", "1", "2", C_12))
push!(circuit, ("L_12", "1", "2", L_12))

# Coupler to Readout Resonator
push!(circuit, ("C_13", "1", "3", C_13))
push!(circuit, ("C_23", "2", "3", C_23))

# Resonator
push!(circuit, ("C_r", "3", "0", C_r))
push!(circuit, ("L_r", "3", "0", L_r))
push!(circuit, ("L_03", "3", "0", L_03))

# RTL (Readout Transmission Line)
push!(circuit, ("L_04", "4", "0", L_04))
push!(circuit, ("R_04_1", "4", "0", R50))
push!(circuit, ("R_04_2", "4", "0", R50))

# Coupling of Resonator to RTL
push!(circuit, ("K_34", "L_03", "L_04", K_34))

# Differential Ports
push!(circuit, ("P1", "1", "0", 1))
push!(circuit, ("R_P1", "1", "0", R_Big))
push!(circuit, ("P2", "2", "0", 2))
push!(circuit, ("R_P2", "2", "0", R_Big))
push!(circuit, ("P3", "3", "0", 3))
push!(circuit, ("R_P3", "3", "0", R_Big))
push!(circuit, ("P4", "4", "0", 4))

circuitdefs = Dict(
    R_Big => 1e100,
    R50 => 50,
    C_01 => sub[sub.name.=="C_01", :value_F][1],
    C_02 => sub[sub.name.=="C_02", :value_F][1],
    C_12 => sub[sub.name.=="C_12", :value_F][1],
    C_13 => sub[sub.name.=="C_13", :value_F][1],
    C_23 => sub[sub.name.=="C_23", :value_F][1],
    # C_r => ,
    L12 => 12.34e-9,
)

# Another Circuit wihtout R50 & Lq for capacitance network and effective capacitance extraction
circuit2 = Tuple{String,String,String,Num}[]
# Qubit
push!(circuit2, ("C_01", "1", "0", C_01))
push!(circuit2, ("C_02", "2", "0", C_02))
push!(circuit2, ("C_12", "1", "2", C_12))
# Coupler
push!(circuit2, ("C_13", "1", "3", C_13))
push!(circuit2, ("C_23", "2", "3", C_23))
# Differential Ports
push!(circuit2, ("P1", "1", "0", 1))
push!(circuit2, ("R_P1", "1", "0", R_Big))
push!(circuit2, ("P2", "2", "0", 2))
push!(circuit2, ("R_P2", "2", "0", R_Big))
push!(circuit2, ("P3", "3", "0", 3))
push!(circuit2, ("R50_XY", "3", "0", R_Big))

circuitdefs2 = Dict(
    R_Big => 1e100,
    C_01 => sub[sub.name.=="C_01", :value_F][1],
    C_02 => sub[sub.name.=="C_02", :value_F][1],
    C_12 => sub[sub.name.=="C_12", :value_F][1],
    C_13 => sub[sub.name.=="C_13", :value_F][1],
    C_23 => sub[sub.name.=="C_23", :value_F][1],
)


const Circuit = Vector{Tuple{String,String,String,Number}}

function solve_circuit(
    circuit::Circuit,
    circuitdefs::Dict{String,Number},
    f_start::Real, # GHz
    f_stop::Real, # GHz
    f_step::Real; # GHz
    solver::Function=hbsolve,
)::JosephsonCircuits.HB
    # Define the unit
    GHz = 1e9

    ws = 2 * pi * (f_start:f_step:f_stop) * GHz
    wp = (2 * pi * 4.3 * GHz)
    Ip = 0.0
    sources = [(mode=(1,), port=1, current=Ip)]
    Npumpharmonics = (20,)
    Nmodulationharmonics = (10,)

    return solver(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs; returnZ=true)

end



freqs = single_FQ_with_XY.linearized.w / (2 * pi * 1e9)

Z_mat = Array(single_FQ_with_XY.linearized.Z[1, :, 1, :, :]) # 只取第一個 Mode 的 Z 矩陣
N, _, Nf = size(Z_mat)
Y_mat = similar(Z_mat)    # 同樣型別、同樣尺寸

for k in 1:Nf
    # 先把切片拿成真正的 Matrix
    Zk = Matrix(@view Z_mat[:, :, k])
    # inv!(F) 就会返回 Zk^{-1} 这个 Matrix
    Y_mat[:, :, k] = inv(Zk)
    # ——等价于 Y_mat[:,:,k] = Zk \ I
end

Y11 = vec(Y_mat[1, 1, :]) # 取出 Y₁₁
Y12 = vec(Y_mat[1, 2, :]) # 取出 Y₁₂
Y21 = vec(Y_mat[2, 1, :]) # 取出 Y₂₁
Y22 = vec(Y_mat[2, 2, :]) # 取出 Y₂₂
Y13 = vec(Y_mat[1, 3, :]) # 取出 Y₁₃
Y23 = vec(Y_mat[2, 3, :]) # 取出 Y₂₃
Y31 = vec(Y_mat[3, 1, :]) # 取出 Y₃₁
Y32 = vec(Y_mat[3, 2, :]) # 取出 Y₃₂
Y33 = vec(Y_mat[3, 3, :]) # 取出 Y₃₃

Nf = length(Y11)

# Calculate the weighting of common and differential modes
w_1 = (circuitdefs[C_01] + circuitdefs[C_13])
w_2 = (circuitdefs[C_02] + circuitdefs[C_23])
S = w_1 + w_2
alpha = w_1 / S
beta = w_2 / S

# Do Neumann-Kron reduction to eliminate port 3 (XY line)
# I will directly use the result from handwriting notes
A = Y11 .- ((Y13 .* Y13) ./ Y33)
B = Y22 .- ((Y23 .* Y23) ./ Y33)
C = -(Y12 .- ((Y13 .* Y23) ./ Y33))

Y_m_eff_11 = A .- (2 .* C) .+ B
Y_m_eff_12 = beta .* (A .- C) .- alpha .* (-C .+ B)
Y_m_eff_21 = beta .* (A .- C) .- alpha .* (-C .+ B)
Y_m_eff_22 = beta^2 .* A .+ (2 .* alpha .* beta .* C) .+ alpha^2 .* B


# 準備一個 2×2×Nf 的陣列
Y_m_eff = Array{ComplexF64}(undef, 2, 2, Nf)
for k in 1:Nf
    # Put the values into the 2D array
    Y_m_eff[:, :, k] = [
        Y_m_eff_11[k] Y_m_eff_12[k];
        Y_m_eff_21[k] Y_m_eff_22[k]
    ]
end

Yin_dm = Y_m_eff_22 .- (Y_m_eff_21 .* inv.(Y_m_eff_11) .* Y_m_eff_12)   # Vector{ComplexF64} 長度 Nf
G_dm = real.(Yin_dm) # 損耗

Z_mat2 = Array(single_FQ_no_Lq_R50.linearized.Z[1, :, 1, :, :]) # 只取第一個 Mode 的 Z 矩陣
N2, _, Nf2 = size(Z_mat2)
Y_mat2 = similar(Z_mat2)    # 同樣型別、同樣尺寸
for k in 1:Nf2
    Zk2 = Matrix(@view Z_mat2[:, :, k])
    Y_mat2[:, :, k] = inv(Zk2)
end
Y11_2 = vec(Y_mat2[1, 1, :]) # 取出 Y₁₁
Y12_2 = vec(Y_mat2[1, 2, :]) # 取出 Y₁₂
Y21_2 = vec(Y_mat2[2, 1, :]) # 取出 Y₂₁
Y22_2 = vec(Y_mat2[2, 2, :]) # 取出 Y₂₂
Y13_2 = vec(Y_mat2[1, 3, :]) # 取出 Y₁₃
Y23_2 = vec(Y_mat2[2, 3, :]) # 取出 Y₂₃
Y31_2 = vec(Y_mat2[3, 1, :]) # 取出 Y₃₁
Y32_2 = vec(Y_mat2[3, 2, :]) # 取出 Y₃₂
Y33_2 = vec(Y_mat2[3, 3, :]) # 取出 Y₃₃
Nf2 = length(Y11_2)
# Calculate the weighting of common and differential modes
w_1_2 = (circuitdefs2[C_01] + circuitdefs2[C_13])
w_2_2 = (circuitdefs2[C_02] + circuitdefs2[C_23])
S2 = w_1_2 + w_2_2
alpha2 = w_1_2 / S2
beta2 = w_2_2 / S2
# Do Neumann-Kron reduction to eliminate port 3 (XY line)
# I will directly use the result from handwriting notes
A2 = Y11_2 .- ((Y13_2 .* Y13_2) ./ Y33_2)
B2 = Y22_2 .- ((Y23_2 .* Y23_2) ./ Y33_2)
C2 = -(Y12_2 .- ((Y13_2 .* Y23_2) ./ Y33_2))
Y_m_eff_11_2 = A2 .- (2 .* C2) .+ B2
Y_m_eff_12_2 = beta2 .* (A2 .- C2) .- alpha2 .* (-C2 .+ B2)
Y_m_eff_21_2 = beta2 .* (A2 .- C2) .- alpha2 .* (-C2 .+ B2)
Y_m_eff_22_2 = beta2^2 .* A2 .+ (2 .* alpha2 .* beta2 .* C2) .+ alpha2^2 .* B2
# 準備一個 2×2×Nf 的陣列
Y_m_eff_2 = Array{ComplexF64}(undef, 2, 2, Nf2)
for k in 1:Nf2
    # Put the values into the 2D array
    Y_m_eff_2[:, :, k] = [
        Y_m_eff_11_2[k] Y_m_eff_12_2[k];
        Y_m_eff_21_2[k] Y_m_eff_22_2[k]
    ]
end
Yin_dm_2 = Y_m_eff_22_2 .- (Y_m_eff_21_2 .* inv.(Y_m_eff_11_2) .* Y_m_eff_12_2)   # Vector{ComplexF64} 長度 Nf
Ceff_dm = imag.(Yin_dm_2) ./ (2π .* freqs * GHz) # 等效電容（給你有 ω::Vector） # Only Available when L = 0 (purely capacitance network)

C_eff_plot = ili_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=Ceff_dm,
            name="Ceff_dm",
        ),
    ],
    "Single Floating Qubit Differential Mode Effective Capacitance",
    "C_{eff}",
    "Frequency (GHz)",
    "Capacitance (F)";
)

Y_m_eff_plot = ili_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=imag.(Yin_dm),
            name="Im Yin_dm",
        ),
        scatter(
            mode="lines+markers",
            x=freqs,
            y=real.(Yin_dm),
            name="Re Yin_dm",
        ),
    ],
    "Single Floating Qubit Differential Mode Input Admittance",
    "1 / Ω",
    "Frequency (GHz)",
    "Legend";
)

idx = argmin(abs.(Yin_dm))
qubit_frequency = freqs[idx] # GHz
idx_4_3GHz = argmin(abs.(freqs .- 4.3)) # 找最接近 4.3 GHz 的 index
# println("At 4.3 GHz, Im(Yin_dm) = ", imag.(Yin_dm[idx_4_3GHz]), "F")
# f_near = freqs[idx]
Ceff0 = Ceff_dm[idx]
analytical_differential_mode_effective_c = circuitdefs[C_12] + (circuitdefs[C_01] * circuitdefs[C_02]) / (circuitdefs[C_01] + circuitdefs[C_02]) + (circuitdefs[C_13] * circuitdefs[C_23]) / (circuitdefs[C_13] + circuitdefs[C_23])
Yin0 = Yin_dm[idx]
G0 = real(Yin0)
# G0 = real(Yin_dm[idx_4_3GHz]) # 直接取 4.3 GHz 的 Re(Yin_dm)
if G0 <= 0
    @warn "Re(Y_in) ≤ 0 at f ≈ $qubit_frequency GHz → 無有限 T1（近乎無損或模型需檢查）"
else
    T1 = Ceff0 / G0
    println("f≈$(qubit_frequency) GHz:  Ceff=$(Ceff0) F,  ReY=$(G0) S,  T1=$(T1) s")
    # 可選：也印 Q
    ω0 = 2π * qubit_frequency * 1e9
    Q = ω0 * Ceff0 / G0
    println("Q=$(Q)")
end