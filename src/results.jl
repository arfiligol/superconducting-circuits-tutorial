# src/results.jl

struct SimulationResult
    parameter_names::Vector{Symbol}
    parameter_values::Vector{Vector{Float64}}
    freqs::Vector{Float64}
    S11::Array{ComplexF64} # Dimensions: [freqs, param1, param2, ...]
    Z11::Array{ComplexF64} # Dimensions: [freqs, param1, param2, ...]
end

# Helper to initialize result container
function SimulationResult(param_names::Vector{Symbol}, param_vals::Vector{Vector{Float64}}, freqs::Vector)
    # Calculate dimensions
    param_dims = length.(param_vals)
    n_freqs = length(freqs)

    # Total dimensions: freq + params
    dims = (n_freqs, param_dims...)

    return SimulationResult(
        param_names,
        param_vals,
        Float64.(freqs),
        zeros(ComplexF64, dims),
        zeros(ComplexF64, dims)
    )
end

# Compatibility constructor for single parameter sweep
function SimulationResult(param_name::Symbol, param_vals::Vector, freqs::Vector)
    return SimulationResult([param_name], [Float64.(param_vals)], freqs)
end
