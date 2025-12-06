from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Optional


def load_uploaded_csv(uploaded_file) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        return None
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception:
        return None


def load_sample_price_data() -> pd.DataFrame:
    rng = pd.date_range("2015-01-01", periods=120, freq="M")
    # crude trend + seasonality
    trend = (rng.year - 2015) * 0.5
    season = (rng.month % 12) * 0.3
    noise = np.random.normal(0, 0.5, size=len(rng))
    df = pd.DataFrame({
        "date": rng,
        "milk_price": 30 + trend + season + noise,
    })
    return df


def load_sample_climate_data() -> pd.DataFrame:
    rng = pd.date_range("2010-01-01", periods=180, freq="M")
    rain_base = 100 + 10 * np.sin(np.linspace(0, 6.28 * 4, len(rng)))
    drought_base = 50 + 8 * np.cos(np.linspace(0, 6.28 * 3, len(rng)))
    df = pd.DataFrame({
        "date": rng,
        "rainfall_index": rain_base + np.random.normal(0, 3, len(rng)),
        "drought_index": drought_base + np.random.normal(0, 2, len(rng)),
    })
    return df


def load_sample_counterparty_data(n: int = 300) -> pd.DataFrame:
    rng = pd.date_range("2018-01-01", periods=n, freq="M")
    df = pd.DataFrame({
        "farmer_id": np.random.randint(1, 60, size=n),
        "date": rng,
        "loan_amount": np.random.uniform(20_000, 200_000, size=n),
        "age": np.random.randint(25, 65, size=n),
        "years_in_farming": np.random.randint(3, 40, size=n),
        "leverage_ratio": np.random.uniform(0.1, 0.9, size=n),
        "arrears_flag": np.random.binomial(1, p=0.22, size=n),
    })
    return df
