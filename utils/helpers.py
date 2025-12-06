from __future__ import annotations
import pandas as pd
import numpy as np


def normalize_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    return (s - s.min()) / (s.max() - s.min() + 1e-9)


def risk_band(score: float) -> str:
    if score < 0.33:
        return "Low"
    elif score < 0.66:
        return "Medium"
    return "High"


def colour_for_risk(score: float) -> str:
    if score < 0.33:
        return "#4CAF50"
    elif score < 0.66:
        return "#FFC107"
    return "#F44336"
