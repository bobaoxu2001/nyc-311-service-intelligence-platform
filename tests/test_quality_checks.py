import duckdb
import pytest

from src import quality_checks


@pytest.fixture
def silver(tmp_path, monkeypatch):
    database = tmp_path / "requests.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("""
            CREATE TABLE silver_service_requests (
                is_duplicate_unique_key BOOLEAN,
                created_ts TIMESTAMP,
                invalid_date_order BOOLEAN,
                borough_norm VARCHAR,
                resolution_hours DOUBLE,
                status_norm VARCHAR
            )
        """)
    monkeypatch.setattr(quality_checks, "DB_PATH", database)
    monkeypatch.setattr(quality_checks, "INSIGHTS_DIR", tmp_path / "insights")
    return database


def test_empty_silver_is_not_a_successful_quality_report(silver):
    with pytest.raises(ValueError, match="empty"):
        quality_checks.run_quality_checks()
    assert not (quality_checks.INSIGHTS_DIR / "data_quality_report.csv").exists()


def test_invalid_rows_remain_visible_in_the_quality_report(silver):
    with duckdb.connect(str(silver)) as connection:
        connection.execute("""
            INSERT INTO silver_service_requests VALUES
            (false, '2026-01-01', false, 'BRONX', 1, 'CLOSED'),
            (true, NULL, true, 'INVALID', -1, '')
        """)
    result = quality_checks.run_quality_checks()
    assert (result.total_records == 2).all()
    assert (result.failed_records == 1).all()
    assert (result.status == "REVIEW").all()
    assert (result.pass_rate == 0.5).all()
