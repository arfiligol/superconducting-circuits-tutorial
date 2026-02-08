import numpy as np
import plotly.graph_objects as go


def generate_fake_data():
    # Simulate a SQUID arch: f = f_max * |cos(x)|
    phi = np.linspace(-2, 2, 100)  # Flux-like variable
    # Map to L_jun for x-axis? Or just plot vs Index/Flux to keep it simple as requested
    # The user mentioned "Fake Data Point"
    # Let's emulate L_jun vs Freq as in the real app

    # L_jun is typically ~ 1/|cos|. Let's just plot generic X vs Y
    x = np.linspace(0.1, 2.0, 50)  # L_jun [nH]

    # Simple model: Freq = 1 / sqrt(L_total) ~ 1 / sqrt(x + L_geo)
    # Let's just do a simple curve
    y_raw = 5.0 / np.sqrt(x) + np.random.normal(0, 0.05, 50)  # Add noise
    y_fit = 5.0 / np.sqrt(x)

    return x, y_raw, y_fit


def plot_sandbox():
    x, y_raw, y_fit = generate_fake_data()

    # Minimal Plotly Trace
    trace_raw = go.Scatter(
        x=x, y=y_raw, mode="markers", name="Fake Raw Data", marker=dict(size=10, color="blue")
    )

    trace_fit = go.Scatter(
        x=x,
        y=y_fit,
        mode="lines",
        name="Fake Fit Curve",
        line=dict(width=3, color="red", dash="dash"),
    )

    # Minimal Figure - No custom layout applied
    fig = go.Figure(data=[trace_raw, trace_fit])

    # Basic titles so we know what we are looking at
    fig.update_layout(
        title="Sandbox: Minimal Plotly Graph",
        xaxis_title="Fake X (L_jun)",
        yaxis_title="Fake Y (Freq)",
    )

    fig.show()


if __name__ == "__main__":
    plot_sandbox()
