from __future__ import annotations
import streamlit as st
from utils.helpers import risk_band, colour_for_risk


def _compute_subsidy_intensity(hectares, climate_score, volatility_band, young_farmer, eco_scheme, region_productivity):
    base = 0.35
    base += 0.25 * climate_score

    if volatility_band == "Low":
        base += 0.02
    elif volatility_band == "Medium":
        base += 0.07
    elif volatility_band == "High":
        base += 0.12

    if eco_scheme:
        base += 0.06
    if young_farmer:
        base += 0.08

    if region_productivity == "Marginal / low productivity":
        base += 0.08
    elif region_productivity == "Core / average productivity":
        base += 0.04
    else:
        base -= 0.04

    if hectares > 80:
        base -= 0.06
    if hectares > 150:
        base -= 0.08

    return float(max(0.0, min(1.0, base)))


def render_subsidy_agent(context_data: dict | None = None):
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Subsidy Optimisation Engine (stylised CAP I & II)</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Uses volatility, climate-adjusted risk and farm structure to suggest a stylised
        subsidy "intensity" indicator that can be mapped to payment envelopes.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    volatility_band_default = context_data.get("volatility_band", "Medium") if context_data else "Medium"
    climate_score_default = context_data.get("climate_score", 0.4) if context_data else 0.4

    col1, col2, col3 = st.columns(3)
    with col1:
        hectares = st.number_input("Eligible hectares", min_value=1.0, max_value=500.0, value=40.0, step=1.0)
        volatility_band = st.selectbox(
            "Volatility band (from AFRE or expert judgement)",
            ["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(volatility_band_default)
            if volatility_band_default in ["Low", "Medium", "High"] else 1,
        )

    with col2:
        climate_score = st.slider(
            "Climate-adjusted risk score (0–1)",
            min_value=0.0,
            max_value=1.0,
            value=float(climate_score_default),
            step=0.05,
        )
        region_productivity = st.selectbox(
            "Region productivity profile",
            [
                "Marginal / low productivity",
                "Core / average productivity",
                "High productivity / intensive",
            ],
        )

    with col3:
        young_farmer = st.checkbox("Young farmer / generational renewal", value=False)
        eco_scheme = st.checkbox("Participating in eco-schemes", value=True)

    intensity = _compute_subsidy_intensity(
        hectares, climate_score, volatility_band, young_farmer, eco_scheme, region_productivity
    )
    band = risk_band(intensity)
    colour = colour_for_risk(intensity)

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    colr1, colr2, colr3 = st.columns([1.2, 1, 1.6])
    with colr1:
        st.markdown('<div class="spectre-small-label">Subsidy Intensity Band</div>', unsafe_allow_html=True)
        st.markdown(
            f"""            <div class="spectre-risk-chip" style="background:{colour}22; color:{colour}; margin-top:0.2rem;">
              {band.upper()}
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with colr2:
        st.markdown('<div class="spectre-small-label">Stylised Intensity (0–1)</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="spectre-metric">{intensity:.2f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:11px; color:#9ca3af; margin-top:0.3rem;">Higher values → stronger case for support.</div>',
            unsafe_allow_html=True,
        )
    with colr3:
        st.markdown(
            """            <div class="spectre-small-label">Interpretation</div>
            <p style="font-size:12px; color:#9ca3af; margin-top:0.25rem;">
            This indicator can be used to rank farms or segments for targeting of Pillar I top-ups,
            eco-scheme bonuses, or Pillar II measures, subject to budget and policy constraints.
            </p>
            """\,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "subsidy_intensity": round(intensity, 3),
        "subsidy_band": band,
    }
