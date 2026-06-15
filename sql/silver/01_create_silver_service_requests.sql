CREATE OR REPLACE TABLE silver_service_requests AS
WITH typed AS (
    SELECT
        CAST(unique_key AS VARCHAR) AS unique_key,
        TRY_CAST(created_date AS TIMESTAMP) AS created_ts,
        TRY_CAST(closed_date AS TIMESTAMP) AS closed_ts,
        NULLIF(UPPER(TRIM(CAST(agency AS VARCHAR))), '') AS agency_norm,
        COALESCE(NULLIF(TRIM(CAST(agency_name AS VARCHAR)), ''), 'Unknown Agency') AS agency_name_norm,
        COALESCE(NULLIF(TRIM(CAST(complaint_type AS VARCHAR)), ''), 'Unknown Complaint') AS complaint_type_norm,
        COALESCE(NULLIF(TRIM(CAST(descriptor AS VARCHAR)), ''), 'Unknown Descriptor') AS descriptor_norm,
        COALESCE(NULLIF(TRIM(CAST(location_type AS VARCHAR)), ''), 'Unknown Location Type') AS location_type_norm,
        NULLIF(TRIM(CAST(incident_zip AS VARCHAR)), '') AS incident_zip,
        NULLIF(TRIM(CAST(incident_address AS VARCHAR)), '') AS incident_address,
        NULLIF(TRIM(CAST(street_name AS VARCHAR)), '') AS street_name,
        NULLIF(TRIM(CAST(cross_street_1 AS VARCHAR)), '') AS cross_street_1,
        NULLIF(TRIM(CAST(cross_street_2 AS VARCHAR)), '') AS cross_street_2,
        COALESCE(NULLIF(UPPER(TRIM(CAST(status AS VARCHAR))), ''), 'UNKNOWN') AS status_norm,
        TRY_CAST(due_date AS TIMESTAMP) AS due_ts,
        NULLIF(TRIM(CAST(resolution_description AS VARCHAR)), '') AS resolution_description,
        CASE
            WHEN UPPER(TRIM(CAST(borough AS VARCHAR))) IN ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND')
                THEN UPPER(TRIM(CAST(borough AS VARCHAR)))
            ELSE 'UNKNOWN'
        END AS borough_norm,
        TRY_CAST(latitude AS DOUBLE) AS latitude,
        TRY_CAST(longitude AS DOUBLE) AS longitude
    FROM bronze_311
),
with_metrics AS (
    SELECT
        *,
        CASE
            WHEN closed_ts IS NOT NULL AND created_ts IS NOT NULL AND closed_ts >= created_ts
                THEN DATE_DIFF('minute', created_ts, closed_ts) / 60.0
            ELSE NULL
        END AS resolution_hours,
        closed_ts IS NULL AS missing_close_date,
        closed_ts IS NOT NULL AND created_ts IS NOT NULL AND closed_ts < created_ts AS invalid_date_order,
        borough_norm = 'UNKNOWN' AS missing_borough,
        COUNT(*) OVER (PARTITION BY unique_key) > 1 AS is_duplicate_unique_key
    FROM typed
)
SELECT
    *,
    status_norm = 'CLOSED' AS is_closed,
    status_norm <> 'CLOSED' AS is_open,
    resolution_hours <= 24 AS closed_within_24h,
    resolution_hours <= 168 AS closed_within_7d
FROM with_metrics;
