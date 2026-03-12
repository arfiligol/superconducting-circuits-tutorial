using JosephsonCircuits
using PlotlyJS
using CSV
using DataFrames
# using Plots
# using GLMakie

include("../../src/julia/utils.jl")

pH = 1e-12
fF = 1e-15

@variables Lsec Csec Cc Cr Lr Rleft Rright
N = 100
Ltotal = 13797.5975 * 1e-6 # 14568.656 um
Ls = 0.423594 * pH
Cs = 0.169434 * fF
Δx = Ltotal / N
xc = 5350.10396 * 1e-6 # 5350.10396 um

circuit = Tuple{String,String,String,Num}[]

# Port 1 (Input)
push!(circuit, ("P1", "1", "0", 1)) # Port 1
push!(circuit, ("R50_Left", "1", "0", Rleft)) # 50 Ohm load

# Transmission Line
for i in 1:N
    push!(circuit, ("Lsec$(i)_$(i+1)", string(i), string(i + 1), Lsec))
    push!(circuit, ("Csec$(i+1)", string(i + 1), "0", Csec))
end

# Resonator coupled to the transmission line
k = round(xc / Δx) # Coupling Section index
push!(circuit, ("Cc$(k)_$(N+2)", string(Int(k)), string(N + 2), Cc))
push!(circuit, ("Cr$(N+2)", string(N + 2), "0", Cr))
push!(circuit, ("Lr$(N+2)", string(N + 2), "0", Lr))

# Port 2 (Output)
push!(circuit, ("P2", string(N + 1), "0", 2)) # Port 2
push!(circuit, ("R50_Right", string(N + 1), "0", Rright)) # 50 Ohm load

circuitdefs = Dict(
    Lsec => Δx * Ls,
    Csec => Δx * Cs,
    Rleft => 50.0,
    Rright => 50.0,
    Cc => 10e-15, # Coupling capacitor
    Cr => 5.24599642556709e-13,
    Lr => 2.13287527427329e-9,
)

ws = 2 * pi * (4.7:0.0001:4.75) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time transmission_line = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, circuit, circuitdefs)


freq_GHz = transmission_line.linearized.w ./ (2 * pi * 1e9)
S21 = transmission_line.linearized.S(
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

CSV.write("transmission_line_s21.csv", df)


ili_plot(
    [
        scatter(
            mode="markers",
            x=freq_GHz,
            y=S21_mag,
            name="S21"
        )
    ],
    "CPW Circuit Model Simulation",
    "Frequency (GHz)",
    "S21",
    ""
)

ili_plot(
    [
        scatter(
            mode="markers",
            x=real.(S21),
            y=imag.(S21),
            marker=attr(
                color=freq_GHz,
                colorscale="Plasma",
                colorbar=attr(title="Frequency (GHz)"),
                showscale=true,
                size=6,
            ),
            showlegend=false,
            # name="S21 locus"
        )
    ],
    "CPW Circuit Model Simulation",
    "Re(S21)",
    "Im(S21)",
    ""
)
