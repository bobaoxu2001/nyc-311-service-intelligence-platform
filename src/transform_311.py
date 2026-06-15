"""Transform raw NYC 311 data into bronze, silver, and gold DuckDB models."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "nyc_311_raw.parquet"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROCESSED_DIR / "nyc_311.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sample_dashboard_data"

SQL_FILES = [
    PROJECT_ROOT / "sql" / "bronze" / "01_create_bronze.sql",
    PROJECT_ROOT / "sql" / "silver" / "01_create_silver_service_requests.sql",
    PROJECT_ROOT / "sql" / "gold" / "01_create_gold_star_schema.sql",
    PROJECT_ROOT / "sql" / "gold" / "02_create_gold_kpis.sql",
]

EXPORT_TABLES = [
    "fact_service_requests",
    "dim_date",
    "dim_agency",
    "dim_borough",
    "dim_complaint_type",
    "dim_location",
    "daily_request_kpis",
    "monthly_request_kpis",
    "agency_performance_kpis",
    "borough_service_kpis",
    "complaint_type_kpis",
    "backlog_kpis",
]


def run_sql_file(connection: duckdb.DuckDBPyConnection, sql_path: Path) -> None:
    sql = sql_path.read_text(encoding="utf-8").replace("{{ raw_path }}", RAW_PATH.as_posix())
    print(f"Running {sql_path.relative_to(PROJECT_ROOT)}")
    connection.execute(sql)


def export_powerbi_csvs(connection: duckdb.DuckDBPyConnection) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for table in EXPORT_TABLES:
        output_path = OUTPUT_DIR / f"{table}.csv"
        connection.execute(f"COPY (SELECT * FROM {table}) TO ? (HEADER, DELIMITER ',')", [str(output_path)])
        print(f"Exported {output_path.relative_to(PROJECT_ROOT)}")


def transform() -> Path:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}. Run src/ingest_311.py first.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB_PATH)) as connection:
        for sql_file in SQL_FILES:
            run_sql_file(connection, sql_file)
        export_powerbi_csvs(connection)

    print(f"DuckDB database saved to {DB_PATH}")
    return DB_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build NYC 311 bronze, silver, and gold tables.")
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
    transform()
