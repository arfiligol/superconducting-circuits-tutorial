module JPACircuitModelSim

using JosephsonCircuits

include("components.jl")
include("parameters.jl")
include("results.jl")
include("simulation.jl")
include("plotting.jl")

export Circuit, add_component!, to_josephson_circuit
export Capacitor, Inductor, Resistor, JosephsonJunction, Port
export Sweep, SimulationConfig
export SimulationResult, simulate
export plot_result

end
