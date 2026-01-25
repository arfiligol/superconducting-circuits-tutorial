#=
Julia Simulation Bridge for JosephsonCircuits.jl

This file provides wrapper functions that are called from Python via JuliaCall.
It simplifies the interface between Python domain models and Julia's hbsolve.
=#

using JosephsonCircuits

"""
    run_lc_simulation(L_nH, C_pF, f_start_GHz, f_stop_GHz, n_points)

Simulate a simple LC resonator and return S11 data.

# Arguments
- `L_nH`: Inductance in nanohenries
- `C_pF`: Capacitance in picofarads  
- `f_start_GHz`: Start frequency in GHz
- `f_stop_GHz`: Stop frequency in GHz
- `n_points`: Number of frequency points

# Returns
Dict with keys: :frequencies_ghz, :s11_real, :s11_imag
"""
function run_lc_simulation(L_nH::Float64, C_pF::Float64,
    f_start_GHz::Float64, f_stop_GHz::Float64,
    n_points::Int)
    # Unit conversions
    nH = 1e-9
    pF = 1e-12
    GHz = 1e9

    # Define circuit
    @variables L C R50

    circuit = [
        ("P1", "1", "0", 1),      # Port 1
        ("R50", "1", "0", R50),   # 50Ω impedance
        ("L", "1", "2", L),       # Inductor
        ("C", "2", "0", C),       # Capacitor
    ]

    circuitdefs = Dict(
        L => L_nH * nH,
        C => C_pF * pF,
        R50 => 50.0,
    )

    # Frequency range
    frequencies = range(f_start_GHz, f_stop_GHz, length=n_points) .* GHz
    ws = 2π .* frequencies

    # Pump configuration (for hbsolve)
    wp = (2π * 5.0GHz,)  # Default pump at 5 GHz
    sources = [(mode=(1,), port=1, current=0.0)]

    # Run simulation
    sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)

    # Extract S11
    S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)

    return Dict(
        :frequencies_ghz => collect(frequencies ./ GHz),
        :s11_real => real.(S11),
        :s11_imag => imag.(S11)
    )
end


"""
    run_custom_simulation(topology, component_values, f_start_GHz, f_stop_GHz, n_points)

Simulate a custom circuit topology.

# Arguments  
- `topology`: Vector of tuples (name, node1, node2, value_key)
- `component_values`: Dict mapping value keys to actual values (with units)
- `f_start_GHz`, `f_stop_GHz`, `n_points`: Frequency sweep parameters

# Returns
Dict with keys: :frequencies_ghz, :s11_real, :s11_imag
"""
function run_custom_simulation(topology::Vector,
    component_values::Dict,
    f_start_GHz::Float64,
    f_stop_GHz::Float64,
    n_points::Int)
    GHz = 1e9

    # Build circuit from topology
    circuit = [(t[1], t[2], t[3], t[4]) for t in topology]

    # Frequency range
    frequencies = range(f_start_GHz, f_stop_GHz, length=n_points) .* GHz
    ws = 2π .* frequencies

    # Pump configuration
    wp = (2π * 5.0GHz,)
    sources = [(mode=(1,), port=1, current=0.0)]

    # Run simulation
    sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, component_values)

    # Extract S11
    S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)

    return Dict(
        :frequencies_ghz => collect(frequencies ./ GHz),
        :s11_real => real.(S11),
        :s11_imag => imag.(S11)
    )
end


"""
    run_lc_parameter_sweep(L_values_nH, C_values_pF, f_start_GHz, f_stop_GHz, n_points)

Run a 2D parameter sweep over L and C values entirely in Julia for performance.
Uses multithreading for parallel execution.

# Arguments
- `L_values_nH`: Vector of inductance values in nH
- `C_values_pF`: Vector of capacitance values in pF  
- `f_start_GHz`, `f_stop_GHz`, `n_points`: Frequency sweep parameters

# Returns
Dict with:
- :frequencies_ghz: 1D vector of frequencies
- :L_values_nh: 1D vector of L values
- :C_values_pf: 1D vector of C values
- :s11_magnitude: 3D array [L_idx, C_idx, freq_idx]
- :resonance_freqs_ghz: 2D array [L_idx, C_idx] of found resonances
"""
function run_lc_parameter_sweep(L_values_nH::Vector{Float64},
    C_values_pF::Vector{Float64},
    f_start_GHz::Float64,
    f_stop_GHz::Float64,
    n_points::Int)
    nH = 1e-9
    pF = 1e-12
    GHz = 1e9

    n_L = length(L_values_nH)
    n_C = length(C_values_pF)

    # Preallocate result arrays
    frequencies = range(f_start_GHz, f_stop_GHz, length=n_points) .* GHz
    s11_magnitude = zeros(n_L, n_C, n_points)
    resonance_freqs = zeros(n_L, n_C)

    # Circuit template
    @variables L C R50
    circuit = [
        ("P1", "1", "0", 1),
        ("R50", "1", "0", R50),
        ("L", "1", "2", L),
        ("C", "2", "0", C),
    ]

    ws = 2π .* frequencies
    wp = (2π * 5.0GHz,)
    sources = [(mode=(1,), port=1, current=0.0)]

    # Sweep over all L, C combinations (fully in Julia with threading)
    Threads.@threads for i in 1:n_L
        for j in 1:n_C
            circuitdefs = Dict(
                L => L_values_nH[i] * nH,
                C => C_values_pF[j] * pF,
                R50 => 50.0,
            )

            sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)
            S11 = sol.linearized.S(outputmode=(0,), outputport=1, inputmode=(0,), inputport=1, freqindex=:)

            mag = abs.(S11)
            s11_magnitude[i, j, :] = mag

            # Find resonance (minimum S11)
            min_idx = argmin(mag)
            resonance_freqs[i, j] = frequencies[min_idx] / GHz
        end
    end

    return Dict(
        :frequencies_ghz => collect(frequencies ./ GHz),
        :L_values_nh => L_values_nH,
        :C_values_pf => C_values_pF,
        :s11_magnitude => s11_magnitude,
        :resonance_freqs_ghz => resonance_freqs
    )
end
