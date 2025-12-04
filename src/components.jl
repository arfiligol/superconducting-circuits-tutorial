# src/components.jl

abstract type CircuitComponent end

struct Capacitor <: CircuitComponent
    name::String
    n1::String
    n2::String
    value::Union{Real,Symbol} # Can be a number or a symbolic variable
end

struct Inductor <: CircuitComponent
    name::String
    n1::String
    n2::String
    value::Union{Real,Symbol}
end

struct Resistor <: CircuitComponent
    name::String
    n1::String
    n2::String
    value::Union{Real,Symbol}
end

struct JosephsonJunction <: CircuitComponent
    name::String
    n1::String
    n2::String
    value::Union{Real,Symbol} # Critical current or Inductance? Usually LJ or Ic. Let's assume LJ for now as per JosephsonCircuits convention often uses L.
    # Wait, JosephsonCircuits usually takes (name, n1, n2, value).
end

struct Port <: CircuitComponent
    name::String
    n1::String
    n2::String
    value::Union{Real,Symbol} # Port impedance or index? Usually just 1 or 50.
end

mutable struct Circuit
    components::Vector{CircuitComponent}

    Circuit() = new(Vector{CircuitComponent}[])
end

function add_component!(ckt::Circuit, comp::CircuitComponent)
    push!(ckt.components, comp)
end

# Helper to convert our Circuit struct to JosephsonCircuits compatible list
function to_josephson_circuit(ckt::Circuit)
    netlist = []
    for c in ckt.components
        push!(netlist, (c.name, c.n1, c.n2, c.value))
    end
    return netlist
end
