using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames

include("../utils.jl")

# --- 1. 定義常數與參數 ---
nH = 1e-9
GHz = 1e9
pF = 1e-12
fF = 1e-15

@variables C_static L_squid L_s_1 L_s_2 R50

# 電路結構 (Topology 不變)
LC_circuit = [
    ("P1", "1", "0", 1),
    ("R_P1", "1", "0", R50),
    # Inductor Branch
    ("L_squid", "1", "2", L_squid),
    ("L_s_1", "2", "0", L_s_1),
    # Capacitor Branch
    ("C_static", "1", "3", C_static),
    ("L_s_2", "3", "0", L_s_2)
]

# 模擬設定
ws = 2 * pi * (0.1:0.01:20) * 1e9 # 稍微降低解析度以加快 Sweep 速度，可視需求調回
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)


# 定義 Sweep 範圍
L_jun_sweep_values = (0.1:0.1:1.0) * nH  # 間隔設為 0.2 以免圖太亂

# --- 工具函式 ---
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

# --- 準備容器 ---
# 1. 用於 CSV 輸出的數據容器
all_L_jun = Float64[]
all_freqs = Float64[]
all_angles = Float64[]

# 2. 用於繪圖的 Traces 容器 (存放 Plotly 的 AbstractTrace)
plot_traces = AbstractTrace[]
plot_traces_imY11 = AbstractTrace[]

println("開始執行 Parameter Sweep...")

for L_jun_val in L_jun_sweep_values

    # 計算 Lr
    current_Lr = L_jun_val / 2

    # 更新電路參數
    LC_circuit_defs = Dict(
        C_static => 1.37 * pF,
        L_squid => current_Lr,
        L_s_1 => 0.067 * nH,
        L_s_2 => 0.105 * nH,
        R50 => 50,
    )

    # 執行模擬
    sol = hbsolve(ws, wp, sources, Nmodulationharmonics,
        Npumpharmonics, LC_circuit, LC_circuit_defs; returnZ=true)

    # 提取數據
    freqs = sol.linearized.w / (2 * pi * 1e9)
    S11 = sol.linearized.S(
        outputmode=(0,),
        outputport=1,
        inputmode=(0,),
        inputport=1,
        freqindex=:
    )
    phase_rad = angle.(S11)
    phase_deg = rad2deg.(unwrap_phase(phase_rad))

    # 計算導納矩陣並取出 Im(Y11)
    Z_mat = Array(sol.linearized.Z[1, :, 1, :, :])
    _, _, Nf = size(Z_mat)
    Y_mat = similar(Z_mat)
    for k in 1:Nf
        Zk = Matrix(@view Z_mat[:, :, k])
        Y_mat[:, :, k] = inv(Zk)
    end
    Y11 = vec(Y_mat[1, 1, :])
    imY11 = imag.(Y11)

    # --- A. 處理 CSV 數據 (堆疊) ---
    append!(all_L_jun, fill(L_jun_val / nH, length(freqs)))
    append!(all_freqs, freqs)
    append!(all_angles, phase_deg)

    # --- B. 處理繪圖 (新增 Trace) ---
    # 這裡建立單次模擬的線條
    trace = scatter(
        x=freqs,
        y=phase_deg,
        mode="lines", # 建議用 lines，若點太多 lines+markers 會很雜
        name="$(round(L_jun_val / nH, digits=2)) nH" # Legend 顯示名稱
    )
    push!(plot_traces, trace)

    # Im(Y11) 的曲線
    trace_imY11 = scatter(
        x=freqs,
        y=imY11,
        mode="lines",
        name="$(round(L_jun_val / nH, digits=2)) nH"
    )
    push!(plot_traces_imY11, trace_imY11)
end

println("模擬完成，正在繪圖與輸出...")

# --- 呼叫 ili_plot ---
# 直接將收集好的 plot_traces 陣列傳入
final_plot = ili_plot(
    plot_traces,                        # traces::Vector
    "S11 Phase Sweep (L_jun Variation)", # title
    "Frequency (GHz)",                  # xaxis_title
    "Angle (deg)",                      # yaxis_title
    "L_jun Value";                      # legend_title
    # y_range = (-180, 180),            # 可選參數：固定 Y 軸範圍
)

# 顯示圖表
display(final_plot)

# 顯示 Im(Y11)
imY11_plot = ili_plot(
    plot_traces_imY11,
    "Im(Y11) Sweep (L_jun Variation)",
    "Frequency (GHz)",
    "Im(Y11) (S)",
    "L_jun Value";
    # y_range=(-0.1, 0.1),
)
display(imY11_plot)

# --- 輸出 CSV (同前) ---
df_export = DataFrame(
    "L_jun [nH]" => all_L_jun,
    "Freq [GHz]" => all_freqs,
    "angle(S(1,1))" => all_angles
)
CSV.write("S11_Sweep_Ljun.csv", df_export)
println("CSV 檔案已輸出。")
