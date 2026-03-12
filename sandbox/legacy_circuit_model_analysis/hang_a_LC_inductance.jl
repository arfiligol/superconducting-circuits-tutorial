using JosephsonCircuits
using PlotlyJS, CSV, DataFrames

include("../../src/julia/utils.jl")

pF = 1e-12
nH = 1e-9
@variables Lp Lr Lr_cpl Cr k R50 Rwire Rshort
circuit = Tuple{String,String,String,Num}[]

# 兩埠 + 端接（50 Ω）
push!(circuit, ("P1", "1", "0", 1))
push!(circuit, ("P2", "2", "0", 2))
push!(circuit, ("Rsrc", "1", "0", R50))
push!(circuit, ("Rload", "2", "0", R50))

# 主線參與線圈 Lp：接在 1-2, 這裡假設 Lp 極小，幾乎不改變阻抗
push!(circuit, ("L_p", "1", "2", Lp)) # Should be very small nearly zero.

# 諧振器（對地）
push!(circuit, ("C_r", "3", "0", Cr))
push!(circuit, ("L_r", "3", "4", Lr))
push!(circuit, ("L_r_coup", "4", "0", Lr_cpl))

# 互感（注意：K 的參數是「耦合係數 k（無單位）」不是 M）
push!(circuit, ("K_cpl", "L_p", "L_r_coup", k))

M = 1.594074972675781e-10      # 你的 M_eq
k_val = 0.99                       # 你原本想用的 k（數值上很大，但先尊重你的設定）
Lr_val = 2.13287527427329e-9
Cr_val = 5.24599642556709e-13
Lp_val = 50e-12                     # 50 pH：在 5 GHz 時 X_L ≈ j1.57 Ω，影響很小
Lr_cpl_val = (M^2) / (k_val^2 * Lp_val)
Lr_uncpl_val = Lr_val - Lr_cpl_val
@assert Lr_uncpl_val > 0 "Lr_cpl 太大使得 Lr 變成負的；請增大 Lp 或降低 k"

circuitdefs = Dict(
    R50 => 50.0, Rwire => 1e-6, Rshort => 1e-6,
    Lp => Lp_val,                       # 參與線圈先抓 10–100 pH
    k => k_val,                         # 2%：直線 CPW 常見 0.5–5%
    Lr_cpl => Lr_cpl_val,
    Cr => Cr_val,         # 你的值
    Lr => Lr_uncpl_val,          #
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
    "Ideal TL + Shunt LC via Mutual Inductance", "Frequency (GHz)", "|S21|", "";
    y_range=(0.0, 1.05))
