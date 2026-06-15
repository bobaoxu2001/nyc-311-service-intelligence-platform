"""Run data quality checks against the NYC 311 silver/gold models."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "nyc_311.duckdb"
INSIGHTS_DIR = PROJECT_ROOT / "outputs" / "insights"


CHECKS = [
    {
        "rule": "unique_key uniqueness",
        "severity": "high",
        "sql": "SELECT COUNT(*) AS failed_records FROM silver_service_requests WHERE is_duplicate_unique_key",
    },
    {
        "rule": "created_date not null",
        "severity": "high",
        "sql": "SELECT COUNT(*) AS failed_records FROM silver_service_requests WHERE created_ts IS NULL",
    },
    {
        "rule": "closed_date greater than or equal to created_date when closed",
        "severity": "high",
        "sql": "SELECT COUNT(*) AS failed_records FROM silver_service_requests WHERE invalid_date_order",
    },
    {
        "rule": "valid borough values",
        "severity": "medium",
        "sql": """
            SELECT COUNT(*) AS failed_records
            FROM silver_service_requests
            WHERE borough_norm NOT IN ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND', 'UNKNOWN')
        """,
    },
    {
        "rule": "resolution_hours non-negative",
        "severity": "high",
        "sql": "SELECT COUNT(*) AS failed_records FROM silver_service_requests WHERE resolution_hours < 0",
    },
    {
        "rule": "status normalization",
        "severity": "medium",
        "sql": "SELECT COUNT(*) AS failed_records FROM silver_service_requests WHERE status_norm IS NULL OR status_norm = ''",
    },
]


def run_quality_checks() -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DB_PATH}. Run src/transform_311.py first.")

    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    with duckdb.connect(str(DB_PATH), read_only=True) as connection:
        total_records = connection.execute("SELECT COUNT(*) FROM silver_service_requests").fetchone()[0]
        for check in CHECKS:
            failed = connection.execute(check["sql"]).fetchone()[0]
            pass_rate = 1 - (failed / total_records if total_records else 0)
            rows.append(
                {
                    "rule": check["rule"],
                    "severity": check["severity"],
                    "failed_records": int(failed),
                    "total_records": int(total_records),
                    "pass_rate": round(pass_rate, 6),
                    "status": "PASS" if failed == 0 else "REVIEW",
                }
            )

    report = pd.DataFrame(rows)
    report.to_csv(INSIGHTS_DIR / "data_quality_report.csv", index=False)
    write_markdown_report(report)
    print(f"Saved data quality report to {INSIGHTS_DIR}")
    return report


def write_markdown_report(report: pd.DataFrame) -> None:
    lines = [
        "# Data Quality Report",
        "",
        "This report validates the NYC 311 silver layer before the data is used in Power BI-ready gold tables.",
        "",
        "| Rule | Severity | Failed Records | Pass Rate | Status |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report.itertuples(index=False):
        lines.append(
            f"| {row.rule} | {row.severity} | {row.failed_records:,} | {row.pass_rate:.2%} | {row.status} |"
        )
    lines.extend(
        [
            "",
            "## Validation Rules",
            "",
            "- `unique_key` should identify one service request.",
            "- `created_date` is required for trend, SLA, and backlog analysis.",
            "- `closed_date` should be greater than or equal to `created_date` when present.",
            "- Borough names are normalized to the five NYC boroughs plus `UNKNOWN`.",
            "- `resolution_hours` must be non-negative.",
            "- Status values are trimmed, uppercased, and blank-safe.",
        ]
    )
    (INSIGHTS_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_quality_checks()
