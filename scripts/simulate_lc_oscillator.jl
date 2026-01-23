# scripts/simulate_lc_oscillator.jl

# ==========================================
# LC 振盪器 S11 模擬範例
# ==========================================
# 這個腳本演示如何使用現有的 Framework 模擬一個透過 Cc 耦合到 50 Ohm Port 的 LC 振盪器。
# 我們將觀察 S11 的 Phase (相位) 與 Magnitude (振幅)。

include("../src/JPACircuitModelSim.jl")
using .JPACircuitModelSim
using JosephsonCircuits
using PlotlyJS

# --- Helper Functions ---
function unwrap_phase(phases::AbstractVector{<:Real})
    if isempty(phases)
        return phases
    end
    unwrapped = similar(phases)
    unwrapped[1] = phases[1]
    shift = 0.0
    two_pi = 2π
    for i in 2:length(phases)
        diff = phases[i] - phases[i-1]
        if diff > π
            shift -= two_pi
        elseif diff < -π
            shift += two_pi
        end
        unwrapped[i] = phases[i] + shift
    end
    return unwrapped
end

function find_resonance(freqs, s11_complex)
    # Calculate Phase
    phase_rad = angle.(s11_complex)

    # Unwrap Phase
    phase_unwrapped = unwrap_phase(phase_rad)

    # Calculate Group Delay: -d(Phase)/d(omega)
    # We can approximate derivative with finite difference
    # But since we just want the peak, d(Phase)/df is sufficient (max slope)
    # Note: Resonance is usually where phase change is sharpest.
    # For a reflection notch (undercoupled/critically coupled), slope is steepest.

    # Using central difference for better accuracy
    d_phase = zeros(length(freqs))

    # Handle boundaries
    d_phase[1] = (phase_unwrapped[2] - phase_unwrapped[1]) / (freqs[2] - freqs[1])
    d_phase[end] = (phase_unwrapped[end] - phase_unwrapped[end-1]) / (freqs[end] - freqs[end-1])

    for i in 2:length(freqs)-1
        d_phase[i] = (phase_unwrapped[i+1] - phase_unwrapped[i-1]) / (freqs[i+1] - freqs[i-1])
    end

    # Group Delay is negative of phase slope w.r.t angular frequency
    # Here we just look for the frequency where the change is most negative (steep drop)
    # Typically S11 resonance phase goes from 0 to -360 or similar (lagging).
    # So we look for minimum derivative (Max negative slope).

    min_deriv_val, min_deriv_idx = findmin(d_phase)

    return freqs[min_deriv_idx], phase_unwrapped, d_phase
end

# --- 1. 定義常數 (Define Constants) ---
nH = 1e-9
pF = 1e-12
fF = 1e-15
GHz = 1e9

# --- 2. 定義電路 (Define Circuit) ---
# 電路結構：
# Node 0: Ground
# Node 1: Port, R50, Cc 的一端 (Port 端)
# Node 2: LC Tank, Cc 的另一端 (器件端)

ckt = Circuit()

# Port 1 與 50 Ohm 電阻並聯 (於 Node 1)
# Port("Name", "Node+", "Node-", ImpedanceIndex)
add_component!(ckt, Port("P1", "1", "0", 1))
add_component!(ckt, Resistor("R50", "1", "0", :R50))
add_component!(ckt, Inductor("L_stab", "1", "0", :L_stab)) # Stabilization Inductor

# 耦合電容 Cc (連接 Node 1 與 Node 2)
add_component!(ckt, Capacitor("Cc", "1", "2", :Cc))

# LC Tank (於 Node 2)
add_component!(ckt, Inductor("L_tank", "2", "0", :L_tank))
add_component!(ckt, Capacitor("C_tank", "2", "0", :C_tank))

# --- 3. 定義參數與掃描 (Define Parameters & Sweep) ---
# 設定元件數值
# L = 12 nH, C = 112 fF -> 共振頻率 f0 = 1 / (2*pi*sqrt(LC))
# L = 12e-9, C = 112e-15
# f0 = 1/(2*pi*sqrt(1344e-24)) = 1/(2*pi*36.66e-12) = 1/2.3e-10 ≈ 4.34 GHz
circuit_defs = Dict(
    :R50 => 50.0,
    :L_stab => 1.0, # Large inductor to stabilize Node 1 (Low impedance at DC, High at RF)
    :L_tank => 12.0 * nH,
    :C_tank => 112.0 * fF,
    :Cc => 0.05 * pF # 初始值，稍後會被 sweep 覆蓋
)

# 定義掃描 (Sweep)
Cc_sweep_values = [100, 500, 1000] * fF
sweep = Sweep(:Cc, Cc_sweep_values)

# --- 4. 模擬設定 (Simulation Config) ---
# 頻率掃描範圍
ws = 2 * pi * (0.1:0.001:10) * 1e9

config = SimulationConfig(
    ws=ws,
    wp=(1.0e9,), # One dummy pump frequency
    Ip=0.0,
    Npumpharmonics=(1,), # Need at least 1 harmonic to define basis?
    Nmodulationharmonics=(1,)
)

# --- 5. 執行模擬 (Run Simulation) ---
println("開始模擬 LC Oscillator...")
results = simulate(ckt, sweep, config, circuit_defs)

# --- 6. 分析與繪圖 (Analysis & Plot Results) ---
println("分析共振頻率 (Fitting Phase)...")

# 準備繪圖
p_phase = plot_result(results, type=:phase)
# display(p_phase)

# 遍歷每個 Sweep 點計算共振頻率
# S11 array dimensions: [freq, sweep_param_index]
# results.S11
# results.freqs 是 GHz

sweep_param_name = results.parameter_names[1]
sweep_vals = results.parameter_values[1]

println("\n=== 共振頻率分析結果 ===")
for i in 1:length(sweep_vals)
    val = sweep_vals[i]
    val_str = if abs(val) < 1e-9
        "$(val*1e12) pF"
    elseif abs(val) < 1e-12
        "$(val*1e15) fF"
    else
        "$(val)"
    end

    # 提取該參數下的 S11 數據 (所有頻率)
    # results.S11 is [freq, param_idx]
    s11_slice = results.S11[:, i]

    f0, _, _ = find_resonance(results.freqs, s11_slice)

    println("對於 $sweep_param_name = $val_str, 萃取出的共振頻率 f0 = $(round(f0, digits=4)) GHz")
end
println("========================\n")

println("繪製 S11 Phase...")
display(p_phase)

# println("繪製 S11 Magnitude...")
# p_mag = plot_result(results, type=:magnitude)
# display(p_mag)
