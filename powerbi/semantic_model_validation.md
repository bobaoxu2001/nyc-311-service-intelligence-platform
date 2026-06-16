# Semantic Model Validation

## Relationship Validation

| Check | Expected Result |
|---|---|
| Fact row count | Matches generated `fact_service_requests.csv` or Fabric gold fact count. |
| Date relationship | `created_date_key` filters fact rows through `dim_date`. |
| Agency relationship | `agency_key` filters fact rows through `dim_agency`. |
| Borough relationship | `borough_key` filters fact rows through `dim_borough`. |
| Complaint relationship | `complaint_type_key` filters fact rows through `dim_complaint_type`. |
| Location relationship | `location_key` filters fact rows through `dim_location`. |

## Measure Validation

- Total Requests = fact row count.
- Open Requests + Closed Requests = Total Requests.
- Backlog Rate = Open Requests / Total Requests.
- Closed Within 7 Days % matches SQL KPI sample within rounding tolerance.
- Anomaly Count matches `anomalies.csv`.
- High Risk Backlog Count matches `backlog_kpis`.
- Predictive high-risk count matches `ml_predictions.csv`.

## Refresh Validation

- Confirm latest source ingestion timestamp.
- Confirm quality report generated after silver layer refresh.
- Confirm anomaly and ML outputs generated after gold marts refresh.
- Confirm semantic model refresh completes after all upstream jobs.
