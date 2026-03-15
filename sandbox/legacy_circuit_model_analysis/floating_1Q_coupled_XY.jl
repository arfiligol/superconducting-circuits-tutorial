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
const LQ_SWEEP_SUMMARY_CSV_PATH =
    joinpath(@__DIR__, "floating_1Q_coupled_XY_Lq_sweep_summary.csv")
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
    # Port 1 / Port 2 明確接 50 Ohm termination。
    # 後處理時再對這兩個 measurement ports 做 PTC，把人工載入扣掉。
    push!(circuit, ("P1", "1", "0", 1))
    push!(circuit, ("R_P1", "1", "0", R50))
    push!(circuit, ("P2", "2", "0", 2))
    push!(circuit, ("R_P2", "2", "0", R50))

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
    extract_resonance_from_yin(freqs_ghz, yin_dm)

用 `Im(Yin_dm)` 過零來估計共振頻率，並在線性插值後讀出同一點的 `Re(Yin_dm)`。
若掃頻範圍內沒有過零點，則退回 `argmin(abs.(Im(Yin_dm)))`。
"""
function extract_resonance_from_yin(freqs_ghz, yin_dm)
    imag_y = imag.(yin_dm)
    real_y = real.(yin_dm)
    crossing_pairs = Tuple{Int,Int}[]

    for k in 1:(length(freqs_ghz) - 1)
        imag_y[k] == 0 && return (frequency_ghz=freqs_ghz[k], re_y=real_y[k], crossed=true)
        imag_y[k] * imag_y[k + 1] < 0 && push!(crossing_pairs, (k, k + 1))
    end

    if !isempty(crossing_pairs)
        scores = [abs(imag_y[i]) + abs(imag_y[j]) for (i, j) in crossing_pairs]
        k1, k2 = crossing_pairs[argmin(scores)]

        f1 = freqs_ghz[k1]
        f2 = freqs_ghz[k2]
        im1 = imag_y[k1]
        im2 = imag_y[k2]
        re1 = real_y[k1]
        re2 = real_y[k2]
        t = -im1 / (im2 - im1)

        return (
            frequency_ghz=f1 + t * (f2 - f1),
            re_y=re1 + t * (re2 - re1),
            crossed=true,
        )
    end

    idx = argmin(abs.(imag_y))
    return (
        frequency_ghz=freqs_ghz[idx],
        re_y=real_y[idx],
        crossed=false,
    )
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
# 再準備 sweep 會用到的參數：
# - 三個 ports 都保留 50 Ohm termination
# - Lq 則在 sweep loop 中逐個代入

@variables R50 C_01 C_02 C_12 Lq C_13 C_23
const LQ_SWEEP_VALUES = collect(10.0:1.0:30.0) .* nH

component_values = build_component_values(qubit_cap_table)

base_circuitdefs = merge(
    component_values,
    Dict(
        R50 => 50.0,
    ),
)

# 原本 Ceff 的做法有兩條：
# 1. 用純電容 reference 網路做 `Ceff_dm = Im(Yin_dm) / omega`
# 2. 用這個解析式當作 constant Ceff estimate
effective_capacitance_estimate =
    component_values[C_12] +
    (component_values[C_01] * component_values[C_02]) /
    (component_values[C_01] + component_values[C_02]) +
    (component_values[C_13] * component_values[C_23]) /
    (component_values[C_13] + component_values[C_23])


# =============================================================================
# 5. Build the circuit used in this study
# =============================================================================
# 這個分析只跑一個版本的模型：
# - full_circuit: 真正有 qubit inductance，且三個 ports 都保留 50 Ohm termination

full_circuit = build_floating_qubit_coupled_xy_circuit(
    include_qubit_inductor=true,
    port3_resistance_symbol=R50,
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
# 7. Run the simulation
# =============================================================================
# 這裡對 Lq 做 sweep。
# 每一個 Lq 都會跑：
# hbsolve -> Z to Y -> PTC -> CT -> Kron -> Yin_dm -> f_res -> ReY(f_res) -> T1

sweep_summary = DataFrame(
    Lq_nH=Float64[],
    qubit_frequency_GHz=Float64[],
    ReY_at_resonance_S=Float64[],
    T1_s=Float64[],
    crossed_zero=Bool[],
)

for lq_value in LQ_SWEEP_VALUES
    circuitdefs = merge(base_circuitdefs, Dict(Lq => lq_value))

    @time single_FQ = hbsolve(
        ws,
        wp,
        sources,
        Nmodulationharmonics,
        Npumpharmonics,
        full_circuit,
        circuitdefs;
        returnZ=true,
    )

    current_freqs = single_FQ.linearized.w ./ (2π .* GHz)
    y_cube_raw = z_to_y_cube(single_FQ)
    y_cube_ptc = apply_port_termination_compensation(
        y_cube_raw;
        resistance_ohm_by_port=Dict(1 => 50.0, 2 => 50.0),
    )
    dm_result = differential_mode_input_admittance(y_cube_ptc, circuitdefs)
    yin_dm = dm_result.Yin_dm

    lq_nh = lq_value / nH
    resonance = extract_resonance_from_yin(current_freqs, yin_dm)
    qubit_frequency = resonance.frequency_ghz
    G0 = resonance.re_y
    T1 = G0 > 0 ? effective_capacitance_estimate / G0 : NaN

    push!(
        sweep_summary,
        (
            Lq_nH=lq_nh,
            qubit_frequency_GHz=qubit_frequency,
            ReY_at_resonance_S=G0,
            T1_s=T1,
            crossed_zero=resonance.crossed,
        ),
    )
end


# =============================================================================
# 8. Plot the T1 sweep
# =============================================================================
# 你要的圖：
# - x 軸：Lq
# - y 軸：T1
# - 顏色：共振頻率

T1_vs_Lq_scatter_plot = build_plot(
    [
        scatter(
            mode="markers",
            x=sweep_summary.Lq_nH,
            y=sweep_summary.T1_s,
            text=[
                "f=$(round(f, digits=4)) GHz, ReY=$(g) S, crossed=$(crossed)"
                for (f, g, crossed) in zip(
                    sweep_summary.qubit_frequency_GHz,
                    sweep_summary.ReY_at_resonance_S,
                    sweep_summary.crossed_zero,
                )
            ],
            marker=attr(
                size=12,
                color=sweep_summary.qubit_frequency_GHz,
                colorscale="Viridis",
                colorbar=attr(title="Frequency (GHz)"),
                showscale=true,
            ),
            name="T1",
        ),
    ],
    "Floating Qubit T1 vs Lq Sweep",
    "Lq (nH)",
    "T1 (s)",
    legend_title="Metric",
)

CSV.write(LQ_SWEEP_SUMMARY_CSV_PATH, sweep_summary)
println("Wrote sweep summary CSV to $(LQ_SWEEP_SUMMARY_CSV_PATH)")
