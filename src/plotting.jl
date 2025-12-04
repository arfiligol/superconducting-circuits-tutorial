# src/plotting.jl

using PlotlyJS
using Printf

# --- Constants for Layout ---
const PLOTLY_FONT_SIZE = 18
const PLOTLY_TITLE_FONT_SIZE = 30
const PLOTLY_LEGEND_FONT_SIZE = 18

function unwrap_phase(phases::AbstractVector{<:Real})
    if isempty(phases)
        return phases
    end
    unwrapped = similar(phases)
    unwrapped[1] = phases[1]
    shift = 0.0
    two_pi = 2π
    for i in 2:length(phases)
        diff = phases[i] - phases[i-1]
        if diff > π
            shift -= two_pi
        elseif diff < -π
            shift += two_pi
        end
        unwrapped[i] = phases[i] + shift
    end
    return unwrapped
end

function format_value_with_unit(val::Real, param_name::Symbol)
    # Heuristic for unit conversion
    name_str = string(param_name)

    if startswith(name_str, "L") && abs(val) < 1e-6
        # Inductance -> nH
        return @sprintf("%.2f nH", val * 1e9)
    elseif startswith(name_str, "C") && abs(val) < 1e-9
        # Capacitance -> pF
        return @sprintf("%.2f pF", val * 1e12)
    elseif abs(val) < 1e-3 && abs(val) > 0
        return @sprintf("%.2e", val)
    else
        return string(round(val, digits=3))
    end
end

function apply_plotly_layout(
    p;
    title::String,
    xaxis_title::String,
    yaxis_title::String,
    legend_title::String="Legend",
    x_range=nothing,
    y_range=nothing,
    width=nothing,
    height=nothing
)
    layout_attrs = Dict{Symbol,Any}(
        :title => Dict(
            :text => title,
            :xanchor => "center",
            :yanchor => "top",
            :x => 0.5,
            :font => Dict(:size => PLOTLY_TITLE_FONT_SIZE)
        ),
        :font => Dict(:size => PLOTLY_FONT_SIZE),
        :showlegend => true,
        :legend => Dict(
            :title => Dict(:text => legend_title, :font => Dict(:size => PLOTLY_LEGEND_FONT_SIZE)),
            :font => Dict(:size => PLOTLY_LEGEND_FONT_SIZE)
        ),
        :margin => Dict(:l => 70, :r => 40, :t => 80, :b => 70),
        :xaxis => Dict(:title_text => xaxis_title),
        :yaxis => Dict(:title_text => yaxis_title),
        :hovermode => "closest"
    )

    if !isnothing(width)
        layout_attrs[:width] = width
    end
    if !isnothing(height)
        layout_attrs[:height] = height
    end
    if !isnothing(x_range)
        layout_attrs[:xaxis][:range] = x_range
    end
    if !isnothing(y_range)
        layout_attrs[:yaxis][:range] = y_range
    end

    relayout!(p, layout_attrs)
    return p
end

function plot_result(result::SimulationResult; type=:phase, fixed_indices::Dict{Int,Int}=Dict{Int,Int}())
    traces = AbstractTrace[]

    # Determine which parameter to sweep (plot)
    # Default: Sweep the first parameter (index 1)
    # If there are multiple parameters, we need to fix the others.

    n_dims = length(result.parameter_names)

    if n_dims == 0
        error("No parameters in result")
    end

    # We assume we are plotting along the 1st parameter dimension by default
    # unless specified otherwise (TODO: support plotting along other dims)
    sweep_dim = 1
    sweep_param_name = result.parameter_names[sweep_dim]
    sweep_values = result.parameter_values[sweep_dim]

    # Construct the slicing index
    # S11 dims: [freq, p1, p2, ...]
    # We want to iterate over p1, and fix p2, p3...

    # Default fixed indices for other dimensions: 1
    current_indices = ones(Int, n_dims)

    # Apply user provided fixed indices
    for (dim, idx) in fixed_indices
        if dim != sweep_dim && 1 <= idx <= length(result.parameter_values[dim])
            current_indices[dim] = idx
        end
    end

    # Build title suffix to show fixed parameters
    title_suffix = ""
    if n_dims > 1
        fixed_info = []
        for d in 2:n_dims
            p_name = result.parameter_names[d]
            p_val = result.parameter_values[d][current_indices[d]]
            p_str = format_value_with_unit(p_val, p_name)
            push!(fixed_info, "$p_name=$p_str")
        end
        title_suffix = " (" * join(fixed_info, ", ") * ")"
    end

    if type == :phase
        y_label = "Phase (deg)"
        title_text = "S11 Phase Sweep" * title_suffix
    elseif type == :magnitude
        y_label = "Magnitude"
        title_text = "S11 Magnitude Sweep" * title_suffix
    elseif type == :imY11
        y_label = "Im(Y11) (S)"
        title_text = "Im(Y11) Sweep" * title_suffix
    else
        error("Unknown plot type: $type")
    end

    for i in 1:length(sweep_values)
        val = sweep_values[i]
        val_str = format_value_with_unit(val, sweep_param_name)

        # Construct full index for this trace
        # We want [:, i, fixed_p2, fixed_p3...]
        # current_indices holds [1, fixed_p2, fixed_p3...] (initially 1s)
        # We update the sweep dimension index
        current_indices[sweep_dim] = i

        # Convert to tuple for indexing
        # Note: result.S11 has 1 extra dimension at the start for frequency
        # So we need (:, current_indices...)
        slice_idx = (:, current_indices...)

        if type == :phase
            # Calculate phase in degrees
            phase_rad = angle.(result.S11[slice_idx...])
            y_data = rad2deg.(unwrap_phase(phase_rad))
        elseif type == :magnitude
            y_data = abs.(result.S11[slice_idx...])
        elseif type == :imY11
            # Calculate Y11 from Z11
            y_data = imag.(1 ./ result.Z11[slice_idx...])
        end

        trace = scatter(
            x=result.freqs,
            y=y_data,
            mode="lines",
            name="$(sweep_param_name) = $(val_str)"
        )
        push!(traces, trace)
    end

    p = plot(traces)

    apply_plotly_layout(
        p,
        title=title_text,
        xaxis_title="Frequency (GHz)",
        yaxis_title=y_label,
        legend_title=string(sweep_param_name)
    )

    return p
end
