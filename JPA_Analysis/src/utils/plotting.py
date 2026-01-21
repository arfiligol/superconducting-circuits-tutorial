from __future__ import annotations

from typing import Any

import plotly.graph_objects as go  # type: ignore

MATPLOTLIB_FONT_SIZE = 16
MATPLOTLIB_TITLE_SIZE = 28

PLOTLY_FONT_SIZE = 18
PLOTLY_TITLE_FONT_SIZE = 30
PLOTLY_LEGEND_FONT_SIZE = 18


def apply_plotly_layout(
    fig: go.Figure,
    *,
    title: str,
    xaxis_title: str,
    yaxis_title: str,
    legend_title: str = "Legend",
    x_range: tuple[float, float] | None = None,
    y_range: tuple[float, float] | None = None,
    x_tickformat: str | None = None,
    y_tickformat: str | None = None,
    showlegend: bool = True,
    width: int | None = None,
    height: int | None = None,
) -> go.Figure:
    fig.update_layout(
        autosize=width is None and height is None,
        width=width,
        height=height,
        title=dict(
            text=title,
            xanchor="center",
            yanchor="top",
            x=0.5,
            font=dict(size=PLOTLY_TITLE_FONT_SIZE),
        ),
        font=dict(size=PLOTLY_FONT_SIZE),
        showlegend=showlegend,
        legend=dict(
            title=dict(text=legend_title, font=dict(size=PLOTLY_LEGEND_FONT_SIZE)),
            font=dict(size=PLOTLY_LEGEND_FONT_SIZE),
        ),
        margin=dict(l=70, r=40, t=80, b=70),
    )

    xaxis: dict[str, Any] = {"title_text": xaxis_title}
    if x_range is not None:
        xaxis["range"] = list(x_range)
    if x_tickformat is not None:
        xaxis["tickformat"] = x_tickformat

    yaxis: dict[str, Any] = {"title_text": yaxis_title}
    if y_range is not None:
        yaxis["range"] = list(y_range)
    if y_tickformat is not None:
        yaxis["tickformat"] = y_tickformat

    fig.update_layout(xaxis=xaxis, yaxis=yaxis)
    return fig


def plotly_default_config(title: str) -> dict[str, Any]:
    return {
        "scrollZoom": True,
        "responsive": True,
        "staticPlot": False,
        "displayModeBar": True,
        "toImageButtonOptions": {"format": "png", "filename": title, "scale": 5},
        "modeBarButtonsToAdd": ["drawline", "eraseshape"],
    }
