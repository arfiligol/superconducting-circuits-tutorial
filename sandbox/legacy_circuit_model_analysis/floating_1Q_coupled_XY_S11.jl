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
@variables R50 C_01 C_02 C_12 Lq C_13 C_23
# @variables R_Big R50 C_01 C_02 C_12 C_13 C_23


circuit = Tuple{String,String,String,Num}[]

# Qubit
push!(circuit, ("C_01", "1", "0", C_01))
push!(circuit, ("C_02", "2", "0", C_02))
push!(circuit, ("C_12", "1", "2", C_12))
push!(circuit, ("Lq", "1", "2", Lq))

# Coupler
push!(circuit, ("C_13", "1", "3", C_13))
push!(circuit, ("C_23", "2", "3", C_23))

# Ports

push!(circuit, ("P_XY", "3", "0", 1))
# R50
push!(circuit, ("R50_XY", "3", "0", R50))

circuitdefs = Dict(
    R50 => 50,
    C_01 => sub[sub.name.=="C_01", :value_F][1],
    C_02 => sub[sub.name.=="C_02", :value_F][1],
    C_12 => sub[sub.name.=="C_12", :value_F][1],
    C_13 => sub[sub.name.=="C_13", :value_F][1],
    C_23 => sub[sub.name.=="C_23", :value_F][1],
    Lq => 12.34e-9,
)

ws = 2 * pi * (1.0:0.001:10.0) * GHz
wp = (2 * pi * 4.3 * GHz,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (1,)
Nmodulationharmonics = (1,)

ws = 2 * pi * (4:0.001:5) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time single_FQ_with_XY = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, circuit, circuitdefs; returnZ=true)

freqs = single_FQ_with_XY.linearized.w / (2 * pi * 1e9)

S11_plot = ili_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=abs2.(single_FQ_with_XY.linearized.S(
                outputmode=(0,),
                outputport=1,
                inputmode=(0,),
                inputport=1,
                freqindex=:
            )))
    ],
    "Single Floating Qubit Differential Mode Input Admittance",
    "Frequency (GHz)",
    "|S11|",
    "Legend";
    y_range=(0.0, 1.0),
)

S11_vals = single_FQ_with_XY.linearized.S(
    outputmode=(0,),
    outputport=1,
    inputmode=(0,),
    inputport=1,
    freqindex=:
)

S11_phase = angle.(S11_vals)  # 單位：radian

S11_phase_plot = ili_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=S11_phase,
        )
    ],
    "Single Floating Qubit XY Port S11 Phase",
    "Frequency (GHz)",
    "Phase(S11) (rad)",
    "Legend";
    # 你可以視情況加上 y_range，例如 y_range=(-π, π)
)
