"""Detect explainable daily volume anomalies by complaint type and borough."""

from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "nyc_311.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sample_dashboard_data"
INSIGHTS_DIR = PROJECT_ROOT / "outputs" / "insights"


def detect_anomalies() -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DB_PATH}. Run src/transform_311.py first.")

    with duckdb.connect(str(DB_PATH), read_only=True) as connection:
        daily = connection.execute(
            """
            SELECT
                request_date,
                borough,
                complaint_type,
                total_requests
            FROM daily_request_kpis
            WHERE request_date IS NOT NULL
            """
        ).df()

    if daily.empty:
        raise RuntimeError("No daily KPI rows available for anomaly detection.")

    daily["request_date"] = pd.to_datetime(daily["request_date"])
    daily = daily.sort_values(["borough", "complaint_type", "request_date"])
    group_cols = ["borough", "complaint_type"]

    def add_signals(group: pd.DataFrame) -> pd.DataFrame:
        prior_volume = group["total_requests"].shift(1)
        group["rolling_mean_14d"] = prior_volume.rolling(window=14, min_periods=7).mean()
        group["rolling_std_14d"] = prior_volume.rolling(window=14, min_periods=7).std()
        group["rolling_q1_28d"] = prior_volume.rolling(window=28, min_periods=10).quantile(0.25)
        group["rolling_q3_28d"] = prior_volume.rolling(window=28, min_periods=10).quantile(0.75)
        return group

    scored = daily.groupby(group_cols).apply(add_signals, include_groups=False).reset_index()
    if "level_2" in scored.columns:
        scored = scored.drop(columns=["level_2"])
    scored["rolling_std_14d"] = scored["rolling_std_14d"].replace(0, np.nan)
    scored["z_score"] = (scored["total_requests"] - scored["rolling_mean_14d"]) / scored["rolling_std_14d"]
    scored["iqr"] = scored["rolling_q3_28d"] - scored["rolling_q1_28d"]
    scored["iqr_upper_bound"] = scored["rolling_q3_28d"] + (1.5 * scored["iqr"])
    scored["is_zscore_anomaly"] = (scored["z_score"] >= 3) & (scored["total_requests"] >= 10)
    scored["is_iqr_anomaly"] = (scored["total_requests"] > scored["iqr_upper_bound"]) & (scored["total_requests"] >= 10)
    scored["is_anomaly"] = scored["is_zscore_anomaly"] | scored["is_iqr_anomaly"]

    anomalies = scored.loc[scored["is_anomaly"]].copy()
    anomalies["recommended_action"] = anomalies.apply(recommend_action, axis=1)
    anomalies = anomalies.sort_values(["request_date", "total_requests"], ascending=[False, False])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    anomalies.to_csv(OUTPUT_DIR / "anomalies.csv", index=False)
    write_anomaly_summary(anomalies)
    print(f"Saved {len(anomalies):,} anomalies to {OUTPUT_DIR / 'anomalies.csv'}")
    return anomalies


def recommend_action(row: pd.Series) -> str:
    return (
        f"Review root cause for {row['complaint_type']} spike in {row['borough']} and confirm whether staffing, "
        "weather, seasonal demand, or a localized service issue explains the increase."
    )


def write_anomaly_summary(anomalies: pd.DataFrame) -> None:
    lines = [
        "# AI Risk & Anomaly Summary",
        "",
        "Method: explainable rolling baseline using prior 14-day mean/z-score and prior 28-day IQR by borough and complaint type.",
        "",
    ]
    if anomalies.empty:
        lines.append("No high-confidence volume spikes were detected in the current sample.")
    else:
        lines.extend(
            [
                f"Detected **{len(anomalies):,}** unusual daily request-volume spikes in the current sample.",
                "",
                "## Top Recent Anomalies",
                "",
            ]
        )
        for row in anomalies.head(10).itertuples(index=False):
            z_score = "n/a" if pd.isna(row.z_score) else f"{row.z_score:.1f}"
            lines.append(
                f"- {row.request_date.date()}: {row.complaint_type} in {row.borough} reached "
                f"{int(row.total_requests):,} requests versus a 14-day baseline of "
                f"{row.rolling_mean_14d:.1f}; z-score {z_score}."
            )
    (INSIGHTS_DIR / "anomaly_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    detect_anomalies()
