# src/simulation.jl

using ProgressMeter

function simulate(
    ckt::Circuit,
    sweeps::Vector{Sweep},
    config::SimulationConfig,
    circuit_defs::Dict{Symbol,Float64}
)
    # Convert Circuit to JosephsonCircuits format
    lc_circuit = to_josephson_circuit(ckt)

    # Frequencies in GHz for storage
    freqs_ghz = config.ws ./ (2 * pi * 1e9)

    # Extract parameter names and values
    param_names = [s.parameter for s in sweeps]
    param_values_list = [collect(s.values) for s in sweeps]

    # Initialize results container
    results = SimulationResult(param_names, param_values_list, collect(freqs_ghz))

    println("Starting multi-parameter sweep for $(param_names)...")

    # Create iterator for all parameter combinations
    # Iterators.product returns a generator of tuples
    param_combinations = collect(Iterators.product(param_values_list...))

    # We need to track indices for storage
    # CartesianIndices matches the shape of the product
    indices = CartesianIndices(tuple(length.(param_values_list)...))

    # Progress Bar
    p = Progress(length(indices); dt=0.5, desc="Simulation Progress: ")

    for (idx, vals) in zip(indices, param_combinations)
        # vals is a tuple of current parameter values (val1, val2, ...)
        # idx is a CartesianIndex (i1, i2, ...)

        # Update circuit definitions with current sweep values
        current_defs = copy(circuit_defs)
        for (name, val) in zip(param_names, vals)
            current_defs[name] = val
        end

        # Run hbsolve
        sol = hbsolve(
            config.ws,
            config.wp,
            config.sources,
            config.Nmodulationharmonics,
            config.Npumpharmonics,
            lc_circuit,
            current_defs;
            returnZ=true
        )

        # Extract S11
        S11_data = sol.linearized.S(
            outputmode=(0,),
            outputport=1,
            inputmode=(0,),
            inputport=1,
            freqindex=:
        )

        # Extract Z11
        Z11_data = sol.linearized.Z[1, 1, 1, 1, :]

        # Store in results
        # results.S11 has dimensions [freq, p1, p2, ...]
        # We need to construct the full index: (:, i1, i2, ...)
        full_idx = (:, Tuple(idx)...)

        results.S11[full_idx...] = S11_data
        results.Z11[full_idx...] = Z11_data

        next!(p)
    end

    println("Simulation complete.")
    return results
end

# Overload for single sweep for backward compatibility / convenience
function simulate(
    ckt::Circuit,
    sweep::Sweep,
    config::SimulationConfig,
    circuit_defs::Dict{Symbol,Float64}
)
    return simulate(ckt, [sweep], config, circuit_defs)
end
