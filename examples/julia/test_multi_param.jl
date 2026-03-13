# examples/julia/test_multi_param.jl

# include("../src/JPACircuitModelSim.jl")
using JPACircuitModelSim
using JosephsonCircuits
using PlotlyJS

# --- 1. Define Constants ---
nH = 1e-9
GHz = 1e9
pF = 1e-12

# --- 2. Define Circuit ---
ckt = Circuit()
add_component!(ckt, Port("P1", "1", "0", 1))
add_component!(ckt, Resistor("R_P1", "1", "0", :R50))
add_component!(ckt, Inductor("L_s_1", "1", "2", :L_s_1))
add_component!(ckt, Inductor("L_squid", "2", "0", :L_squid))
add_component!(ckt, Capacitor("C_shunt", "2", "0", :C_shunt))
add_component!(ckt, Inductor("L_s_2", "1", "3", :L_s_2))
add_component!(ckt, Capacitor("C_static", "3", "0", :C_static))

# --- 3. Define Parameters & Sweeps ---
circuit_defs = Dict(
    :C_static => 0.0, # Swept
    :L_squid => 0.0,  # Swept
    :L_s_1 => 0.067 * nH,
    :L_s_2 => 0.105 * nH,
    :C_shunt => 10 * pF,
    :R50 => 50.0,
)

# Multi-parameter sweep: Sweep L_squid AND C_static
sweeps = [
    Sweep(:L_squid, (0.1:0.1:1.0) * nH),
    Sweep(:C_static, (0.8:0.1:10.0) * pF)
]

config = SimulationConfig(
    ws=2 * pi * (1:0.001:10) * 1e9, # Zoom in on resonance
    wp=(2 * pi * 8.001 * 1e9,),
    Ip=0.0
)

# --- 4. Run Simulation ---
println("Running multi-parameter simulation...")
results = simulate(ckt, sweeps, config, circuit_defs)

# --- 5. Plot Results ---
println("Plotting results...")

# Plot 1: Sweep L_squid, fix C_static to 1st value (default)
p1 = plot_result(results, type=:phase)
display(p1)

# Plot 2: Sweep L_squid, fix C_static to 2nd value
# p2 = plot_result(results, type=:phase, fixed_indices=Dict(2 => 2))
# display(p2)

println("Test complete.")
