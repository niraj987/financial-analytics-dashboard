import pandas as pd
import numpy as np
from datetime import timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# ─────────────────────────────────────────────────────────────────────────────
# RFM  ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates Recency, Frequency, and Monetary values for each customer."""
    snapshot_date = df["InvoiceDate"].max() + timedelta(days=1)

    rfm = (
        df.groupby("Customer ID")
        .agg(
            Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
            Frequency=("Invoice", "nunique"),
            MonetaryValue=("Revenue", "sum"),
        )
        .reset_index()
    )
    # Keep only profitable customers
    rfm = rfm[rfm["MonetaryValue"] > 0].copy()
    return rfm


def segment_customers(rfm: pd.DataFrame) -> pd.DataFrame:
    """Segments customers using quintile-based RFM scores."""
    quantiles = rfm[["Recency", "Frequency", "MonetaryValue"]].quantile(
        [0.2, 0.4, 0.6, 0.8]
    ).to_dict()

    def r_score(x, p, d):
        if x <= d[p][0.2]:   return 5
        elif x <= d[p][0.4]: return 4
        elif x <= d[p][0.6]: return 3
        elif x <= d[p][0.8]: return 2
        else:                 return 1

    def fm_score(x, p, d):
        if x <= d[p][0.2]:   return 1
        elif x <= d[p][0.4]: return 2
        elif x <= d[p][0.6]: return 3
        elif x <= d[p][0.8]: return 4
        else:                 return 5

    out = rfm.copy()
    out["R"] = out["Recency"].apply(r_score,       args=("Recency",       quantiles))
    out["F"] = out["Frequency"].apply(fm_score,    args=("Frequency",     quantiles))
    out["M"] = out["MonetaryValue"].apply(fm_score, args=("MonetaryValue", quantiles))
    out["RFM_Score"] = out["R"].map(str) + out["F"].map(str) + out["M"].map(str)

    def label(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4 and m >= 4:   return "🏆 Champions"
        if r >= 3 and f >= 3 and m >= 3:   return "💎 Loyal Customers"
        if r >= 4 and f <= 2:              return "🌱 Potential Loyalists"
        if r <= 2 and f >= 4:              return "⚠️ At Risk (Churning)"
        if r <= 2 and f <= 2:              return "💤 Sleepers / Lost"
        return "📊 Average"

    out["Segment"] = out.apply(label, axis=1)

    # Churn risk score (higher = more likely to churn)
    out["Churn_Risk_Score"] = round(
        (out["Recency"] / out["Recency"].max()) * 60
        + ((5 - out["F"]) / 4) * 40,
        1,
    )
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER LIFETIME VALUE
# ─────────────────────────────────────────────────────────────────────────────

def calculate_clv(rfm: pd.DataFrame, lifespan_years: int = 3) -> pd.DataFrame:
    """Appends a simplified CLV column to the RFM dataframe."""
    avg_purchase_value = rfm["MonetaryValue"] / rfm["Frequency"].clip(lower=1)
    purchase_frequency = rfm["Frequency"] / (rfm["Recency"].clip(lower=1) / 365)
    clv = avg_purchase_value * purchase_frequency * lifespan_years
    rfm = rfm.copy()
    rfm["CLV"] = clv.clip(lower=0).round(2)
    return rfm


# ─────────────────────────────────────────────────────────────────────────────
# ABC / PARETO  ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def perform_abc_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """ABC classification of products by revenue contribution."""
    prod = (
        df.groupby("Description")["Revenue"]
        .sum()
        .reset_index()
        .query("Revenue > 0")
        .sort_values("Revenue", ascending=False)
        .reset_index(drop=True)
    )
    prod["Cumulative_Revenue"] = prod["Revenue"].cumsum()
    total = prod["Revenue"].sum()
    prod["Cumulative_Pct"] = prod["Cumulative_Revenue"] / total

    def abc(p):
        if p <= 0.70: return "A – High Value"
        if p <= 0.90: return "B – Medium Value"
        return "C – Low Value"

    prod["ABC_Class"] = prod["Cumulative_Pct"].apply(abc)
    return prod


# ─────────────────────────────────────────────────────────────────────────────
# REVENUE  FORECASTING
# ─────────────────────────────────────────────────────────────────────────────

def forecast_revenue(df: pd.DataFrame, periods: int = 12):
    """
    Holt-Winters weekly revenue forecast.
    Returns (historical_df, forecast_df).
    Falls back to additive-only model when < 2 full seasons of data.
    """
    weekly = df.resample("W", on="InvoiceDate")["Revenue"].sum()
    weekly = weekly[weekly > 0]

    n = len(weekly)
    hist_df = weekly.reset_index()

    if n < 24:
        return hist_df, pd.DataFrame()

    # Use seasonal model only when we have at least ~2 full years
    use_seasonal = n >= 104
    try:
        if use_seasonal:
            model = ExponentialSmoothing(
                weekly, trend="add", seasonal="add", seasonal_periods=52
            )
        else:
            model = ExponentialSmoothing(weekly, trend="add", seasonal=None)
        fit   = model.fit(optimized=True)
        fc    = fit.forecast(periods)
    except Exception:
        # Ultimate fallback – simple linear extrapolation
        slope  = (weekly.iloc[-1] - weekly.iloc[-8]) / 8
        last   = pd.Timestamp(weekly.index[-1])
        fc_idx = pd.date_range(start=last + pd.Timedelta(weeks=1), periods=periods, freq="W")
        fc     = pd.Series(
            [max(0, weekly.iloc[-1] + slope * i) for i in range(1, periods + 1)],
            index=fc_idx,
        )

    fc_df = fc.reset_index()
    fc_df.columns = ["InvoiceDate", "Forecasted_Revenue"]
    return hist_df, fc_df


# ─────────────────────────────────────────────────────────────────────────────
# COHORT  ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    """Computes monthly cohort retention rates."""
    tmp = df[["Customer ID", "InvoiceDate"]].copy()
    tmp["OrderMonth"] = tmp["InvoiceDate"].dt.to_period("M")
    cohort_map = tmp.groupby("Customer ID")["OrderMonth"].min().rename("CohortMonth")
    tmp = tmp.join(cohort_map, on="Customer ID")
    # Use int64 explicitly to avoid pandas period-to-int deprecation issues
    tmp["PeriodNumber"] = (
        tmp["OrderMonth"].astype("int64") - tmp["CohortMonth"].astype("int64")
    )
    cohort_df = (
        tmp.groupby(["CohortMonth", "PeriodNumber"])["Customer ID"]
        .nunique()
        .reset_index()
    )
    cohort_pivot = cohort_df.pivot_table(
        index="CohortMonth", columns="PeriodNumber", values="Customer ID"
    )
    cohort_size = cohort_pivot.iloc[:, 0]
    retention   = cohort_pivot.divide(cohort_size, axis=0).round(3) * 100
    # Clip to first 12 months and convert Period index → str for Plotly JSON compatibility
    retention   = retention.iloc[:, :12]
    retention.index   = retention.index.astype(str)
    retention.columns = [str(c) for c in retention.columns]
    return retention
