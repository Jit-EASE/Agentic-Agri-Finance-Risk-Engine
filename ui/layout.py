from __future__ import annotations
import streamlit as st
from core.config import APP_NAME, APP_TAGLINE


def set_page():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="📊",
        layout="wide",
    )


def inject_spectre_css():
    st.markdown(
        """        <style>
        html, body, [class*="css"]  {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
            font-size: 13px;
        }

        .main {
            background: radial-gradient(circle at top, #191d2b 0, #06070b 45%, #020308 100%);
            color: #f2f2f5;
        }

        .spectre-card {
            border-radius: 18px;
            padding: 1.1rem 1.3rem;
            border: 1px solid rgba(255,255,255,0.06);
            background: linear-gradient(135deg, rgba(12,16,32,0.95), rgba(8,10,20,0.98));
            box-shadow: 0 14px 40px rgba(0,0,0,0.6);
        }

        .spectre-tagline {
            font-size: 11px;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #9ca3af;
        }

        .spectre-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            border: 1px solid rgba(148,163,184,0.45);
            font-size: 11px;
            color: #e5e7eb;
            background: radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent);
            margin-right: 0.4rem;
            margin-bottom: 0.2rem;
        }

        .spectre-risk-chip {
            padding: 0.08rem 0.5rem;
            border-radius: 999px;
            font-size: 11px;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .spectre-small-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #9ca3af;
        }

        .spectre-metric {
            font-size: 22px;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] {
            background: radial-gradient(circle at top, #050716 0, #02030a 60%, #000 100%);
            border-right: 1px solid rgba(148,163,184,0.35);
        }

        #MainMenu, header, footer {visibility: hidden;}
        </style>
        """\,
        unsafe_allow_html=True,
    )


def render_header():
    col1, col2 = st.columns([4, 2])
    with col1:
        st.markdown(
            f"""            <div class="spectre-card">
              <div class="spectre-tagline">AGENTIC AGRI-FINANCE RISK ENGINE</div>
              <div style="display:flex; align-items:baseline; gap:0.5rem; margin-top:0.4rem;">
                <h2 style="margin:0; font-weight:550;">{APP_NAME}</h2>
              </div>
              <p style="margin-top:0.35rem; color:#9ca3af; font-size:13px;">
                {APP_TAGLINE}. Built for credit scoring, farm loans, insurance and subsidy design.
              </p>
              <div style="margin-top:0.4rem;">
                <span class="spectre-pill">Volatility Agent</span>
                <span class="spectre-pill">Climate-Adjustment Agent</span>
                <span class="spectre-pill">Counterparty Agent</span>
                <span class="spectre-pill">Compliance & Subsidy</span>
              </div>
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """            <div class="spectre-card" style="height:100%;">
              <div class="spectre-small-label">Run Mode</div>
              <div style="font-size:12px; color:#9ca3af;">Prototype – synthetic data with upload override.</div>
              <div style="margin-top:0.7rem;" class="spectre-small-label">Pipeline</div>
              <ul style="margin-top:0.2rem; padding-left:1.1rem; font-size:12px; color:#9ca3af;">
                <li>Ingest → Clean → Feature engineering</li>
                <li>Econometric + ML scoring</li>
                <li>Risk banding, policy & narrative overlays</li>
              </ul>
            </div>
            """\,
            unsafe_allow_html=True,
        )


def render_footer():
    st.markdown(
        """        <div style="text-align:right; margin-top:0.8rem; font-size:11px; color:#6b7280;">
          AFRE • Prototype only – not investment advice.
        </div>
        """\,
        unsafe_allow_html=True,
    )
