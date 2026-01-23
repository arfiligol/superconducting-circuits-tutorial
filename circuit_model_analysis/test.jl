using JosephsonCircuits
using PlotlyJS
using LinearAlgebra

# ==========================================
# 1. 物理常數與計算函式
# ==========================================
const h = 6.62607015e-34
const e = 1.60217663e-19
const Phi0 = h / (2 * e) # ~2.067e-15 Wb

# SQUID 電感計算函式
# L_jun_single: 單顆 Junction 的零磁通電感
# phi_norm: 歸一化磁通 (Phi / Phi0)
function get_squid_inductance(L_jun_single, phi_norm)
    # SQUID 有兩顆 JJ 並聯，零磁通時總電感為 L_jun / 2
    L_zero = L_jun_single / 2

    # 避免分母為 0 (Flux = 0.5 時)
    # 加上一個極小值 1e-6 或是限制最大電感值
    denominator = abs(cos(pi * phi_norm))
    return L_zero / max(denominator, 1e-3)
end

# Phase Unwrapping 函式
# 用來處理相位超過 +/- pi 時的驟變問題
function unwrap_phase(phases::AbstractVector)
    unwrapped = copy(phases)
    # 掃描陣列，如果相鄰點差異超過 pi，就加減 2pi 來修正
    for i in 2:length(unwrapped)
        diff = unwrapped[i] - unwrapped[i-1]
        while diff > pi
            unwrapped[i] -= 2 * pi
            diff -= 2 * pi
        end
        while diff < -pi
            unwrapped[i] += 2 * pi
            diff += 2 * pi
        end
    end
    return unwrapped
end

# ==========================================
# 2. 定義電路參數
# ==========================================
nH = 1e-9
pF = 1e-12
R50 = 50.0

# 定義符號變數
@variables C_static L_squid C_shunt L_s_1 L_s_2 R_port

# 電路結構 (保留你的 Topology)
circuit = [
    ("P1", "1", "0", 1),         # Port definition
    ("R_P1", "1", "0", R_port),  # Port Impedance
    # Inductor Branch
    ("L_s_1", "1", "2", L_s_1),
    ("L_squid", "2", "0", L_squid), # 這是我們要根據 Flux 改變的元件
    ("C_shunt", "2", "0", C_shunt),
    # Capacitor Branch
    ("L_s_2", "1", "3", L_s_2),
    ("C_static", "3", "0", C_static),
]

# ==========================================
# 3. 掃描參數設定 (Flux Sweep)
# ==========================================
# 頻率範圍 (根據你的電路，大約在 4-8 GHz 會有反應)
freqs_ghz = range(1.0, 10.0, length=401)
ws = freqs_ghz .* (2 * pi * 1e9)

# Flux Bias 範圍 (-0.5 到 0.5 Phi0)
flux_range = range(-0.5, 0.5, length=101)

# 基底參數 (假設單顆 JJ 的 Lj 為 1.0 nH)
# 你可以調整這個值來改變拱門的頂點頻率
L_jun_base = 1.0 * nH

# 準備 2D 矩陣儲存數據 [Frequency, Flux]
s11_phase_map = zeros(Float64, length(ws), length(flux_range))
s11_mag_map = zeros(Float64, length(ws), length(flux_range))

println("開始模擬 Flux Sweep (Base L_jun = $(L_jun_base/nH) nH)...")

# ==========================================
# 4. 執行模擬迴圈
# ==========================================
for (i, phi) in enumerate(flux_range)

    # 1. 物理層：計算當前 Flux 下的 SQUID 電感
    curr_L_squid = get_squid_inductance(L_jun_base, phi)

    # 2. 更新電路數值字典
    circuitdefs = Dict(
        C_static => 0.885 * pF,
        L_squid => curr_L_squid, # 動態更新這裡
        L_s_1 => 0.001 * nH,
        L_s_2 => 0.001 * nH,
        C_shunt => 2.0 * pF,
        R_port => 50.0
    )

    # 3. 執行模擬 (使用 hblinsolve 做線性小訊號分析即可)
    sol = JosephsonCircuits.hblinsolve(ws, circuit, circuitdefs)

    # 4. 提取 S11
    # sol.S 維度: [OutMode, OutPort, InMode, InPort, Freq]
    s11 = sol.S[1, 1, 1, 1, :]

    # --- 關鍵修改：在存入矩陣前先 Unwrap ---
    raw_phase = angle.(s11)
    unwrapped_phase = unwrap_phase(raw_phase)

    # 存入矩陣 (現在存的是連續相位)
    s11_phase_map[:, i] .= unwrapped_phase
    s11_mag_map[:, i] .= 20 * log10.(abs.(s11))
