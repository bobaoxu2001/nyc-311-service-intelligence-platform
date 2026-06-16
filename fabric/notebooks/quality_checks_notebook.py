"""Fabric Notebook-ready data quality checks.

This file is a portable notebook script blueprint. In a real Fabric notebook,
replace the local CSV reads with Lakehouse/Warehouse table reads.
"""

from pathlib import Path

import pandas as pd


DATA_DIR = Path("outputs/sample_dashboard_data")
INSIGHTS_DIR = Path("outputs/insights")


def main() -> None:
    fact_path = DATA_DIR / "fact_service_requests.csv"
    if not fact_path.exists():
        raise FileNotFoundError("Expected fact_service_requests.csv or Fabric table equivalent.")

    fact = pd.read_csv(fact_path)
    checks = [
        ("request_id uniqueness", fact["request_id"].duplicated().sum()),
        ("created date not null", fact["created_ts"].isna().sum()),
        ("invalid date order", fact["invalid_date_order"].astype(bool).sum()),
        ("missing borough flag", fact["missing_borough"].astype(bool).sum()),
        ("negative resolution hours", (fact["resolution_hours"] < 0).sum()),
    ]
    report = pd.DataFrame(checks, columns=["rule", "failed_records"])
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(INSIGHTS_DIR / "fabric_quality_check_blueprint_output.csv", index=False)
    display(report) if "display" in globals() else print(report)


if __name__ == "__main__":
    main()
