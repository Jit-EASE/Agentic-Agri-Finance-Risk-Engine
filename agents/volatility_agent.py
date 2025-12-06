from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go

from core.data_loader import load_uploaded_csv, load_sample_price_data
from core.preprocessing import summarise_volatility
from utils.helpers import normalize_series, risk_band, colour_for_risk
from utils.plotly_spectre import spectre_template, add_crosshair, HOVER


def render_volatility_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Volatility Agent</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Maps seasonal and price volatility for key farm outputs. Rolling volatility feeds
        credit, insurance and subsidy logic.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload monthly price series (CSV with 'date' and one price column) or use AFRE sample data.",
        type=["csv"],
        key="volatility_upload",
    )

    if uploaded_file is not None:
        df_raw = load_uploaded_csv(uploaded_file)
    else:
        df_raw = load_sample_price_data()

    if df_raw is None or df_raw.empty:
        st.warning("No data available. Please upload a CSV file.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    price_cols = [c for c in df_raw.columns if c.lower() != "date"]
    if not price_cols:
        st.warning("No price columns found in dataset.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    price_col = st.selectbox("Select price column", price_cols, index=0)

    work = df_raw[["date", price_col]].rename(columns={price_col: "price"})
    df_vol = summarise_volatility(work, "price")

    vol_series = df_vol["rolling_vol_12m"].dropna()
    if vol_series.empty:
        st.warning("Not enough observations to compute rolling volatility.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    vol_norm = normalize_series(vol_series)
    vol_score = float(vol_norm.iloc[-1])
    band = risk_band(vol_score)
    band_colour = colour_for_risk(vol_score)
    latest_row = df_vol.loc[df_vol["rolling_vol_12m"].notna()].iloc[-1]

    col1, col2, col3 = st.columns([1.1, 1, 1])
    with col1:
        st.markdown('<div class="spectre-small-label">Current Volatility Band</div>', unsafe_allow_html=True)
        st.markdown(
            f"""            <div class="spectre-risk-chip" style="background:{band_colour}22; color:{band_colour}; margin-top:0.2rem;">
              {band.upper()}
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<div class="spectre-small-label">12m Rolling Volatility</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="spectre-metric">{latest_row["rolling_vol_12m"]:.3f}</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown('<div class="spectre-small-label">Observation Date</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:13px; margin-top:0.25rem;">{latest_row["date"].date()}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_vol["date"],
        y=df_vol["price"],
        mode="lines",
        name="Price",
        line=dict(width=2),
        hovertemplate=HOVER,
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_vol["date"],
        y=df_vol["rolling_vol_12m"],
        mode="lines",
        name="12m volatility",
        line=dict(width=1.5, dash="dash"),
        hovertemplate=HOVER,
        yaxis="y2",
    ))

    fig.update_layout(
        **spectre_template(),
        height=340,
        xaxis_title="Date",
        yaxis_title="Price",
        yaxis2=dict(
            title="Volatility",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )
    fig = add_crosshair(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """        <p style="font-size:11px; color:#9ca3af; margin-top:0.4rem;">
        Higher rolling volatility implies greater uncertainty around farm cashflows. AFRE feeds
        this signal into credit limits, insurance premiums and subsidy design.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "volatility_band": band,
        "volatility_score": round(vol_score, 3),
    }
