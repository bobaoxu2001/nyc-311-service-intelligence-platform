CREATE OR REPLACE TABLE dim_date AS
WITH dates AS (
    SELECT DISTINCT CAST(created_ts AS DATE) AS date_day
    FROM silver_service_requests
    WHERE created_ts IS NOT NULL
    UNION
    SELECT DISTINCT CAST(closed_ts AS DATE) AS date_day
    FROM silver_service_requests
    WHERE closed_ts IS NOT NULL
)
SELECT
    CAST(STRFTIME(date_day, '%Y%m%d') AS INTEGER) AS date_key,
    date_day,
    EXTRACT(year FROM date_day) AS year,
    EXTRACT(quarter FROM date_day) AS quarter,
    EXTRACT(month FROM date_day) AS month,
    STRFTIME(date_day, '%B') AS month_name,
    EXTRACT(week FROM date_day) AS week_of_year,
    STRFTIME(date_day, '%A') AS day_name,
    EXTRACT(dow FROM date_day) AS day_of_week
FROM dates;

CREATE OR REPLACE TABLE dim_agency AS
SELECT
    ROW_NUMBER() OVER (ORDER BY agency_norm) AS agency_key,
    agency_norm AS agency,
    MAX(agency_name_norm) AS agency_name
FROM silver_service_requests
GROUP BY agency_norm;

CREATE OR REPLACE TABLE dim_borough AS
SELECT
    ROW_NUMBER() OVER (ORDER BY borough_norm) AS borough_key,
    borough_norm AS borough
FROM silver_service_requests
GROUP BY borough_norm;

CREATE OR REPLACE TABLE dim_complaint_type AS
SELECT
    ROW_NUMBER() OVER (ORDER BY complaint_type_norm) AS complaint_type_key,
    complaint_type_norm AS complaint_type
FROM silver_service_requests
GROUP BY complaint_type_norm;

CREATE OR REPLACE TABLE dim_location AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY borough_norm, incident_zip, latitude, longitude
    ) AS location_key,
    borough_norm AS borough,
    incident_zip,
    latitude,
    longitude
FROM (
    SELECT DISTINCT
        borough_norm,
        incident_zip,
        latitude,
        longitude
    FROM silver_service_requests
);

CREATE OR REPLACE TABLE fact_service_requests AS
SELECT
    s.unique_key AS request_id,
    created_date.date_key AS created_date_key,
    closed_date.date_key AS closed_date_key,
    agency.agency_key,
    borough.borough_key,
    complaint.complaint_type_key,
    location.location_key,
    CAST(s.created_ts AS DATE) AS created_date,
    CAST(s.closed_ts AS DATE) AS closed_date,
    s.created_ts,
    s.closed_ts,
    s.status_norm AS status,
    s.descriptor_norm AS descriptor,
    s.location_type_norm AS location_type,
    s.incident_zip,
    s.latitude,
    s.longitude,
    s.resolution_hours,
    s.is_open,
    s.is_closed,
    COALESCE(s.closed_within_24h, FALSE) AS closed_within_24h,
    COALESCE(s.closed_within_7d, FALSE) AS closed_within_7d,
    s.missing_close_date,
    s.invalid_date_order,
    s.missing_borough,
    s.is_duplicate_unique_key
FROM silver_service_requests s
LEFT JOIN dim_date created_date
    ON created_date.date_day = CAST(s.created_ts AS DATE)
LEFT JOIN dim_date closed_date
    ON closed_date.date_day = CAST(s.closed_ts AS DATE)
LEFT JOIN dim_agency agency
    ON agency.agency = s.agency_norm
LEFT JOIN dim_borough borough
    ON borough.borough = s.borough_norm
LEFT JOIN dim_complaint_type complaint
    ON complaint.complaint_type = s.complaint_type_norm
LEFT JOIN dim_location location
    ON location.borough = s.borough_norm
    AND location.incident_zip IS NOT DISTINCT FROM s.incident_zip
    AND location.latitude IS NOT DISTINCT FROM s.latitude
    AND location.longitude IS NOT DISTINCT FROM s.longitude;
