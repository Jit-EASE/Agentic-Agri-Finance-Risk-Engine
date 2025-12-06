from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np


def _auto_clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    for col in df.columns:
        if df[col].dtype == object:
            if col.lower() in ("date", "dt", "timestamp") or "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

    for col in df.columns:
        if df[col].dtype == object:
            cleaned = df[col].str.replace(",", "", regex=False).str.replace("€", "", regex=False).str.strip()
            try:
                df[col] = pd.to_numeric(cleaned)
            except Exception:
                pass

    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            df[f"{col}_outlier_flag"] = ((df[col] < q1 - 3 * iqr) | (df[col] > q3 + 3 * iqr)).astype(int)

    return df


def render_csv_agent():
    st.markdown('<div class="spectre-card">', unsafe_allow_html=True)

    st.markdown(
        """        <div class="spectre-small-label">Universal CSV Intelligence Agent</div>
        <p style="font-size:12px; color:#9ca3af; margin-top:0.2rem;">
        Ingests any CSV, infers basic structure, and performs light-touch cleaning:
        column trimming, date parsing, numeric conversion, and simple outlier flags.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload any CSV file",
        type=["csv"],
        key="csv_universal_upload",
    )

    if uploaded_file is None:
        st.info("Upload a CSV to see profiling and cleaning.")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    try:
        df_raw = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        return {}

    st.markdown('<div class="spectre-small-label" style="margin-top:0.5rem;">Raw snapshot</div>', unsafe_allow_html=True)
    st.dataframe(df_raw.head(), use_container_width=True)

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)

    st.markdown('<div class="spectre-small-label">Structure & missingness</div>', unsafe_allow_html=True)
    info_cols = []
    for col in df_raw.columns:
        missing = df_raw[col].isna().mean()
        info_cols.append((col, str(df_raw[col].dtype), f"{missing:.1%}"))

    info_df = pd.DataFrame(info_cols, columns=["Column", "Dtype", "Missing share"])
    st.dataframe(info_df, use_container_width=True)

    df_clean = _auto_clean(df_raw)

    st.markdown("<hr style='border-color: rgba(148,163,184,0.25);'>", unsafe_allow_html=True)
    st.markdown('<div class="spectre-small-label">Cleaned preview</div>', unsafe_allow_html=True)
    st.dataframe(df_clean.head(), use_container_width=True)

    st.markdown(
        """        <p style="font-size:11px; color:#9ca3af; margin-top:0.4rem;">
        This agent is intentionally conservative – it does not impute values or drop rows by default.
        Its role is to standardise basic types so AFRE agents and econometric models can attach on top.
        </p>
        """\,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return {
        "csv_rows": int(df_clean.shape[0]),
        "csv_cols": int(df_clean.shape[1]),
        "csv_filename": getattr(uploaded_file, "name", "unknown.csv"),
    }
