from __future__ import annotations
import streamlit as st

from ui.layout import set_page, inject_spectre_css, render_header, render_footer

from agents.volatility_agent import render_volatility_agent
from agents.climate_agent import render_climate_agent
from agents.counterparty_agent import render_counterparty_agent
from agents.gpt_agent import render_gpt_agent

from agents.reg_compliance_agent import render_reg_compliance_agent
from agents.subsidy_agent import render_subsidy_agent
from agents.loan_sim_agent import render_loan_sim_agent
from agents.portfolio_agent import render_portfolio_agent
from agents.csv_agent import render_csv_agent


def main():
    set_page()
    inject_spectre_css()

    context_data = {
        "volatility_band": None,
        "volatility_score": None,
        "climate_score": None,
        "pd_score": None,
        "farmer_id": None,
        "reg_compliance_band": None,
        "reg_compliance_score": None,
        "subsidy_intensity": None,
        "loan_sim_pd": None,
        "loan_sim_decision": None,
        "portfolio_total_ead": None,
        "portfolio_total_el": None,
        "portfolio_hhi": None,
        "csv_filename": None,
    }

    with st.sidebar:
        st.markdown(
            """            <div style="padding:0.6rem 0.4rem;">
              <div style="font-size:12px; color:#9ca3af; text-transform:uppercase; letter-spacing:0.14em;">
                AFRE Console
              </div>
              <div style="font-size:11px; color:#6b7280; margin-top:0.35rem;">
                Agentic Agri-Finance Risk Engine – prototype stack.
              </div>
            </div>
            """\,
            unsafe_allow_html=True,
        )

        mode = st.radio(
            "Select module",
            options=[
                "Volatility Agent",
                "Climate-Adjustment Agent",
                "Counterparty Agent",
                "Regulatory Compliance AI",
                "Subsidy Optimisation Engine",
                "AI Loan Decision Simulator",
                "Multi-Farm Portfolio Risk Agent",
                "Universal CSV Intelligence Agent",
                "Narrative Intelligence Agent (GPT-4o-mini)",
            ],
            index=0,
        )

    render_header()

    if mode == "Volatility Agent":
        result = render_volatility_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Climate-Adjustment Agent":
        result = render_climate_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Counterparty Agent":
        result = render_counterparty_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Regulatory Compliance AI":
        result = render_reg_compliance_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Subsidy Optimisation Engine":
        result = render_subsidy_agent(context_data=context_data)
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "AI Loan Decision Simulator":
        result = render_loan_sim_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Multi-Farm Portfolio Risk Agent":
        result = render_portfolio_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Universal CSV Intelligence Agent":
        result = render_csv_agent()
        if isinstance(result, dict):
            context_data.update(result)

    elif mode == "Narrative Intelligence Agent (GPT-4o-mini)":
        render_gpt_agent(context_data)

    render_footer()


if __name__ == "__main__":
    main()
