# examples/julia/test_new_framework.jl

include("../src/JPACircuitModelSim.jl")
using .JPACircuitModelSim
using JosephsonCircuits
using PlotlyJS

# --- 1. Define Constants ---
nH = 1e-9
GHz = 1e9
pF = 1e-12
fF = 1e-15

# --- 2. Define Circuit ---
ckt = Circuit()
add_component!(ckt, Port("P1", "1", "0", 1))
add_component!(ckt, Resistor("R_P1", "1", "0", :R50))
# Inductor Branch
add_component!(ckt, Inductor("L_s_1", "1", "2", :L_s_1))
add_component!(ckt, Inductor("L_squid", "2", "0", :L_squid))
add_component!(ckt, Capacitor("C_shunt", "2", "0", :C_shunt))
# Capacitor Branch
add_component!(ckt, Inductor("L_s_2", "1", "3", :L_s_2))
add_component!(ckt, Capacitor("C_static", "3", "0", :C_static))

# --- 3. Define Parameters & Sweep ---
# Initial values
circuit_defs = Dict(
    :C_static => 0.885 * pF,
    :L_squid => 0.0, # Will be swept
    :L_s_1 => 0.067 * nH,
    :L_s_2 => 0.105 * nH,
    :C_shunt => 10 * pF,
    :R50 => 50.0,
)

# Sweep definition
L_jun_sweep_values = (0.1:0.2:1.0) * nH
sweep = Sweep(:L_squid, L_jun_sweep_values / 2) # Note: Lr = L_jun / 2

# Simulation Config
ws = 2 * pi * (0.1:0.01:20) * 1e9
config = SimulationConfig(
    ws=ws,
    wp=(2 * pi * 8.001 * 1e9,),
    Ip=0.0
)

# --- 4. Run Simulation ---
println("Running simulation...")
results = simulate(ckt, sweep, config, circuit_defs)

# --- 5. Plot Results ---
println("Plotting results...")
p1 = plot_result(results, type=:phase)
display(p1)

# p2 = plot_result(results, type=:imY11)
# display(p2)

println("Test complete.")
