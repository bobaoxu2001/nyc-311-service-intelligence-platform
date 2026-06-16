"""Fabric Notebook-ready anomaly detection blueprint."""

from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path("outputs/sample_dashboard_data")


def main() -> None:
    daily = pd.read_csv(DATA_DIR / "daily_request_kpis.csv")
    daily["request_date"] = pd.to_datetime(daily["request_date"])
    daily = daily.sort_values(["borough", "complaint_type", "request_date"])

    def score(group: pd.DataFrame) -> pd.DataFrame:
        prior = group["total_requests"].shift(1)
        group["rolling_mean_14d"] = prior.rolling(14, min_periods=7).mean()
        group["rolling_std_14d"] = prior.rolling(14, min_periods=7).std().replace(0, np.nan)
        group["z_score"] = (group["total_requests"] - group["rolling_mean_14d"]) / group["rolling_std_14d"]
        group["is_anomaly"] = (group["z_score"] >= 3) & (group["total_requests"] >= 10)
        return group

    scored = daily.groupby(["borough", "complaint_type"], group_keys=False).apply(score)
    anomalies = scored[scored["is_anomaly"]].copy()
    anomalies.to_csv(DATA_DIR / "fabric_anomaly_events_blueprint.csv", index=False)
    display(anomalies.head(20)) if "display" in globals() else print(anomalies.head(20))


if __name__ == "__main__":
    main()
