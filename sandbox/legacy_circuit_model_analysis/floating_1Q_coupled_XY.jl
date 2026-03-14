using LinearAlgebra
using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames

# =============================================================================
# 1. Basic setup
# =============================================================================
# 這一段只做最基本的環境設定：
# - 載入單位常數
# - 指定要分析哪一顆 qubit
# - 準備 Q3D 匯出的電容矩陣資料

const nH = 1e-9
const GHz = 1e9
const fF = 1e-15

const CAP_MATRIX_PATH = joinpath(@__DIR__, "PF6FQ_Q3D_C_Matrix.csv")
const TARGET_QUBIT = "q5"


# =============================================================================
# 2. Helper functions
# =============================================================================
# 這裡把重複出現的步驟抽成小函式，讓主流程可以直接讀出：
# 「先建模 -> 再求解 -> 再做 reduction -> 最後抽物理量」。

"""
    load_qubit_capacitance_table(csv_path, qubit_id)

讀取 Q3D 匯出的電容表，只保留目標 qubit 的資料，並把 fF 轉成 SI 單位 F。
"""
function load_qubit_capacitance_table(csv_path, qubit_id)
    df = CSV.read(csv_path, DataFrame)
    sub = df[df.qubit_id.==qubit_id, :]
    isempty(sub) && error("No capacitance data found for qubit_id = $qubit_id")

    sub.value_F = sub[!, "value(fF)"] .* fF
    return sub
end

"""
    get_component_value(sub, component_name)

從 qubit 對應的資料表中取出某一個元件的電容值。
"""
function get_component_value(sub, component_name)
    values = sub[sub.name.==component_name, :value_F]
    isempty(values) && error("Missing component $component_name in capacitance table")
    return values[1]
end

"""
    build_floating_qubit_coupled_xy_circuit(; include_qubit_inductor, port3_resistance_symbol)

建立「floating qubit + XY line」的三埠模型。

- Port 1 / Port 2：qubit 的兩個差模端點
- Port 3：XY line 耦合端
- include_qubit_inductor=false 時，可得到純電容網路，用來抽等效電容
"""
function build_floating_qubit_coupled_xy_circuit(; include_qubit_inductor, port3_resistance_symbol)
    circuit = Tuple{String,String,String,Num}[]

    # Qubit body:
    # C_01 / C_02 是兩個 pad 對地電容，C_12 是 pad 間電容。
    push!(circuit, ("C_01", "1", "0", C_01))
    push!(circuit, ("C_02", "2", "0", C_02))
    push!(circuit, ("C_12", "1", "2", C_12))

    # Lq 只放在完整 qubit 模型中；若拿掉 Lq，網路就只剩靜電耦合。
    if include_qubit_inductor
        push!(circuit, ("Lq", "1", "2", Lq))
    end

    # Coupling to XY line:
    # 透過 C_13 / C_23 把 qubit 兩側 pad 耦合到 node 3。
    push!(circuit, ("C_13", "1", "3", C_13))
    push!(circuit, ("C_23", "2", "3", C_23))

    # Differential probe ports:
    # Port 1 / Port 2 用非常大的電阻接地，近似理想量測 port 而不額外載入系統。
    push!(circuit, ("P1", "1", "0", 1))
    push!(circuit, ("R_P1", "1", "0", R_Big))
    push!(circuit, ("P2", "2", "0", 2))
    push!(circuit, ("R_P2", "2", "0", R_Big))

    # XY line port:
    # Port 3 是外部控制線；可接真實 50 Ohm，也可用超大電阻近似開路。
    push!(circuit, ("P3", "3", "0", 3))
    push!(circuit, ("R50_XY", "3", "0", port3_resistance_symbol))

    return circuit
end

"""
    build_component_values(sub)

把資料表中的電容值整理成 JosephsonCircuits 使用的符號參數字典。
"""
function build_component_values(sub)
    return Dict(
        C_01 => get_component_value(sub, "C_01"),
        C_02 => get_component_value(sub, "C_02"),
        C_12 => get_component_value(sub, "C_12"),
        C_13 => get_component_value(sub, "C_13"),
        C_23 => get_component_value(sub, "C_23"),
    )
end

"""
    z_to_y_cube(solution)

從 hbsolve 的線性化 Z 矩陣出發，逐頻點反矩陣得到 Y 矩陣。
輸出尺寸為 `(port, port, frequency_index)`。
"""
function z_to_y_cube(solution)
    z_cube = Array(solution.linearized.Z[1, :, 1, :, :])
    _, _, n_freq = size(z_cube)
    y_cube = similar(z_cube)

    for k in 1:n_freq
        y_cube[:, :, k] = inv(Matrix(@view z_cube[:, :, k]))
    end

    return y_cube
