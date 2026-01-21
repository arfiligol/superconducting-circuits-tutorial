# 單參數掃描範例
# 對應教學：docs/tutorials/parameter-sweep.md

using JosephsonCircuits
using PlotlyJS

# === 單位定義 ===
const nH = 1e-9
const pF = 1e-12
const GHz = 1e9

# === 符號變數 ===
@variables L C R50

# === 電路拓撲 ===
circuit = [
    ("P1", "1", "0", 1),
    ("R50", "1", "0", R50),
    ("L", "1", "2", L),
    ("C", "2", "0", C),
]

# === 基本參數 ===
base_defs = Dict(
    C => 1pF,
    R50 => 50,
)

# === 掃描範圍 ===
L_values = (5:2:15) * nH
println("掃描 L: $(L_values ./ nH) nH")

# === 模擬設定 ===
ws = 2π * (0.1:0.02:10) * GHz  # 稍粗的頻率解析度加快速度
wp = (2π * 5.0GHz,)
sources = [(mode=(1,), port=1, current=0.0)]
Nmodulationharmonics = (10,)
Npumpharmonics = (20,)

# === Phase unwrap 工具 ===
function unwrap_phase(phases)
    unwrapped = similar(phases)
    unwrapped[1] = phases[1]
    shift = 0.0
    for i in 2:length(phases)
        diff = phases[i] - phases[i-1]
        if diff > π
            shift -= 2π
        elseif diff < -π
            shift += 2π
        end
        unwrapped[i] = phases[i] + shift
    end
    return unwrapped
end

# === 執行掃描 ===
traces = AbstractTrace[]

println("開始參數掃描...")
for L_val in L_values
    defs = merge(base_defs, Dict(L => L_val))

    sol = hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, defs)

    freqs = sol.linearized.w / (2π * GHz)
    S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)

    phase_deg = rad2deg.(unwrap_phase(angle.(S11)))

    trace = scatter(
        x=freqs,
        y=phase_deg,
        mode="lines",
        name="L = $(round(L_val/nH, digits=1)) nH"
    )
    push!(traces, trace)

    println("  完成 L = $(round(L_val/nH, digits=1)) nH")
end

println("掃描完成！")

# === 繪圖 ===
p = plot(traces, Layout(
    title="S11 Phase - Inductance Sweep",
    xaxis_title="Frequency (GHz)",
    yaxis_title="Phase (deg)",
    legend=attr(title=attr(text="Inductance"))
))

display(p)
