using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames
# using GLMakie

pH = 1e-12
fF = 1e-15

@variables Rbig R50 Cq Lq Cqr Cr Lr Cc

circuit = Tuple{String,String,String,Num}[]

# Port 1 (Input)
push!(circuit, ("P1", "1", "0", 1)) # Port 1
push!(circuit, ("R_P1", "1", "0", Rbig)) # Very Large Resistance (acts like open circuit)

# Grounding Qubit
push!(circuit, ("Cq", "1", "0", Cq))
push!(circuit, ("Lq", "1", "0", Lq))

# Coupler
push!(circuit, ("C_qr", "1", "2", Cqr))

# Resonator
push!(circuit, ("Cr", "2", "0", Cr))
push!(circuit, ("Lr", "2", "0", Lr))

# Coupler
push!(circuit, ("Cc", "2", "3", Cc))

# TL R50 / 2
push!(circuit, ("R_TL", "3", "0", R50 / 2))

circuitdefs = Dict(
    Rbig => 1e15,
    Cq => 55e-15,
    Lq => 14.2e-9,
    Cqr => 5e-15,
    Cr => 5.24599642556709e-13,
    Lr => 2.13287527427329e-9,
    Cc => 10e-15, # Coupling capacitor
    R50 => 50.0,
)

ws = 2 * pi * (5:0.0001:6) * 1e9
wp = (2 * pi * 8.001 * 1e9,)
Ip = 0.0
sources = [(mode=(1,), port=1, current=Ip)]
Npumpharmonics = (20,)
Nmodulationharmonics = (10,)

@time transmission_line = hbsolve(ws, wp, sources, Nmodulationharmonics,
    Npumpharmonics, circuit, circuitdefs; returnZ=true)

freqs = transmission_line.linearized.w / (2 * pi * 1e9)
Z11 = vec(transmission_line.linearized.Z[1, 1, 1, 1, :])
# 計算實部導納 Re{Y₁₁} = Re{1/Z₁₁}
G11 = real.(1 ./ (Z11))
# 取實部與虛部
R11 = real.(Z11)
X11 = imag.(Z11)

plot(
    scatter(
        mode="markers",
        x=freqs,
        y=G11,
    ),
    config=PlotConfig(
        scrollZoom=true,
        responsive=true,
        staticPlot=false,
        displayModeBar=true, # Default False
        toImageButtonOptions=attr(
            format="png", # one of png, svg, jpeg, webp
            filename="custom_image",
            height=500,
            width=700,
            scale=10, # Multiply title/legend/axis/canvas sizes by this factor
        ).fields,
        modeBarButtonsToAdd=["drawline",
            # "drawopenpath",
            # "drawclosedpath",
            "drawcircle",
            "drawrect",
            "eraseshape"
        ],
    ),
)


plot(
    freqs, R11,
    xlabel="Frequency (GHz)", ylabel="Ω",
    label="Re Z₁₁"
)
plot!(
    freqs, X11,
    label="Im Z₁₁"
)
