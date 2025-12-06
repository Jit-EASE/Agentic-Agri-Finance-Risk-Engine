from __future__ import annotations
import pandas as pd


def add_month_and_year(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    return df


def summarise_volatility(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    s = df.set_index("date")[value_col].asfreq("M").interpolate()
    out = s.to_frame("price")
    out["return"] = out["price"].pct_change()
    out["rolling_vol_6m"] = out["return"].rolling(6).std()
    out["rolling_vol_12m"] = out["return"].rolling(12).std()
    out["rolling_vol_24m"] = out["return"].rolling(24).std()
    out = out.reset_index()
    return out


def merge_climate_credit(
    credit_df: pd.DataFrame,
    climate_df: pd.DataFrame,
    on_col: str = "date",
) -> pd.DataFrame:
    credit_df = credit_df.copy()
    climate_df = climate_df.copy()
    credit_df[on_col] = pd.to_datetime(credit_df[on_col])
    climate_df[on_col] = pd.to_datetime(climate_df[on_col])
    merged = pd.merge_asof(
        credit_df.sort_values(on_col),
        climate_df.sort_values(on_col),
        on=on_col,
        direction="backward",
    )
    return merged
