from __future__ import annotations
import plotly.graph_objects as go

HOVER = "<b>%{x}</b><br><span style='color:#38bdf8;'>%{y}</span><extra></extra>"


def spectre_template():
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, system-ui",
            size=12,
            color="#e5e7eb",
        ),
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.65)",
            font_size=12,
            font_family="Inter",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.07)",
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.07)",
            zeroline=False,
        ),
        margin=dict(l=10, r=10, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )


def add_crosshair(fig: go.Figure, x: bool = True, y: bool = True) -> go.Figure:
    hovermode = "x unified" if x and y else "x" if x else "y"
    fig.update_layout(
        hovermode=hovermode,
    )
    fig.update_xaxes(
        showspikes=True,
        spikemode="across+toaxis",
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="rgba(56,189,248,0.65)",
        spikethickness=1.2,
    )
    fig.update_yaxes(
        showspikes=True,
        spikemode="across+toaxis",
        spikesnap="cursor",
        spikedash="solid",
        spikecolor="rgba(56,189,248,0.65)",
        spikethickness=1.2,
    )
    return fig
