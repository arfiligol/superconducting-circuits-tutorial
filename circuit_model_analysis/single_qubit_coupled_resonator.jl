using JosephsonCircuits
using Plots
# using GLMakie

pH = 1e-12
fF = 1e-15

@variables RLeft Cq Lq Cr Lr Cc

circuit = Tuple{String,String,String,Num}[]

# Port 1 (Input)
push!(circuit, ("P1", "1", "0", 1)) # Port 1
push!(circuit, ("R50_Left", "1", "0", Rleft)) # 50 Ohm load

# Grounding Qubit
push!(circuit, ("Cq", "1", "0", Cq))
push!(circuit, ("Lq", "1", "0", Lq))

# Coupler
push!(circuit, ("Cc", "1", "2", Cc))

# Resonator
push!(circuit, ("Cr", "2", "0", Cr))
push!(circuit, ("Lr", "2", "0", Lr))


circuitdefs = Dict(
    Rleft => 50.0,
    Cc => 10e-15, # Coupling capacitor
    Cq => 1e-15,
    Lq => 14.2e-9,
    Cr => 5.24599642556709e-13,
    Lr => 2.13287527427329e-9,
)

ws = 2 * pi * (1:0.0001:5) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time transmission_line = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, circuit, circuitdefs; returnZ=true)

freqs = transmission_line.linearized.w / (2 * pi * 1e9)
Z11 = vec(transmission_line.linearized.Z[1, 1, 1, 1, :])
# 計算實部導納 Re{Y₁₁} = Re{1/Z₁₁}
G11 = real.(1 ./ (Z11))
# 取實部與虛部
R11 = real.(Z11)
X11 = imag.(Z11)

plotlyjs()

plot(
    freqs,
    G11,
    xlabel="Frequency (GHz)",
    ylabel="Re{Y}",
    ylims=(-0.1, 0.1),
    # xlims=(4, 5),
    label="JosephsonCircuits.jl",
)


plot(
    freqs, R11,
    xlabel="Frequency (GHz)", ylabel="Ω",
    label="Re Z₁₁"
)
plot!(
    freqs, X11,
    label="Im Z₁₁"
)
