from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from core.data_loader import load_uploaded_csv, load_sample_counterparty_data
from utils.helpers import risk_band
from utils.plotly_spectre import spectre_template, add_crosshair, HOVER


def _build_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "loan_amount" not in df.columns:
        df["loan_amount"] = np.random.uniform(20000, 200000, size=len(df))
    if "farmer_id" not in df.columns:
        df["farmer_id"] = np.arange(1, len(df) + 1)

    if "arrears_flag" in df.columns:
        df["pd"] = 0.05 + 0.20 * df["arrears_flag"]
    else:
        df["pd"] = 0.1

    df["lgd"] = 0.45
    df["ead"] = df["loan_amount"]
    df["el"] = df["pd"] * df["lgd"] * df["ead"]
    df["pd_band"] = df["pd"].apply(risk_band)
    return df


def render_portfolio_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Multi-Farm Portfolio Risk Agent</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Aggregates farm-level exposures into a stylised portfolio view: expected loss, concentration,
        and risk buckets.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload portfolio CSV (farmer_id, loan_amount, arrears_flag, etc.) or use AFRE sample.",
        type=["csv"],
        key="portfolio_upload",
    )

    if uploaded_file is not None:
        df_raw = load_uploaded_csv(uploaded_file)
    else:
        df_raw = load_sample_counterparty_data()

    if df_raw is None or df_raw.empty:
        st.warning("No portfolio data available.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    df = _build_portfolio(df_raw)

    total_ead = float(df["ead"].sum())
    total_el = float(df["el"].sum())
    weights = df["ead"] / max(total_ead, 1e-9)
    hhi = float((weights**2).sum())
    band_hhi = "Concentrated" if hhi > 0.18 else "Moderate" if hhi > 0.1 else "Well diversified"

    col1, col2, col3 = st.columns([1.1, 1.1, 1.2])
    with col1:
        st.markdown('<div class="spectre-small-label">Total exposure (EAD)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="spectre-metric">€{total_ead:,.0f}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="spectre-small-label">Portfolio EL (annual)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="spectre-metric">€{total_el:,.0f}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="spectre-small-label">Concentration (HHI)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="spectre-metric">{hhi:.3f}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:11px; color:#9ca3af; margin-top:0.2rem;">{band_hhi}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    band_summary = (
        df.groupby("pd_band", as_index=False)[["ead", "el"]]
        .sum()
        .sort_values("ead", ascending=False)
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=band_summary["pd_band"],
        y=band_summary["ead"],
        name="Exposure (EAD)",
        hovertemplate=HOVER,
    ))
    fig.add_trace(go.Bar(
        x=band_summary["pd_band"],
        y=band_summary["el"],
        name="Expected Loss",
        hovertemplate=HOVER,
    ))
    fig.update_layout(
        **spectre_template(),
        barmode="group",
        height=320,
        xaxis_title="PD band",
        yaxis_title="€",
    )
    fig = add_crosshair(fig, y=False)
    st.markly_chart = st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """        <p style="font-size:11px; color:#9ca3af; margin-top:0.4rem;">
        This view highlights how much of the book sits in higher PD bands, and where expected
        loss is concentrated. In a full implementation, this would link to capital, pricing and
        portfolio strategy.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "portfolio_total_ead": round(total_ead, 2),
        "portfolio_total_el": round(total_el, 2),
        "portfolio_hhi": round(hhi, 3),
    }
