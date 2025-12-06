from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from core.data_loader import (
    load_uploaded_csv,
    load_sample_climate_data,
    load_sample_counterparty_data,
)
from core.preprocessing import merge_climate_credit
from utils.helpers import normalize_series, risk_band, colour_for_risk
from utils.plotly_spectre import spectre_template, add_crosshair, HOVER


def _compute_climate_adjusted_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["rainfall_index", "drought_index", "leverage_ratio"]:
        if col in df.columns:
            df[f"{col}_n"] = normalize_series(df[col].fillna(df[col].median()))
        else:
            df[f"{col}_n"] = 0.5

    df["climate_stress_raw"] = (
        0.4 * df["rainfall_index_n"]
        + 0.4 * df["drought_index_n"]
        + 0.2 * df["leverage_ratio_n"]
    )
    df["climate_adjusted_score"] = df["climate_stress_raw"].clip(0, 1)
    return df


def render_climate_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Climate-Adjustment Agent</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Computes climate-risk-adjusted creditworthiness by overlaying farm financials with
        climate indices. Intended for climate-aligned credit scoring and subsidy design.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        credit_file = st.file_uploader(
            "Upload farm credit / loan panel (CSV with date, farmer_id, leverage_ratio, loan_amount, etc.)",
            type=["csv"],
            key="climate_credit_upload",
        )
    with col_u2:
        climate_file = st.file_uploader(
            "Upload climate index data (CSV with date, rainfall_index, drought_index, etc.)",
            type=["csv"],
            key="climate_climate_upload",
        )

    if credit_file is not None:
        credit_df = load_uploaded_csv(credit_file)
    else:
        credit_df = load_sample_counterparty_data()

    if climate_file is not None:
        climate_df = load_uploaded_csv(climate_file)
    else:
        climate_df = load_sample_climate_data()

    if credit_df is None or climate_df is None:
        st.warning("Unable to load data. Please check your CSVs.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    merged = merge_climate_credit(credit_df, climate_df, on_col="date")
    merged = _compute_climate_adjusted_score(merged)

    farmer_scores = (
        merged.groupby("farmer_id", as_index=False)["climate_adjusted_score"]
        .mean()
        .rename(columns={"climate_adjusted_score": "mean_climate_score"})
    )

    if farmer_scores.empty:
        st.warning("No farmer records after merge.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    selected_farmer = st.selectbox(
        "Select farmer",
        options=sorted(farmer_scores["farmer_id"].unique()),
    )

    f_row = farmer_scores.loc[farmer_scores["farmer_id"] == selected_farmer].iloc[0]
    f_score = float(f_row["mean_climate_score"])
    f_band = risk_band(f_score)
    f_colour = colour_for_risk(f_score)

    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        st.markdown('<div class="spectre-small-label">Climate-Adjusted Band</div>', unsafe_allow_html=True)
        st.markdown(
            f"""            <div class="spectre-risk-chip" style="background:{f_colour}22; color:{f_colour}; margin-top:0.2rem;">
              {f_band.upper()}
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<div class="spectre-small-label">Mean Climate Risk Score</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="spectre-metric">{f_score:.2f}</div>',
            unsafe_allow_html=True,
        )
    with col3:
        n_obs = len(merged.loc[merged["farmer_id"] == selected_farmer])
        st.markdown('<div class="spectre-small-label">Observations</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:13px; margin-top:0.25rem;">{n_obs} months</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    f_series = merged.loc[merged["farmer_id"] == selected_farmer].sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=f_series["date"],
        y=f_series["climate_adjusted_score"],
        mode="lines+markers",
        name="Climate-adjusted score",
        hovertemplate=HOVER,
    ))
    fig.update_layout(
        **spectre_template(),
        height=320,
        xaxis_title="Date",
        yaxis_title="Score (0–1)",
        yaxis=dict(range=[0, 1]),
    )
    fig = add_crosshair(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """        <p style="font-size:11px; color:#9ca3af; margin-top:0.4rem;">
        Higher scores signal farms structurally exposed to climate shocks and leverage, even
        before conventional default indicators emerge.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "climate_score": round(f_score, 3),
        "farmer_id": int(selected_farmer),
    }
