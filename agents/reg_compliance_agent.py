from __future__ import annotations
import streamlit as st
from utils.helpers import risk_band, colour_for_risk


def _compute_compliance_risk(ai_risk_level, automation_level, esg_orientation, portfolio_criticality):
    base = {
        "Low": 0.25,
        "Limited": 0.45,
        "High": 0.75,
    }.get(ai_risk_level, 0.45)

    if automation_level == "Supportive / human-in-the-loop":
        base -= 0.05
    elif automation_level == "Fully automated decisions (with audit trail)":
        base += 0.05
    elif automation_level == "Fully automated – thin or no oversight":
        base += 0.15

    if portfolio_criticality == "Idiosyncratic / small exposures":
        base -= 0.05
    elif portfolio_criticality == "Core book / large share of balance sheet":
        base += 0.10

    if esg_orientation == "ESG positive / impact-aligned":
        base -= 0.05
    elif esg_orientation == "ESG neutral":
        base += 0.0
    elif esg_orientation == "ESG controversial / transition risk":
        base += 0.08

    return float(max(0.0, min(1.0, base)))


def render_reg_compliance_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Regulatory Compliance AI</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Stylised EU AI Act + ESG + Basel III lens over AFRE use-cases. This is a conceptual
        tool to structure dialogue with legal, compliance and supervisors – not legal advice.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        use_case = st.selectbox(
            "Primary AFRE use-case",
            [
                "Credit scoring for individual farm loans",
                "Pricing and underwriting for agri-insurance",
                "Subsidy targeting and eligibility screening",
                "Macro stress-testing / supervisory analytics",
            ],
        )

        ai_risk_level = st.selectbox(
            "EU AI Act – indicative risk level",
            ["Low", "Limited", "High"],
            index=1,
        )

        automation_level = st.selectbox(
            "Automation level",
            [
                "Supportive / human-in-the-loop",
                "Fully automated decisions (with audit trail)",
                "Fully automated – thin or no oversight",
            ],
        )

    with col2:
        portfolio_criticality = st.selectbox(
            "Portfolio materiality (Basel lens)",
            [
                "Idiosyncratic / small exposures",
                "Material sub-portfolio",
                "Core book / large share of balance sheet",
            ],
        )

        esg_orientation = st.selectbox(
            "ESG orientation of target segment",
            [
                "ESG positive / impact-aligned",
                "ESG neutral",
                "ESG controversial / transition risk",
            ],
        )

        jurisdiction = st.selectbox(
            "Jurisdiction mix",
            [
                "EU only",
                "EU + non-EU (EEA / UK)",
                "Global portfolio (incl. EM / high-risk)",
            ],
        )

    score = _compute_compliance_risk(ai_risk_level, automation_level, esg_orientation, portfolio_criticality)
    band = risk_band(score)
    colour = colour_for_risk(score)

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    colr1, colr2, colr3 = st.columns([1.2, 1, 1.4])
    with colr1:
        st.markdown('<div class="spectre-small-label">Compliance Risk Band</div>', unsafe_allow_html=True)
        st.markdown(
            f"""            <div class="spectre-risk-chip" style="background:{colour}22; color:{colour}; margin-top:0.2rem;">
              {band.upper()}
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with colr2:
        st.markdown('<div class="spectre-small-label">Composite Score</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="spectre-metric">{score:.2f}</div>',
            unsafe_allow_html=True,
        )
    with colr3:
        st.markdown(
            """            <div class="spectre-small-label">Indicative implications</div>
            <ul style="margin-top:0.3rem; font-size:12px; color:#9ca3af; padding-left:1.1rem;">
              <li>Higher scores imply stronger governance, documentation and audit expectations.</li>
              <li>Interaction between EU AI Act risk layer and Basel capital planning.</li>
              <li>ESG profile can alter supervisory appetite and disclosure needs.</li>
            </ul>
            """\,
            unsafe_allow_html=True,
        )

    st.markdown(
        """        <p style="font-size:11px; color:#6b7280; margin-top:0.4rem;">
        Final classification should be determined by internal legal, risk and compliance
        functions aligned with EU AI Act, CRR/CRD and local supervisory guidance.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "reg_compliance_band": band,
        "reg_compliance_score": round(score, 3),
        "reg_use_case": use_case,
        "reg_jurisdiction": jurisdiction,
    }