end

"""
    apply_port_termination_compensation(y_cube; resistance_ohm_by_port)

在 Y-domain 做 port termination compensation:

    Y_ptc = Y_raw - diag(1 / R_i)

這裡只會扣除被指定的 ports；未指定的 port 會保持原樣。
"""
function apply_port_termination_compensation(y_cube; resistance_ohm_by_port)
    compensated = copy(y_cube)
    n_ports, _, n_freq = size(compensated)

    for (port, resistance_ohm) in resistance_ohm_by_port
        if port < 1 || port > n_ports
            error("Port index $port is out of range for a $n_ports-port matrix.")
        end
        resistance_ohm <= 0 && error("Termination resistance for port $port must be positive.")

        shunt_admittance = 1 / resistance_ohm
        for k in 1:n_freq
            compensated[port, port, k] -= shunt_admittance
        end
    end

    return compensated
end

"""
    differential_mode_weights(component_values)

計算差模/共模轉換中使用的權重。
這裡的 alpha / beta 反映兩個 qubit pad 對整體浮動島權重的分配。
"""
function differential_mode_weights(component_values)
    w_1 = component_values[C_01] + component_values[C_13]
    w_2 = component_values[C_02] + component_values[C_23]
    total = w_1 + w_2

    return (
        w_1=w_1,
        w_2=w_2,
        alpha=w_1 / total,
        beta=w_2 / total,
    )
end

"""
    build_cm_dm_coordinate_transform(component_values)

建立從 `(port1, port2, port3)` 到 `(cm, dm, port3)` 的座標轉換矩陣 A，
使得：

    [V_cm, V_dm, V_3]' = A * [V_1, V_2, V_3]'
"""
function build_cm_dm_coordinate_transform(component_values)
    weights = differential_mode_weights(component_values)
    alpha = weights.alpha
    beta = weights.beta
    return [
        alpha beta 0.0
        1.0 -1.0 0.0
        0.0 0.0 1.0
    ]
end

"""
    apply_coordinate_transformation(y_cube, transform_matrix)

對每個頻點的 Y 矩陣施作：

    Y_m = A^(-T) * Y * A^(-1)

其中 A 定義的是 `V_m = A * V_port`。
"""
function apply_coordinate_transformation(y_cube, transform_matrix)
    _, _, n_freq = size(y_cube)
    transformed = Array{ComplexF64}(undef, size(y_cube))
    a_inv = inv(Matrix{Float64}(transform_matrix))
    a_inv_t = transpose(a_inv)

    for k in 1:n_freq
        transformed[:, :, k] = a_inv_t * Matrix(@view y_cube[:, :, k]) * a_inv
    end

    return transformed
end

"""
    kron_reduce_y_cube(y_cube; keep_ports, drop_ports)

在每個頻點對 Y 矩陣做 Schur complement / Kron reduction：

    Y_eff = Y_kk - Y_kd * Y_dd^(-1) * Y_dk

這裡 `keep_ports` / `drop_ports` 對應目前矩陣座標系下的索引。
"""
function kron_reduce_y_cube(y_cube; keep_ports, drop_ports)
    n_ports, _, n_freq = size(y_cube)
    keep = collect(keep_ports)
    drop = collect(drop_ports)

    isempty(keep) && error("keep_ports must contain at least one port.")
    length(union(keep, drop)) == length(keep) + length(drop) ||
        error("keep_ports and drop_ports must be disjoint.")
    sort(union(keep, drop)) == collect(1:n_ports) ||
        error("keep_ports and drop_ports must partition all $n_ports ports.")

    reduced = Array{ComplexF64}(undef, length(keep), length(keep), n_freq)

    for k in 1:n_freq
        yk = Matrix(@view y_cube[:, :, k])
        y_kk = yk[keep, keep]

        if isempty(drop)
            reduced[:, :, k] = y_kk
            continue
        end

        y_kd = yk[keep, drop]
        y_dd = yk[drop, drop]
        y_dk = yk[drop, keep]
        reduced[:, :, k] = y_kk - (y_kd * (y_dd \ y_dk))
    end

    return reduced
end

