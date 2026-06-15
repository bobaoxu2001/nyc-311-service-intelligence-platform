"""Generate rule-based consulting recommendations from KPI outputs."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "nyc_311.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sample_dashboard_data"
INSIGHTS_DIR = PROJECT_ROOT / "outputs" / "insights"


def load_table(connection: duckdb.DuckDBPyConnection, table: str) -> pd.DataFrame:
    return connection.execute(f"SELECT * FROM {table}").df()


def generate_summary() -> Path:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB database not found: {DB_PATH}. Run src/transform_311.py first.")

    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB_PATH), read_only=True) as connection:
        agency = load_table(connection, "agency_performance_kpis")
        borough = load_table(connection, "borough_service_kpis")
        complaint = load_table(connection, "complaint_type_kpis")
        backlog = load_table(connection, "backlog_kpis")
        monthly = load_table(connection, "monthly_request_kpis")
        overall = connection.execute(
            """
            SELECT
                COUNT(*) AS total_requests,
                SUM(is_open::INT) AS open_requests,
                AVG(resolution_hours) AS avg_resolution_hours,
                MEDIAN(resolution_hours) AS median_resolution_hours,
                AVG(closed_within_7d::INT) AS pct_closed_within_7d
            FROM fact_service_requests
            """
        ).df().iloc[0]

    anomalies_path = OUTPUT_DIR / "anomalies.csv"
    anomalies = pd.read_csv(anomalies_path) if anomalies_path.exists() else pd.DataFrame()

    total_requests = int(overall["total_requests"])
    open_requests = int(overall["open_requests"] or 0)
    backlog_rate = open_requests / total_requests if total_requests else 0
    avg_resolution = float(overall["avg_resolution_hours"]) if pd.notna(overall["avg_resolution_hours"]) else 0
    pct_7d = float(overall["pct_closed_within_7d"]) if pd.notna(overall["pct_closed_within_7d"]) else 0

    high_backlog = backlog.sort_values(["backlog_rate", "total_requests"], ascending=[False, False]).head(5)
    top_complaints = complaint.sort_values("total_requests", ascending=False).head(5)
    slow_agencies = agency.sort_values("avg_resolution_hours", ascending=False).head(5)
    top_borough = borough.sort_values("total_requests", ascending=False).head(1)
    latest_mom = monthly.dropna(subset=["mom_request_growth_pct"]).sort_values("request_month").tail(1)

    lines = [
        "# Executive Summary",
        "",
        "This rule-based AI insight summary converts NYC 311 operational KPIs into consulting-style recommendations without using an external LLM API.",
        "",
        "## KPI Snapshot",
        "",
        f"- Total requests analyzed: **{total_requests:,}**",
        f"- Open requests: **{open_requests:,}** ({backlog_rate:.1%} backlog rate)",
        f"- Average resolution time: **{avg_resolution:.1f} hours**",
        f"- Closed within 7 days: **{pct_7d:.1%}**",
    ]

    if not latest_mom.empty:
        row = latest_mom.iloc[0]
        lines.append(f"- Latest month-over-month request growth: **{row['mom_request_growth_pct']:.1%}**")

    lines.extend(["", "## Consulting Recommendations", ""])

    if backlog_rate >= 0.15:
        lines.append(
            "- Prioritize a backlog triage sprint: the current backlog rate is elevated enough to warrant agency-level queue review, aging analysis, and short-cycle escalation rules."
        )
    else:
        lines.append(
            "- Maintain backlog controls: backlog rate is not the primary portfolio risk, but high-risk agency/borough pockets should still be reviewed weekly."
        )

    if not high_backlog.empty:
        row = high_backlog.iloc[0]
        lines.append(
            f"- Focus backlog review on **{row['agency']} / {row['borough']}**, where backlog rate is {row['backlog_rate']:.1%} across {int(row['total_requests']):,} requests."
        )

    if not top_complaints.empty:
        row = top_complaints.iloc[0]
        lines.append(
            f"- Launch a root-cause review for **{row['complaint_type']}**, the highest-volume complaint category with {int(row['total_requests']):,} requests."
        )

    if not slow_agencies.empty:
        row = slow_agencies.iloc[0]
        if pd.notna(row["avg_resolution_hours"]):
            lines.append(
                f"- Review workflow design for **{row['agency']}**, where average resolution time is {row['avg_resolution_hours']:.1f} hours."
            )

    if not top_borough.empty:
        row = top_borough.iloc[0]
        lines.append(
            f"- Use borough-level capacity planning for **{row['borough']}**, the largest demand area in the current sample."
        )

    if not anomalies.empty:
        row = anomalies.iloc[0]
        lines.append(
            f"- Investigate the latest anomaly: **{row['complaint_type']}** in **{row['borough']}** reached {int(row['total_requests']):,} requests on {row['request_date']}."
        )

    lines.extend(
        [
            "",
            "## Suggested Client Next Steps",
            "",
            "1. Validate data-quality exceptions with operational owners before executive reporting.",
            "2. Build a Power BI semantic model with certified KPI definitions and date/agency/borough dimensions.",
            "3. Run weekly anomaly monitoring to surface complaint spikes before they become sustained backlog.",
            "4. Translate the highest-risk agency/borough combinations into queue-management actions and SLA review meetings.",
        ]
    )

    output_path = INSIGHTS_DIR / "executive_summary.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved executive summary to {output_path}")
    return output_path


if __name__ == "__main__":
    generate_summary()
