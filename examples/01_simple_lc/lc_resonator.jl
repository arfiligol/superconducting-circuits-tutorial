# LC 共振器模擬範例
# 對應教學：docs/tutorials/lc-resonator.md

using JosephsonCircuits
using PlotlyJS

# === 單位定義 ===
const nH = 1e-9
const pF = 1e-12
const GHz = 1e9

# === 符號變數 ===
@variables L C R50

# === 電路拓撲 ===
# Port ─── L ─── C ─── GND
#  │
# 50Ω
#  │
# GND

circuit = [
    ("P1", "1", "0", 1),      # Port 1
    ("R50", "1", "0", R50),   # 50Ω 阻抗匹配
    ("L", "1", "2", L),       # 電感
    ("C", "2", "0", C),       # 電容
]

# === 參數值 ===
circuitdefs = Dict(
    L => 10nH,
    C => 1pF,
    R50 => 50,
)

# 計算理論共振頻率
f0_theory = 1 / (2π * sqrt(10nH * 1pF)) / GHz
println("理論共振頻率: $(round(f0_theory, digits=3)) GHz")

# === 模擬設定 ===
ws = 2π * (0.1:0.01:10) * GHz
wp = (2π * 5.0GHz,)
sources = [(mode=(1,), port=1, current=0.0)]
Nmodulationharmonics = (10,)
Npumpharmonics = (20,)

# === 執行模擬 ===
println("開始模擬...")
sol = hbsolve(ws, wp, sources, Nmodulationharmonics, Npumpharmonics, circuit, circuitdefs)
println("模擬完成！")

# === 提取結果 ===
freqs = sol.linearized.w / (2π * GHz)
S11 = sol.linearized.S(
    outputmode=(0,),
    outputport=1,
    inputmode=(0,),
    inputport=1,
    freqindex=:
)

# === 處理相位 ===
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

phase_rad = angle.(S11)
phase_deg = rad2deg.(unwrap_phase(phase_rad))
mag_dB = 20 * log10.(abs.(S11))

# === 繪圖 ===
trace_phase = scatter(
    x=freqs,
    y=phase_deg,
    mode="lines",
    name="S11 Phase"
)

trace_mag = scatter(
    x=freqs,
    y=mag_dB,
    mode="lines",
    name="S11 Magnitude"
)

# 相位圖
p1 = plot(trace_phase, Layout(
    title="LC Resonator - S11 Phase",
    xaxis_title="Frequency (GHz)",
    yaxis_title="Phase (deg)"
))
display(p1)

# 幅度圖
p2 = plot(trace_mag, Layout(
    title="LC Resonator - S11 Magnitude",
    xaxis_title="Frequency (GHz)",
    yaxis_title="Magnitude (dB)"
))
display(p2)
