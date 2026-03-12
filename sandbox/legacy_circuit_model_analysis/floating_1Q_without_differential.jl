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
    ("Cg1", "2", "1", Cg1),
    ("Cg2", "1", "0", Cg2),
    ("Cq", "2", "0", Cq),
    ("Lq", "2", "0", Lq),
    # Port
    ("P1", "1", "2", 1),
    ("R_P1", "1", "2", R_Big),
]

single_FQ_circuitdefs = Dict(
    R_Big => 1e30,
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

ws = 2 * pi * (0.1:0.001:10) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time single_FQ = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, single_FQ_circuit, single_FQ_circuitdefs; returnZ=true)

freqs = single_FQ.linearized.w / (2 * pi * 1e9)
Z11 = vec(single_FQ.linearized.Z[1, 1, 1, 1, :])
# 計算實部導納 Re{Y₁₁} = Re{1/Z₁₁}
G11 = real.(1 ./ (Z11))
# 取實部與虛部
R11 = real.(Z11)
X11 = imag.(Z11)

admittance_plot = ili_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=G11,
            name="Re Y₁₁",
        )
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
            y=R11,
            name="Re Z₁₁",
        ),
        scatter(
            mode="lines+markers",
            x=freqs,
            y=X11,
            name="Im Z₁₁",
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
