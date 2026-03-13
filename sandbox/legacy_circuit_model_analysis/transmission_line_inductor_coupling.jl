using JosephsonCircuits
using PlotlyJS
using CSV
using DataFrames
# using Plots
# using GLMakie

include("../../src/julia/utils.jl")

pH = 1e-12
fF = 1e-15

@variables Lsec Csec Lsec_series Lsec_mut Cr Lr_series Lr_mut K Rleft Rright
N = 1
Ltotal = 13797.5975 * 1e-6 # 14568.656 um
Ls = 0.423594 * pH
Cs = 0.169434 * fF
Δx = Ltotal / N
xc = 5350.10396 * 1e-6 # 5350.10396 um

circuit = Tuple{String,String,String,Num}[]

# Port 1 (Input)
push!(circuit, ("P1", "1", "0", 1)) # Port 1
push!(circuit, ("R50_Left", "1", "0", Rleft)) # 50 Ohm load

# Transmission Line with mutual inductive coupling section
coupling_index = clamp(Int(round(xc / Δx)), 1, N)
mut_node_tl = N + 2
res_node = N + 3
res_mid_node = N + 4

for i in 1:N
    left = string(i)
    right = string(i + 1)
    if i == coupling_index
        mid = string(mut_node_tl)
        push!(circuit, ("Lsec$(i)_series", left, mid, Lsec_series))
        push!(circuit, ("Lsec$(i)_mut", mid, right, Lsec_mut))
    else
        push!(circuit, ("Lsec$(i)_$(i+1)", left, right, Lsec))
    end
    push!(circuit, ("Csec$(i+1)", right, "0", Csec))
end

# Resonator coupled via mutual inductance
res_node_str = string(res_node)
res_mid_str = string(res_mid_node)
mut_branch_name = "Lsec$(coupling_index)_mut"

push!(circuit, ("Cr$(res_node)", res_node_str, "0", Cr))
push!(circuit, ("Lr_series", res_node_str, res_mid_str, Lr_series))
push!(circuit, ("Lr_mut", res_mid_str, "0", Lr_mut))
push!(circuit, ("K_couple", mut_branch_name, "Lr_mut", K))

# Port 2 (Output)
push!(circuit, ("P2", string(N + 1), "0", 2)) # Port 2
push!(circuit, ("R50_Right", string(N + 1), "0", Rright)) # 50 Ohm load

Lsec_total = Δx * Ls
Lr_total = 2.13287527427329e-9

tl_coupling_fraction = 0.5
res_coupling_fraction = 0.5

Lsec_mut_val = tl_coupling_fraction * Lsec_total
Lsec_series_val = Lsec_total - Lsec_mut_val
Lr_mut_val = res_coupling_fraction * Lr_total
Lr_series_val = Lr_total - Lr_mut_val

circuitdefs = Dict{Num,Float64}(
    Lsec => Lsec_total,
    Csec => Δx * Cs,
    Lsec_series => Lsec_series_val,
    Lsec_mut => Lsec_mut_val,
    Cr => 5.24599642556709e-13,
    Lr_series => Lr_series_val,
    Lr_mut => Lr_mut_val,
    K => 0.99,
    Rleft => 50.0,
    Rright => 50.0,
)

ws = 2 * pi * (4.755:0.0000001:4.76) * 1e9
wp = (2 * pi * 4.75 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (1,)
Nmodulationharmonics = (1,)

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

# ili_plot(
#     [
#         scatter(
#             mode="markers",
#             x=real.(S21),
#             y=imag.(S21),
#             marker=attr(
#                 color=freq_GHz,
#                 colorscale="Plasma",
#                 colorbar=attr(title="Frequency (GHz)"),
#                 showscale=true,
#                 size=6,
#             ),
#             showlegend=false,
#             # name="S21 locus"
#         )
#     ],
#     "CPW Circuit Model Simulation",
#     "Re(S21)",
#     "Im(S21)",
#     ""
# )