end

println("模擬完成，開始繪圖...")

# ==========================================
# 5. 繪製 Color Map (Heatmap) 使用 PlotlyJS
# ==========================================

# 繪製 S11 Phase (Unwrapped)
# 因為 Unwrap 後數值範圍變大，我們移除 zmin/zmax 的硬限制，讓顏色自動縮放
trace_phase = heatmap(
    x=flux_range,
    y=freqs_ghz,
    z=s11_phase_map,
    colorscale="Viridis",
    colorbar=attr(title="Phase (rad)"),
    # zmin = -pi, zmax = pi, # 移除限制，因為 Unwrap 後可能超過這個範圍
    hovertemplate="Flux: %{x:.3f} Φ₀<br>Freq: %{y:.3f} GHz<br>Phase: %{z:.3f} rad<extra></extra>"
)

layout_phase = Layout(
    title="JPA S11 Phase vs Flux Bias (Unwrapped Color Map)",
    xaxis=attr(
        title="Flux Bias (Φ/Φ₀)",
        zeroline=false
    ),
    yaxis=attr(
        title="Frequency (GHz)",
        zeroline=false
    ),
    width=800, height=600
)

# 顯示 Phase 圖
p1 = plot(trace_phase, layout_phase)
display(p1)

# ==========================================
# 6. 切片分析 (Slicing Analysis)
# ==========================================
# 設定想要切片的目標值
target_freq_cut = 6.0   # GHz
target_flux_cut = 0.25  # Phi0

println("正在繪製切片圖 (Target Freq: $target_freq_cut GHz, Target Flux: $target_flux_cut Phi0)...")

# --- Cut 1: 固定頻率，看 Phase vs Flux ---
freq_idx = argmin(abs.(freqs_ghz .- target_freq_cut))
actual_freq = freqs_ghz[freq_idx]

# 提取那一列 (Row) 數據 (已經是 Unwrap 的了，直接畫)
phase_flux_slice = s11_phase_map[freq_idx, :]

trace_slice_flux = scatter(
    x=flux_range,
    y=phase_flux_slice,
    mode="lines+markers",
    marker=attr(size=4),
    name="Freq = $(round(actual_freq, digits=3)) GHz",
    line=attr(color="cyan")
)

layout_slice_flux = Layout(
    title="Cut 1: Phase vs Flux Bias (Fixed Freq)",
    xaxis=attr(title="Flux Bias (Φ/Φ₀)"),
    yaxis=attr(title="Unwrapped Phase (rad)"),
    width=800, height=400
)

display(plot(trace_slice_flux, layout_slice_flux))

# --- Cut 2: 固定 Flux，看 Phase vs Frequency ---
flux_idx = argmin(abs.(flux_range .- target_flux_cut))
actual_flux = flux_range[flux_idx]

# 提取那一欄 (Column) 數據 (已經是 Unwrap 的了，直接畫)
phase_freq_slice = s11_phase_map[:, flux_idx]

trace_slice_freq = scatter(
    x=freqs_ghz,
    y=phase_freq_slice,
    mode="lines",
    name="Flux = $(round(actual_flux, digits=3)) Φ₀",
    line=attr(color="orange")
)

layout_slice_freq = Layout(
    title="Cut 2: Phase vs Frequency (Fixed Flux)",
    xaxis=attr(title="Frequency (GHz)"),
    yaxis=attr(title="Unwrapped Phase (rad)"),
    width=800, height=400
)

display(plot(trace_slice_freq, layout_slice_freq))