"""
    differential_mode_input_admittance(y_cube, component_values)

依照目前 notebook 契約做：
1. 先把 PTC 後的 port-basis Y 轉到 `(cm, dm, port3)` basis
2. 再用一次 Kron reduction 同時消掉 `cm` 與 `port3`
3. 最後留下 differential mode 的 driving-point admittance Yin_dm
"""
function differential_mode_input_admittance(y_cube, component_values)
    transform_matrix = build_cm_dm_coordinate_transform(component_values)
    y_modal = apply_coordinate_transformation(y_cube, transform_matrix)
    y_dm_only = kron_reduce_y_cube(y_modal; keep_ports=(2,), drop_ports=(1, 3))
    yin_dm = vec(y_dm_only[1, 1, :])

    return (
        Yin_dm=yin_dm,
        Y_modal=y_modal,
        Y_dm_only=y_dm_only,
        coordinate_transform=transform_matrix,
    )
end

"""
    effective_capacitance_from_yin(yin_dm, freqs_ghz)

當網路中不含 Josephson 電感與 50 Ohm 終端時，
Im(Yin)/omega 可以視為差模看到的有效電容。
"""
function effective_capacitance_from_yin(yin_dm, freqs_ghz)
    omega = 2π .* freqs_ghz .* GHz
    return imag.(yin_dm) ./ omega
end

"""
    build_plot(traces, title, xaxis_title, yaxis_title; legend_title="Legend")

建立這支 sandbox 腳本自用的 PlotlyJS 圖。
這裡不依賴 repo 其他 plotting helper，避免 sandbox 腳本被外部型別耦合卡住。
"""
function build_plot(traces, title, xaxis_title, yaxis_title; legend_title="Legend")
    return plot(
        traces,
        Layout(
            title=title,
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            legend=attr(title=attr(text=legend_title)),
        ),
    )
end


# =============================================================================
# 3. Load capacitance data for the target qubit
# =============================================================================
# 這一步只處理資料來源：
# - 讀取 Q3D 結果
# - 篩出指定 qubit
# - 把元件電容值整理成後續建模要用的字典

qubit_cap_table = load_qubit_capacitance_table(CAP_MATRIX_PATH, TARGET_QUBIT)


# =============================================================================
# 4. Define circuit symbols and parameter values
# =============================================================================
# 這裡先宣告 JosephsonCircuits 會用到的符號參數，
# 再準備兩組 parameter dictionary：
# - 第一組: 真正的 qubit + XY 50 Ohm 負載
# - 第二組: 拿掉 Lq 並把 XY 負載改成近似開路，只保留電容網路

@variables R_Big R50 C_01 C_02 C_12 Lq C_13 C_23

component_values = build_component_values(qubit_cap_table)

circuitdefs = merge(
    component_values,
    Dict(
        R_Big => 1e100,
        R50 => 50.0,
        Lq => 12.34nH,
    ),
)

circuitdefs_open = merge(
    component_values,
    Dict(
        R_Big => 1e100,
        R50 => 1e100,
        Lq => 12.34nH,
    ),
)


# =============================================================================
# 5. Build the two circuits used in this study
# =============================================================================
# 這個分析會跑兩個版本的模型：
# - full_circuit: 真正有 qubit inductance，且 XY line 接 50 Ohm
# - capacitive_reference_circuit: 去掉 Lq，並把 XY line 視為開路
#
# 第二個模型的用途不是找 qubit 頻率，而是抽「純電容視角」的 Ceff。

full_circuit = build_floating_qubit_coupled_xy_circuit(
    include_qubit_inductor=true,
    port3_resistance_symbol=R50,
)

capacitive_reference_circuit = build_floating_qubit_coupled_xy_circuit(
    include_qubit_inductor=false,
    port3_resistance_symbol=R_Big,
)


# =============================================================================
# 6. Harmonic-balance simulation setup
# =============================================================================
# 這裡定義 hbsolve 的掃頻範圍與求解設定。
# 目前保留原本腳本最後實際使用的設定值，不改物理條件。

ws = 2π .* (1:0.001:10) .* GHz
wp = (2π * 8.001 * GHz,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)


# =============================================================================
# 7. Run the two simulations
# =============================================================================
# - 第一個解: 用來抽含 50 Ohm XY 線載入時的 Yin_dm、G、T1
# - 第二個解: 用來抽純電容網路下的 Ceff

@time single_FQ_with_XY = hbsolve(
    ws,
    wp,
    sources,
    Nmodulationharmonics,
    Npumpharmonics,
    full_circuit,
    circuitdefs;
    returnZ=true,
)

