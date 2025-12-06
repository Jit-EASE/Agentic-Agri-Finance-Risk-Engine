from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

from core.data_loader import load_sample_counterparty_data, load_uploaded_csv
from utils.helpers import normalize_series, risk_band, colour_for_risk
from utils.plotly_spectre import spectre_template, add_crosshair

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


def _train_pd_model(df: pd.DataFrame):
    df = df.copy()
    if "arrears_flag" not in df.columns:
        return None, None

    features = ["loan_amount", "age", "years_in_farming", "leverage_ratio"]
    features = [f for f in features if f in df.columns]
    if not features:
        return None, None

    X = df[features]
    y = df["arrears_flag"]

    for col in features:
        X[col] = normalize_series(X[col])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)

    return model, (features, auc, X_train)


def _plot_shap(features, contributions):
    from utils.plotly_spectre import spectre_template, add_crosshair

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=contributions,
        y=features,
        orientation="h",
        marker=dict(color="rgba(250,204,21,0.8)"),
        hovertemplate="<b>%{y}</b>: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        **spectre_template(),
        xaxis_title="Contribution to PD (log-odds scale)",
        height=320,
    )
    fig = add_crosshair(fig)
    return fig


def render_loan_sim_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">AI Loan Decision Simulator</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Simulates PD-based loan decisions and, where possible, uses SHAP-style explanations
        to highlight which features drive risk. This is a sandbox, not a policy engine.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload counterparty dataset (or use AFRE synthetic sample). Needs arrears_flag and basic features.",
        type=["csv"],
        key="loan_sim_upload",
    )

    if uploaded_file is not None:
        df = load_uploaded_csv(uploaded_file)
    else:
        df = load_sample_counterparty_data()

    if df is None or df.empty:
        st.warning("Dataset missing or empty.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    model, meta = _train_pd_model(df)
    if model is None:
        st.warning("Dataset missing arrears_flag or required features.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    features, auc, X_train = meta

    col_top1, col_top2 = st.columns([1, 1])
    with col_top1:
        st.markdown('<div class="spectre-small-label">Model AUC (hold-out)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="spectre-metric">{auc:.3f}</div>', unsafe_allow_html=True)
    with col_top2:
        st.markdown(
            """            <div class="spectre-small-label">Decision rule – stylised</div>
            <p style="font-size:12px; color:#9ca3af; margin-top:0.25rem;">
            For illustration, assume approval if PD &lt; 15%, conditional approval if 15–30%,
            and decline above 30%, subject to policy overrides.
            </p>
            """\,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        loan_amount = st.number_input("Loan amount (€)", min_value=5000.0, max_value=500000.0, value=120000.0, step=5000.0)
    with col_b:
        age = st.number_input("Farmer age", min_value=20, max_value=80, value=46)
    with col_c:
        years_in_farming = st.number_input("Years in farming", min_value=1, max_value=60, value=18)
    with col_d:
        leverage_ratio = st.slider("Leverage ratio", min_value=0.05, max_value=1.0, value=0.55, step=0.05)

    scenario = pd.DataFrame([{
        "loan_amount": loan_amount,
        "age": age,
        "years_in_farming": years_in_farming,
        "leverage_ratio": leverage_ratio,
    }])

    for col in features:
        combined = pd.concat([X_train[col], scenario[col]], ignore_index=True)
        scenario[col] = normalize_series(combined).iloc[-1]

    pd_prob = float(model.predict_proba(scenario[features])[:, 1][0])
    band = risk_band(pd_prob)
    colour = colour_for_risk(pd_prob)

    if pd_prob < 0.15:
        decision = "Approve"
    elif pd_prob < 0.30:
        decision = "Conditional – tighten terms / collateral"
    else:
        decision = "Decline (risk too high)"

    col_dec1, col_dec2, col_dec3 = st.columns([1.1, 1.1, 1.4])
    with col_dec1:
        st.markdown('<div class="spectre-small-label">PD (1-year, stylised)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="spectre-metric">{pd_prob:.2%}</div>', unsafe_allow_html=True)
    with col_dec2:
        st.markdown('<div class="spectre-small-label">Decision</div>', unsafe_allow_html=True)
        st.markdown(
            f"""            <div class="spectre-risk-chip" style="background:{colour}22; color:{colour}; margin-top:0.2rem;">
              {decision}
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with col_dec3:
        st.markdown(
            """            <div class="spectre-small-label">Governance note</div>
            <p style="font-size:12px; color:#9ca3af; margin-top:0.3rem;">
            This rule is illustrative only. Actual decision matrices should be approved by credit
            committees and integrated with policy, ESG and regulatory constraints.
            </p>
            """\,
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    if SHAP_AVAILABLE:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(scenario[features])[1][0]
        abs_vals = np.abs(shap_values)
        order = np.argsort(-abs_vals)
        feat_names = [features[i] for i in order]
        contribs = [shap_values[i] for i in order]

        fig = _plot_shap(feat_names, contribs)
        st.markdown(
            '<div class="spectre-small-label">Feature contributions (SHAP)</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """            <p style="font-size:11px; color:#9ca3af; margin-top:0.4rem;">
            Positive bars increase risk; negative bars reduce it, relative to a reference farmer
            in the training data.
            </p>
            """\,
            unsafe_allow_html=True,
        )
    else:
        st.info("Install the 'shap' package to see feature-level explanations.")

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "loan_sim_pd": round(pd_prob, 4),
        "loan_sim_decision": decision,
    }
