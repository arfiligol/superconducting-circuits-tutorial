using JosephsonCircuits
using PlotlyJS
using CSV, DataFrames

include("../../src/julia/utils.jl")

pH = 1e-12
fF = 1e-15

@variables R_Big R50 Cq Lq Cr Lr Cc

circuit = Tuple{String,String,String,Num}[]

# Port 1 (Input)
push!(circuit, ("P1", "1", "0", 1)) # Port 1
push!(circuit, ("R_P1", "1", "0", R_Big)) # 50 Ohm load

# Grounding Qubit
push!(circuit, ("Cq", "1", "0", Cq))
push!(circuit, ("Lq", "1", "0", Lq))

# Coupler
push!(circuit, ("Cc", "1", "2", Cc))

# R50
push!(circuit, ("R50_XY", "2", "0", R50))


circuitdefs = Dict(
    R_Big => 1e15,
    R50 => 50.0,
    Cc => 10e-15, # Coupling capacitor
    Cq => 1e-15,
    Lq => 24.2e-9,
)

ws = 2 * pi * (0.1:0.001:10) * 1e9
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
    scatter(
        mode="lines",
        x=freqs,
        y=R11,
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



# plot(
#     freqs, R11,
#     xlabel="Frequency (GHz)", ylabel="Ω",
#     label="Re Z₁₁",
# )
# plot!(
#     freqs, X11,
#     label="Im Z₁₁"
# )
