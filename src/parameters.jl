# src/parameters.jl

struct Sweep
    parameter::Symbol
    values::AbstractVector
end

struct SimulationConfig
    ws::AbstractVector{<:Real} # Signal frequencies
    wp::Tuple{Vararg{Real}}    # Pump frequencies
    Ip::Real                   # Pump current
    sources::Vector            # Source definitions
    Npumpharmonics::Tuple{Vararg{Int}}
    Nmodulationharmonics::Tuple{Vararg{Int}}
end

# Helper constructor for common use cases
function SimulationConfig(;
    ws,
    wp,
    Ip,
    sources=[(mode=(1,), port=1, current=Ip)],
    Npumpharmonics=(20,),
    Nmodulationharmonics=(10,)
)
    return SimulationConfig(ws, wp, Ip, sources, Npumpharmonics, Nmodulationharmonics)
end
