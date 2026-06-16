-- Fabric Warehouse gold marts blueprint.
-- Adapt schema names and source table names to the target Fabric workspace.

CREATE SCHEMA IF NOT EXISTS gold;

-- In a real Fabric Warehouse, replace silver_service_requests with the
-- Lakehouse shortcut/table reference used by the client environment.

CREATE OR ALTER VIEW gold.vw_service_request_kpi_base AS
SELECT
    unique_key,
    CAST(created_ts AS date) AS created_date,
    CAST(closed_ts AS date) AS closed_date,
    agency_norm AS agency,
    borough_norm AS borough,
    complaint_type_norm AS complaint_type,
    resolution_hours,
    CAST(is_open AS int) AS is_open,
    CAST(is_closed AS int) AS is_closed,
    CAST(closed_within_24h AS int) AS closed_within_24h,
    CAST(closed_within_7d AS int) AS closed_within_7d
FROM silver_service_requests;

-- Example KPI mart. The local repo contains full DuckDB SQL under sql/gold/.
CREATE TABLE gold.backlog_kpis AS
SELECT
    agency,
    borough,
    COUNT(*) AS total_requests,
    SUM(is_open) AS open_requests,
    SUM(is_closed) AS closed_requests,
    CAST(SUM(is_open) AS float) / NULLIF(COUNT(*), 0) AS backlog_rate,
    AVG(resolution_hours) AS avg_resolution_hours,
    CASE
        WHEN COUNT(*) >= 100 AND CAST(SUM(is_open) AS float) / NULLIF(COUNT(*), 0) >= 0.20 THEN 1
        WHEN COUNT(*) >= 50 AND CAST(SUM(is_open) AS float) / NULLIF(COUNT(*), 0) >= 0.35 THEN 1
        ELSE 0
    END AS high_risk_backlog_flag
FROM gold.vw_service_request_kpi_base
GROUP BY agency, borough;
