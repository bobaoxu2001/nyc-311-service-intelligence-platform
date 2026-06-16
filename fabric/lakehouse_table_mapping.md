# Lakehouse And Warehouse Table Mapping

| Local Layer / Artifact | Fabric Target | Notes |
|---|---|---|
| `data/raw/nyc_311_raw.parquet` | OneLake raw/bronze files | Partition by ingestion date. |
| `data/raw/source_metadata.json` | Bronze metadata table or file | Preserve dataset ID, API URL, row count, and refresh timestamp. |
| `bronze_311` | Lakehouse bronze table | Raw landing table if table materialization is preferred. |
| `silver_service_requests` | Lakehouse silver table | Cleaned request-grain table with quality flags. |
| `fact_service_requests` | Warehouse gold fact table | Request-level fact for certified semantic model. |
| `dim_date` | Warehouse dimension | Mark as Power BI date table. |
| `dim_agency` | Warehouse dimension | Agency slicer and attribution. |
| `dim_borough` | Warehouse dimension | Borough slicer and geography grouping. |
| `dim_complaint_type` | Warehouse dimension | Complaint category analysis. |
| `dim_location` | Warehouse dimension | Map-ready location fields; apply privacy review. |
| `daily_request_kpis` | Warehouse KPI mart | Daily trend and anomaly input. |
| `backlog_kpis` | Warehouse KPI mart | Backlog risk queue and predictive model input. |
| `anomaly_events` | Warehouse AI/analytics table | Output from anomaly detection notebook. |
| `ml_backlog_risk_predictions` | Warehouse AI/analytics table | Output from predictive modeling notebook. |
