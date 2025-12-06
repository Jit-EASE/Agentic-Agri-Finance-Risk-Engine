from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.ensemble import RandomForestClassifier

from core.data_loader import load_uploaded_csv, load_sample_counterparty_data
from utils.helpers import normalize_series, risk_band, colour_for_risk
from utils.plotly_spectre import spectre_template, add_crosshair, HOVER


def _train_default_model(df: pd.DataFrame):
    df = df.copy()
    candidate_features = ["loan_amount", "age", "years_in_farming", "leverage_ratio"]
    features = [c for c in candidate_features if c in df.columns]

    if "arrears_flag" not in df.columns or len(features) == 0:
        return None, None, None

    X = df[features]
    y = df["arrears_flag"]

    for col in features:
        X[col] = normalize_series(X[col])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=5,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)

    return model, auc, (fpr, tpr, features, X_train)


def render_counterparty_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Counterparty Agent</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Predicts farmer repayment behaviour with a simple PD model. Designed as a placeholder
        for your production-grade PD/LGD engines.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload counterparty panel (CSV with arrears_flag, loan_amount, age, years_in_farming, leverage_ratio, etc.)",
        type=["csv"],
        key="counterparty_upload",
    )

    if uploaded_file is not None:
        df_raw = load_uploaded_csv(uploaded_file)
    else:
        df_raw = load_sample_counterparty_data()

    if df_raw is None or df_raw.empty:
        st.warning("No data available. Please upload a CSV.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    model, auc, roc_data = _train_default_model(df_raw)

    if model is None:
        st.warning("Dataset missing required columns or arrears_flag.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    fpr, tpr, features, X_train = roc_data

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="spectre-small-label">Model Type</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:13px; margin-top:0.25rem;">Random Forest, balanced classes.</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown('<div class="spectre-small-label">Out-of-sample AUC</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="spectre-metric">{auc:.3f}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr,
        y=tpr,
        mode="lines",
        name="ROC curve",
        line=dict(width=2),
        hovertemplate=HOVER,
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Random",
        line=dict(width=1, dash="dash"),
        hovertemplate=HOVER,
    ))
    fig.update_layout(
        **spectre_template(),
        height=280,
        xaxis_title="False positive rate",
        yaxis_title="True positive rate",
    )
    fig = add_crosshair(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="spectre-small-label" style="margin-top:0.6rem;">Scenario Probe</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        loan_amount = st.number_input("Loan amount (€)", min_value=5_000.0, max_value=500_000.0, value=100_000.0)
    with col_b:
        age = st.number_input("Farmer age", min_value=20, max_value=80, value=45)
    with col_c:
        years_in_farming = st.number_input("Years in farming", min_value=1, max_value=60, value=15)
    with col_d:
        leverage_ratio = st.slider("Leverage ratio", min_value=0.05, max_value=1.0, value=0.5, step=0.05)

    scenario = pd.DataFrame([{
        "loan_amount": loan_amount,
        "age": age,
        "years_in_farming": years_in_farming,
        "leverage_ratio": leverage_ratio,
    }])

    for col in features:
        combined = pd.concat([X_train[col], scenario[col]], ignore_index=True)
        scenario[col] = normalize_series(combined).iloc[-1]

    prob_default = float(model.predict_proba(scenario[features])[:, 1][0])
    band = risk_band(prob_default)
    colour = colour_for_risk(prob_default)

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    colx, coly = st.columns([1, 1.4])
    with colx:
        st.markdown('<div class="spectre-small-label">PD (1-year, illustrative)</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="spectre-metric">{prob_default:.2%}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="spectre-small-label" style="margin-top:0.6rem;">Risk band</div>', unsafe_allow_html=True)
        st.markdown(
            f"""            <div class="spectre-risk-chip" style="background:{colour}22; color:{colour}; margin-top:0.2rem;">
              {band.upper()}
            </div>
            """\,
            unsafe_allow_html=True,
        )
    with coly:
        st.markdown(
            """            <p style="font-size:11px; color:#9ca3af; margin-top:0.4rem;">
            This is a stylised probability of default based on a small feature set. AFRE is
            designed to be swapped onto your production-grade PD engines while preserving UI
            and banding logic.
            </p>
            """\,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "pd_score": round(prob_default, 4),
        "farmer_id": None,
    }