@time single_FQ_no_Lq_R50 = hbsolve(
    ws,
    wp,
    sources,
    Nmodulationharmonics,
    Npumpharmonics,
    capacitive_reference_circuit,
    circuitdefs_open;
    returnZ=true,
)


# =============================================================================
# 8. Convert solver outputs into differential-mode admittance
# =============================================================================
# 這一步是整支腳本最核心的物理後處理：
# 1. 先把 hbsolve 輸出的 Z(ω) 轉成 Y(ω)
# 2. 對 port 1 / port 2 做 PTC，移除 solver-artificial 50 Ohm termination
# 3. 用 PTC 後的 Y 做 differential/common-mode 座標轉換
# 4. 再做 Kron reduction，最後抽出 qubit 差模看到的 Yin_dm

freqs = single_FQ_with_XY.linearized.w ./ (2π .* GHz)

y_cube_full_raw = z_to_y_cube(single_FQ_with_XY)
y_cube_full_ptc = apply_port_termination_compensation(
    y_cube_full_raw;
    resistance_ohm_by_port=Dict(1 => 50.0, 2 => 50.0),
)
dm_result_full = differential_mode_input_admittance(y_cube_full_ptc, circuitdefs)
Yin_dm = dm_result_full.Yin_dm
G_dm = real.(Yin_dm)

y_cube_open_raw = z_to_y_cube(single_FQ_no_Lq_R50)
y_cube_open_ptc = apply_port_termination_compensation(
    y_cube_open_raw;
    resistance_ohm_by_port=Dict(1 => 50.0, 2 => 50.0),
)
dm_result_open = differential_mode_input_admittance(y_cube_open_ptc, circuitdefs_open)
Ceff_dm = effective_capacitance_from_yin(dm_result_open.Yin_dm, freqs)


# =============================================================================
# 9. Plot the effective capacitance and input admittance
# =============================================================================
# 這裡只做視覺化：
# - C_eff_plot: 純電容網路推得的等效差模電容
# - Y_m_eff_plot: 真實 qubit 模型在差模下的輸入導納

C_eff_plot = build_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=Ceff_dm,
            name="Ceff_dm",
        ),
    ],
    "Single Floating Qubit Differential Mode Effective Capacitance",
    "Frequency (GHz)",
    "Capacitance (F)",
    legend_title="Legend",
)

Y_m_eff_plot = build_plot(
    [
        scatter(
            mode="lines+markers",
            x=freqs,
            y=imag.(Yin_dm),
            name="Im Yin_dm",
        ),
        scatter(
            mode="lines+markers",
            x=freqs,
            y=real.(Yin_dm),
            name="Re Yin_dm",
        ),
    ],
    "Single Floating Qubit Differential Mode Input Admittance",
    "Frequency (GHz)",
    "Admittance (S)",
    legend_title="Legend",
)


# =============================================================================
# 10. Extract resonance point and estimate T1
# =============================================================================
# 這裡把前面抽到的差模輸入導納轉成幾個更直觀的物理量：
# - qubit_frequency: 用 |Yin_dm| 最小的位置當作共振附近點
# - Ceff0: 該頻點的有效差模電容
# - G0:   該頻點的實部導納，視作損耗通道
# - T1:   以 Ceff / G 估算能量衰減時間

idx = argmin(abs.(Yin_dm))
qubit_frequency = freqs[idx] # GHz

idx_4_3GHz = argmin(abs.(freqs .- 4.3))

Ceff0 = Ceff_dm[idx]
analytical_differential_mode_effective_c =
    circuitdefs[C_12] +
    (circuitdefs[C_01] * circuitdefs[C_02]) / (circuitdefs[C_01] + circuitdefs[C_02]) +
    (circuitdefs[C_13] * circuitdefs[C_23]) / (circuitdefs[C_13] + circuitdefs[C_23])

Yin0 = Yin_dm[idx]
G0 = real(Yin0)

if G0 <= 0
    @warn "Re(Y_in) ≤ 0 at f ≈ $qubit_frequency GHz → 無有限 T1（近乎無損或模型需檢查）"
else
    T1 = Ceff0 / G0
    println("f≈$(qubit_frequency) GHz:  Ceff=$(Ceff0) F,  ReY=$(G0) S,  T1=$(T1) s")

    ω0 = 2π * qubit_frequency * GHz
    Q = ω0 * Ceff0 / G0
    println("Q=$(Q)")
end
