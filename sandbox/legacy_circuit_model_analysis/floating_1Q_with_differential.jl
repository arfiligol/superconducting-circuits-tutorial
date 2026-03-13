using LinearAlgebra
using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames

include("../../src/julia/utils.jl")
# using GLMakie

nH = 1e-9
GHz = 1e9
fF = 1e-15

# Single Floating Qubit
@variables R_Big Cq Lq Cg1 Cg2

single_FQ_circuit = [
    # Qubit
    ("Cg1", "1", "0", Cg1),
    ("Cg2", "2", "0", Cg2),
    ("Cq", "1", "2", Cq),
    ("Lq", "1", "2", Lq),
    # Port 1
    ("P1", "1", "0", 1),
    ("R_P1", "1", "0", R_Big),
    # Port 2
    ("P2", "2", "0", 2),
    ("R_P2", "2", "0", R_Big),
]

single_FQ_circuitdefs = Dict(
    R_Big => 1e20,
    Cq => 59.25219e-15,
    Lq => 24.0e-9,
    Cg1 => 102.38399e-15,
    Cg2 => 102.33597e-15,
)

ws = 2 * pi * (1.0:0.001:10.0) * GHz
wp = (2 * pi * 4.3 * GHz,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (1,)
Nmodulationharmonics = (1,)

ws = 2 * pi * (1:0.001:10) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time single_FQ = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, single_FQ_circuit, single_FQ_circuitdefs; returnZ=true)

freqs = single_FQ.linearized.w / (2 * pi * 1e9)

Z_mat = Array(single_FQ.linearized.Z[1, :, 1, :, :]) # 只取第一個 Mode 的 Z 矩陣
N, _, Nf = size(Z_mat)
Y_mat = similar(Z_mat)    # 同樣型別、同樣尺寸

for k in 1:Nf
    # 先把切片拿成真正的 Matrix
    Zk = Matrix(@view Z_mat[:, :, k])
    # 做 LU 分解（返回一个 LU 因子对象）
    F = lu(Zk)
    # inv!(F) 就会返回 Zk^{-1} 这个 Matrix
    Y_mat[:, :, k] = LinearAlgebra.inv!(F)
    # ——等价于 Y_mat[:,:,k] = Zk \ I
end

Y11 = vec(Y_mat[1, 1, :]) # 取出 Y₁₁
Y12 = vec(Y_mat[1, 2, :]) # 取出 Y₁₂
Y21 = vec(Y_mat[2, 1, :]) # 取出 Y₂₁
Y22 = vec(Y_mat[2, 2, :]) # 取出 Y₂₂

Nf = length(Y11)

# 準備一個 2×2×Nf 的陣列
Ycm = Array{ComplexF64}(undef, 2, 2, Nf)
for k in 1:Nf
    y11 = Y11[k]
    y12 = Y12[k]
    y21 = Y21[k]
    y22 = Y22[k]

    # 按照混合模式公式組裝
    Ycm[1, 1, k] = 1 / 4 * (4 * (y11 + y21 + y12 + y22))          # =  Y_cc
    Ycm[1, 2, k] = 1 / 4 * (2 * (y11 + y21 - y12 - y22))          # =  Y_cd
    Ycm[2, 1, k] = 1 / 4 * (2 * (y11 - y21 + y12 - y22))          # =  Y_dc
    Ycm[2, 2, k] = 1 / 4 * (y11 - y21 - y12 + y22)       # =  Y_dd
end

Nf = size(Ycm, 3)
Zcm = similar(Ycm)

for k in 1:Nf
    y11 = Ycm[1, 1, k]
    y12 = Ycm[1, 2, k]
    y21 = Ycm[2, 1, k]
    y22 = Ycm[2, 2, k]

    detY = y11 * y22 - y12 * y21
    # 反矩阵公式： (1/det) * [ d  -b; -c  a ]
    Zcm[1, 1, k] = y22 / detY
    Zcm[1, 2, k] = -y12 / detY
    Zcm[2, 1, k] = -y21 / detY
    Zcm[2, 2, k] = y11 / detY
end

Ycc = Ycm[1, 1, :]  # 共模导纳
Ycd = Ycm[1, 2, :]  #
Ydc = Ycm[2, 1, :]  #
Ydd = Ycm[2, 2, :]  # 差模导纳

Zcc = Zcm[1, 1, :]  # 共模阻抗
Zcd = Zcm[1, 2, :]  #
Zdc = Zcm[2, 1, :]  #
Zdd = Zcm[2, 2, :]  # 差模阻抗

admittance_plot = ili_plot(
    [
        # scatter(
        #     mode="lines+markers",
        #     x=freqs,
        #     y=imag.((Y11 .- Y21 .- Y12 .+ Y22) ./ 4),
        #     name="Im Y_DD (Calculated)",
        # ),
        # scatter(
        #     mode="lines+markers",
        #     x=freqs,
        #     y=real.((Y11 .- Y21 .- Y12 .+ Y22) ./ 4),
        #     name="Re Y_DD (Calculated)",
        # ),
        scatter(
            mode="lines+markers",
            x=freqs,
            y=imag.(Ydd),
            name="Im Y_DD",
        ),
        scatter(
            mode="lines+markers",
            x=freqs,
            y=real.(Ydd),
            name="Re Y_DD",
        ),
    ],
    "Single Floating Qubit Admittance",
    "1 / Ω",
    "Frequency (GHz)",
    "Legend";
    y_range=(-0.1, 1.0),
)
# savefig(admittance_plot, "single_floating_qubit.png"; width=1000, height=800, scale=4)

impedance_plot = ili_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=imag.(Zdd),
            name="Im Z_DD",
        ),
        scatter(
            mode="lines+markers",
            x=freqs,
            y=real.(Zdd),
            name="Re Z_DD",
        ),
    ],
    "Single Floating Qubit Impedance",
    "Ω",
    "Frequency (GHz)",
    "Legend";
)

Ceff = single_FQ_circuitdefs[Cq] + (1 / (1 / single_FQ_circuitdefs[Cg1] + 1 / single_FQ_circuitdefs[Cg2]))
println("Ceff = ", Ceff / fF, " fF")
analytical_fq = 1 / (2π * sqrt(single_FQ_circuitdefs[Lq] * Ceff))
println("Analytical Frequency = ", analytical_fq / GHz, " GHz")

omega_q = 2π * analytical_fq
Y_LC = 1im * omega_q * single_FQ_circuitdefs[Cq] + (1 / (1im * omega_q * single_FQ_circuitdefs[Lq]))
analytical_differential_mode_admittance = Y_LC + (1im * omega_q * (single_FQ_circuitdefs[Cg1] + single_FQ_circuitdefs[Cg2])) / 4
println("Analytical Imaginary Part of Differential Mode Admittance at Qubit Frequency= ", imag(analytical_differential_mode_admittance))

f_drive = 4.5 * GHz
println("Drive Frequency = ", f_drive / GHz, " GHz")
omega_drive = 2π * f_drive
Y_LC_drive = 1im * omega_drive * single_FQ_circuitdefs[Cq] + (1 / (1im * omega_drive * single_FQ_circuitdefs[Lq]))
analytical_differential_mode_admittance_drive = Y_LC_drive + (1im * omega_drive * (single_FQ_circuitdefs[Cg1] + single_FQ_circuitdefs[Cg2])) / 4
println("Analytical Imaginary Part of Differential Mode Admittance at Drive Frequency= ", imag(analytical_differential_mode_admittance_drive))
