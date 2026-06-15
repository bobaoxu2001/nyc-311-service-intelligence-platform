CREATE OR REPLACE TABLE daily_request_kpis AS
SELECT
    f.created_date AS request_date,
    b.borough,
    c.complaint_type,
    COUNT(*) AS total_requests,
    SUM(f.is_open::INT) AS open_requests,
    SUM(f.is_closed::INT) AS closed_requests,
    SUM(f.is_open::INT) * 1.0 / COUNT(*) AS backlog_rate,
    AVG(f.resolution_hours) AS avg_resolution_hours,
    MEDIAN(f.resolution_hours) AS median_resolution_hours,
    AVG(f.closed_within_24h::INT) AS pct_closed_within_24h,
    AVG(f.closed_within_7d::INT) AS pct_closed_within_7d
FROM fact_service_requests f
LEFT JOIN dim_borough b
    ON b.borough_key = f.borough_key
LEFT JOIN dim_complaint_type c
    ON c.complaint_type_key = f.complaint_type_key
GROUP BY 1, 2, 3;

CREATE OR REPLACE TABLE monthly_request_kpis AS
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', created_date) AS request_month,
        COUNT(*) AS total_requests,
        SUM(is_open::INT) AS open_requests,
        SUM(is_closed::INT) AS closed_requests,
        AVG(resolution_hours) AS avg_resolution_hours
    FROM fact_service_requests
    WHERE created_date IS NOT NULL
    GROUP BY 1
)
SELECT
    request_month,
    total_requests,
    open_requests,
    closed_requests,
    open_requests * 1.0 / total_requests AS backlog_rate,
    avg_resolution_hours,
    LAG(total_requests) OVER (ORDER BY request_month) AS prior_month_requests,
    (total_requests - LAG(total_requests) OVER (ORDER BY request_month)) * 1.0
        / NULLIF(LAG(total_requests) OVER (ORDER BY request_month), 0) AS mom_request_growth_pct
FROM monthly;

CREATE OR REPLACE TABLE agency_performance_kpis AS
SELECT
    a.agency,
    a.agency_name,
    COUNT(*) AS total_requests,
    SUM(f.is_open::INT) AS open_requests,
    SUM(f.is_closed::INT) AS closed_requests,
    SUM(f.is_open::INT) * 1.0 / COUNT(*) AS backlog_rate,
    AVG(f.resolution_hours) AS avg_resolution_hours,
    MEDIAN(f.resolution_hours) AS median_resolution_hours,
    AVG(f.closed_within_24h::INT) AS pct_closed_within_24h,
    AVG(f.closed_within_7d::INT) AS pct_closed_within_7d
FROM fact_service_requests f
LEFT JOIN dim_agency a
    ON a.agency_key = f.agency_key
GROUP BY 1, 2;

CREATE OR REPLACE TABLE borough_service_kpis AS
SELECT
    b.borough,
    COUNT(*) AS total_requests,
    SUM(f.is_open::INT) AS open_requests,
    SUM(f.is_closed::INT) AS closed_requests,
    SUM(f.is_open::INT) * 1.0 / COUNT(*) AS backlog_rate,
    AVG(f.resolution_hours) AS avg_resolution_hours,
    MEDIAN(f.resolution_hours) AS median_resolution_hours,
    AVG(f.closed_within_24h::INT) AS pct_closed_within_24h,
    AVG(f.closed_within_7d::INT) AS pct_closed_within_7d
FROM fact_service_requests f
LEFT JOIN dim_borough b
    ON b.borough_key = f.borough_key
GROUP BY 1;

CREATE OR REPLACE TABLE complaint_type_kpis AS
SELECT
    c.complaint_type,
    COUNT(*) AS total_requests,
    SUM(f.is_open::INT) AS open_requests,
    SUM(f.is_closed::INT) AS closed_requests,
    SUM(f.is_open::INT) * 1.0 / COUNT(*) AS backlog_rate,
    AVG(f.resolution_hours) AS avg_resolution_hours,
    MEDIAN(f.resolution_hours) AS median_resolution_hours,
    AVG(f.closed_within_24h::INT) AS pct_closed_within_24h,
    AVG(f.closed_within_7d::INT) AS pct_closed_within_7d
FROM fact_service_requests f
LEFT JOIN dim_complaint_type c
    ON c.complaint_type_key = f.complaint_type_key
GROUP BY 1;

CREATE OR REPLACE TABLE backlog_kpis AS
SELECT
    a.agency,
    b.borough,
    COUNT(*) AS total_requests,
    SUM(f.is_open::INT) AS open_requests,
    SUM(f.is_closed::INT) AS closed_requests,
    SUM(f.is_open::INT) * 1.0 / COUNT(*) AS backlog_rate,
    AVG(f.resolution_hours) AS avg_resolution_hours,
    CASE
        WHEN COUNT(*) >= 100 AND SUM(f.is_open::INT) * 1.0 / COUNT(*) >= 0.20 THEN TRUE
        WHEN COUNT(*) >= 50 AND SUM(f.is_open::INT) * 1.0 / COUNT(*) >= 0.35 THEN TRUE
        ELSE FALSE
    END AS high_risk_backlog_flag
FROM fact_service_requests f
LEFT JOIN dim_agency a
    ON a.agency_key = f.agency_key
LEFT JOIN dim_borough b
    ON b.borough_key = f.borough_key
GROUP BY 1, 2;
