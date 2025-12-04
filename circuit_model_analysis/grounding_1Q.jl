using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames

include("../utils.jl")
# using GLMakie

nH = 1e-9
GHz = 1e9
fF = 1e-15

# Single Floating Qubit
@variables R_Big C L

single_GQ_circuit = [
    ("P1", "1", "0", 1),
    ("R_P1", "1", "0", R_Big),
    ("C1", "1", "0", C),
    ("L1", "1", "0", L),
]

single_GQ_circuitsdefs = Dict(
    C => 59.25219e-15,
    L => 24.0e-9,
    R_Big => 1e30,
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

@time single_GQ = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, single_GQ_circuit, single_GQ_circuitsdefs; returnZ=true)

freqs = single_GQ.linearized.w / (2 * pi * 1e9)
Z11 = vec(single_GQ.linearized.Z[1, 1, 1, 1, :])
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
    "Single Grounding Qubit Admittance",
    "1 / Ω",
    "Frequency (GHz)",
    "Legend";
    y_range=(-0.1, 1.0),
)
savefig(admittance_plot, "grounding_1Q_admittance.png"; width=1000, height=800, scale=4)

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
    "Single Grounding Qubit Impedance",
    "Ω",
    "Frequency (GHz)",
    "Legend";
)
savefig(impedance_plot, "grounding_1Q_impedance.png"; width=1000, height=800, scale=4)


analytical_fq = 1 / (2π * sqrt(single_GQ_circuitsdefs[C] * single_GQ_circuitsdefs[L]))
println("Analytical frequency: ", analytical_fq / GHz, " GHz")