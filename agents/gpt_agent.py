from __future__ import annotations
import streamlit as st
from openai import OpenAI
from core.secrets import OPENAI_API_KEY


def get_client():
    return OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def ask_gpt(prompt: str) -> str:
    client = get_client()
    if client is None:
        return "OpenAI API key not configured. Set OPENAI_API_KEY in your environment to enable this agent."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the AFRE Narrative Intelligence Agent. "
                        "Explain financial risk, agricultural volatility, climate-adjusted creditworthiness, "
                        "repayment behaviour, subsidies and regulation in clear, professional, academic-style "
                        "language suitable for risk committees, supervisors and policymakers. Do not use markdown "
                        "headings; respond as continuous prose."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.25,
            max_tokens=700,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AFRE-GPT agent could not generate output. Error: {e}"


def render_gpt_agent(context_data: dict):
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Narrative Intelligence Agent (GPT‑4o‑mini)</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Converts AFRE’s quantitative outputs into a narrative suitable for credit committees,
        supervisors, boards, or policy audiences.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="spectre-small-label" style="margin-top:0.7rem;">Generate Narrative</div>',
        unsafe_allow_html=True,
    )

    default_prompt = (
        "Explain the combined implications of current volatility, climate-adjusted risk, PD, "
        "subsidy intensity and portfolio risk, as if writing a concise note for a bank risk committee."
    )

    user_prompt = st.text_area(
        "Describe what you want AFRE to interpret or explain.",
        value=default_prompt,
        height=120,
        key="gpt_custom_prompt",
    )

    combine_context = st.checkbox(
        "Include AFRE quantitative context automatically",
        value=True,
    )

    if st.button("Run AFRE Narrative Agent"):
        final_prompt = user_prompt.strip()

        if combine_context:
            final_prompt += "

AFRE Context (JSON-like):
"
            for k, v in context_data.items():
                final_prompt += f"- {k}: {v}
"

        with st.spinner("AFRE Narrative Agent reasoning…"):
            output = ask_gpt(final_prompt)

        st.markdown(
            f"""            <div style="margin-top:0.8rem; padding:1rem; border-radius:12px; background:rgba(255,255,255,0.04);">
                <div style="font-size:12px; color:#9ca3af; margin-bottom:0.3rem;">
                    Explanation
                </div>
                <div style="font-size:13px; line-height:1.55;">
                    {output}
                </div>
            </div>
            """\,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
