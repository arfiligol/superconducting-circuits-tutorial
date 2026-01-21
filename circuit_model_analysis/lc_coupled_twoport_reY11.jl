using JosephsonCircuits
using LinearAlgebra
using CSV
using DataFrames

# Simple LC resonator coupled to a 50-ohm port through Cc.
# Port 1 sits directly on the LC node. Port 2 is on the other side of Cc.

GHz = 1e9
nH = 1e-9
fF = 1e-15

@variables L_res C_res L_couple R_port1 R_port2

two_port_circuit = [
    ("P1", "1", "0", 1),
    ("R_P1", "1", "0", R_port1),
    ("L_res", "1", "0", L_res),
    ("C_res", "1", "0", C_res),
    ("L_couple", "1", "2", L_couple),
    ("P2", "2", "0", 2),
    ("R_P2", "2", "0", R_port2),
]

load_only_circuit = [
    ("P1", "1", "0", 1),
    ("R_P1", "1", "0", R_port1),
    ("L_res", "1", "0", L_res),
    ("C_res", "1", "0", C_res),
    ("L_couple", "1", "2", L_couple),
    ("R_P2", "2", "0", R_port2),
]

circuitdefs = Dict(
    L_res => 10.0 * nH,
    C_res => 100.0 * fF,
    L_couple => 1.0 * 1e-30 * fF,
    R_port1 => 50.0,
    R_port2 => 50.0,
)

println(circuitdefs)

freqs_ghz = range(1.0, 10.0, length=1001)
ws = 2 * pi .* freqs_ghz .* GHz

sol_two_port = JosephsonCircuits.hblinsolve(ws, two_port_circuit, circuitdefs; returnZ=true)
sol_load_only = JosephsonCircuits.hblinsolve(ws, load_only_circuit, circuitdefs; returnZ=true)

Z_two_port = Array(sol_two_port.Z[1, :, 1, :, :])
_, _, Nf = size(Z_two_port)
reY11 = zeros(Float64, Nf)
reY22 = zeros(Float64, Nf)
reY11_load_only = zeros(Float64, Nf)

for k in 1:Nf
    Zk = Matrix(@view Z_two_port[:, :, k])
    Yk = inv(Zk)
    reY11[k] = real(Yk[1, 1])
    reY22[k] = real(Yk[2, 2])

    Zk_load = Matrix(@view sol_load_only.Z[1, :, 1, :, k])
    Yk_load = inv(Zk_load)
    reY11_load_only[k] = real(Yk_load[1, 1])
end

out = DataFrame(
    "Freq [GHz]" => freqs_ghz,
    "Re(Y11) [S]" => reY11,
    "Re(Y22) [S]" => reY22,
    "Re(Y11) load-only [S]" => reY11_load_only,
)

output_path = "data/processed/lc_coupled_twoport_reY11.csv"
mkpath(dirname(output_path))
CSV.write(output_path, out)

println("Wrote: $(output_path)")
closest_idx = argmin(abs.(freqs_ghz .- 5.0))
println("Re(Y11) sample near 5 GHz (", freqs_ghz[closest_idx], " GHz): ", reY11[closest_idx])
println("Re(Y22) sample near 5 GHz (", freqs_ghz[closest_idx], " GHz): ", reY22[closest_idx])
println("Re(Y11) load-only sample near 5 GHz (", freqs_ghz[closest_idx], " GHz): ", reY11_load_only[closest_idx])
