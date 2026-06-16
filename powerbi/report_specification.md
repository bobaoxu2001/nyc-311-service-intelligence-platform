# Power BI Report Specification

This is a Power BI implementation specification, not a `.pbix` export.

## Data Inputs

Import or connect to:

- `fact_service_requests`
- `dim_date`
- `dim_agency`
- `dim_borough`
- `dim_complaint_type`
- `dim_location`
- `daily_request_kpis`
- `agency_performance_kpis`
- `borough_service_kpis`
- `complaint_type_kpis`
- `backlog_kpis`
- `anomalies`
- `ml_predictions`

## Core Pages

1. Executive Operations Overview
2. Agency Performance & Backlog Risk
3. Borough & Complaint Demand Intelligence
4. AI Risk & Anomaly Monitor
5. Predictive Backlog Risk

## Global Slicers

- Date
- Borough
- Agency
- Complaint type
- Status

## Drillthrough

Recommended drillthrough pages:

- Agency detail
- Borough detail
- Complaint type detail
- Anomaly event detail
- Predictive risk detail

## Security Notes

- Use aggregated pages for executives.
- Limit request-level drillthrough if address/location sensitivity is a concern.
- Apply workspace roles and semantic model permissions in Power BI Service or Fabric.
