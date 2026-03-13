using JosephsonCircuits
using PlotlyJS
using CSV
using DataFrames

include("../../src/julia/utils.jl")

nH = 1e-9
pH = 1e-12
pF = 1e-12
fF = 1e-15

@variables C01 C02 Cq Lq C13 C23 Cr Lr L40 K45 L57 R_Big R50

circuit = Tuple{String,String,String,Num}[]

# Floating Qubuit
push!(circuit, ("C_01", "0", "1", C01))
push!(circuit, ("C_q", "1", "2", Cq))
push!(circuit, ("C_02", "0", "2", C02))
push!(circuit, ("L_q", "1", "2", Lq))

# Floating Qubit Coupled To Resonator
push!(circuit, ("C_13", "1", "3", C13))
push!(circuit, ("C_23", "2", "3", C23))

# Resonator consider as a LC circuit
push!(circuit, ("C_r", "3", "0", Cr))
push!(circuit, ("L_r", "3", "4", Lr))

# Resonator Coupled To Feedline
push!(circuit, ("L_40", "4", "0", L40))
push!(circuit, ("L_57", "5", "7", L57))
push!(circuit, ("K_45", "L_40", "L_57", K45))

# Feedline
push!(circuit, ("R_56", "5", "6", R50))
push!(circuit, ("R_78", "7", "8", R50))

# Ports on Feedline
push!(circuit, ("P1", "6", "0", 1))
push!(circuit, ("P2", "8", "0", 2))
push!(circuit, ("R_P1", "6", "0", R_Big))
push!(circuit, ("R_P2", "8", "0", R_Big))

L40_val = 629.23542 * pH
L57_val = 5896.6076 * pH
M_val = 41.02256 * pH
# K45_val = M_val / sqrt(L40_val * L57_val)
K45_val = 0.99

circuitdefs = Dict{Num,Float64}(
    C01 => 98.41825 * fF,
    C02 => 101.72561 * fF,
    Cq => 57.89611 * fF,
    Lq => 24.0 * nH,
    C13 => 18.55682 * fF,
    C23 => 1.01835 * fF,
    Cr => 0.41 * pF,
    Lr => 1.66 * nH - L40_val,
    L40 => L40_val,
    L57 => L57_val,
    K45 => K45_val,
    R_Big => 1e9,
    R50 => 50.0,
)

ws = 2 * pi * (4:0.0001:6.8) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time readout_all_in_one = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, circuit, circuitdefs)

freq_GHz = readout_all_in_one.linearized.w ./ (2 * pi * 1e9)
S21 = readout_all_in_one.linearized.S(
    outputmode=(0,),
    outputport=2,
    inputmode=(0,),
    inputport=1,
    freqindex=:
)
S21_mag = abs.(S21)

df = DataFrame(
    frequency_GHz=freq_GHz,
    S21_real=real.(S21),
    S21_imag=imag.(S21),
    S21_mag=S21_mag,
)

CSV.write("readout_all_in_one_s21.csv", df)

ili_plot(
    [
        scatter(
            mode="markers",
            x=freq_GHz,
            y=S21_mag,
            name="S21"
        )
    ],
    "Readout All In One Model Simulation",
    "Frequency (GHz)",
    "|S21|",
    "";
    y_range=(0.0, 1.1),
)
