using JosephsonCircuits
using PlotlyJS, CSV, DataFrames

include("../utils.jl")

pF = 1e-12
nH = 1e-9

@variables Cc Cr Lr R50 Rwire

circuit = Tuple{String,String,String,Num}[]

# 兩埠 + 端接
push!(circuit, ("P1", "1", "0", 1))
push!(circuit, ("P2", "2", "0", 2))
push!(circuit, ("Rsrc", "1", "0", R50))   # 左端 50 Ω
push!(circuit, ("Rload", "2", "0", R50))   # 右端 50 Ω

# 理想直通線（把 1–2 切成兩段，節點 3 當掛載點）
push!(circuit, ("RwireL", "1", "3", Rwire))  # 近似短路
push!(circuit, ("RwireR", "3", "2", Rwire))

# 掛載支路：系列 Cc → 節點 4；節點 4 對地為 Lr ∥ Cr
push!(circuit, ("C_c", "3", "4", Cc))
push!(circuit, ("C_r", "4", "0", Cr))
push!(circuit, ("L_r", "4", "0", Lr))

# 參數（示例：~4.76 GHz 的 λ/4 等效 LC）
circuitdefs = Dict(
    R50 => 50.0,
    Rwire => 1e-6,            # 近似直短
    Cc => 50e-15,           # 先用 50 fF，之後掃參
    Cr => 5.24599642556709e-13,   # 你原本的值
    Lr => 2.13287527427329e-9     # 你原本的值
)

# 掃頻與求解
ws = 2π .* (4:0.0002:6) .* 1e9
wp = (2π * 8.001e9,)
sources = [(mode=(1,), port=1, current=0.0)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

sol = hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs)

freq_GHz = sol.linearized.w ./ (2π * 1e9)
S21 = sol.linearized.S(outputmode=(0,), outputport=2, inputmode=(0,), inputport=1, freqindex=:)
S21_mag = abs.(S21)

CSV.write("hang_LC_minimal.csv", DataFrame(frequency_GHz=freq_GHz, S21_mag=S21_mag))

ili_plot([scatter(mode="lines", x=freq_GHz, y=S21_mag, name="|S21|")],
    "Ideal TL + Shunt LC via Series Cc", "Frequency (GHz)", "|S21|", "";
    y_range=(0.0, 1.05))
