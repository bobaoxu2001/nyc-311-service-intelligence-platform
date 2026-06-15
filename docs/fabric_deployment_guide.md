# Microsoft Fabric-Ready Implementation Guide

This project runs locally with Python, DuckDB, SQL, and CSV exports. The design maps cleanly to Microsoft Fabric, but this repository does not claim that the pipeline has actually run inside Fabric.

## Local-to-Fabric Mapping

| Local Component | Fabric Equivalent | Purpose |
|---|---|---|
| `data/raw/nyc_311_raw.parquet` | OneLake Lakehouse bronze files | Preserve raw NYC Open Data records. |
| `silver_service_requests` | Lakehouse table or Warehouse table | Standardize fields, parse dates, and add quality flags. |
| Gold star schema tables | Warehouse or Lakehouse SQL endpoint | Serve governed Power BI semantic model tables. |
| `src/ingest_311.py` | Data Factory Pipeline or Dataflow Gen2 | Parameterized ingestion from the Socrata API. |
| `src/transform_311.py` | Fabric Notebook or SQL script | Apply medallion SQL transformations. |
| `src/anomaly_detection.py` | Fabric Notebook scheduled job | Run explainable daily spike detection. |
| CSV outputs | Power BI semantic model import or Direct Lake tables | Build report pages and measures. |

## Suggested Fabric Architecture

1. **OneLake/Lakehouse Bronze**
   - Land raw 311 extracts by ingestion date.
   - Store source metadata such as dataset ID, API URL, requested limit, and ingestion timestamp.

2. **Lakehouse or Warehouse Silver**
   - Apply column standardization and timestamp parsing.
   - Add quality flags for missing close date, invalid date ordering, missing borough, and duplicate keys.

3. **Warehouse or SQL Endpoint Gold**
   - Publish `fact_service_requests` plus date, agency, borough, complaint type, and location dimensions.
   - Publish KPI tables for executive dashboards and operational drilldowns.

4. **Notebook Analytics Layer**
   - Run the rolling-baseline anomaly detector.
   - Persist anomaly outputs to a gold table such as `gold.anomaly_events`.

5. **Power BI Semantic Model**
   - Define measures in one governed semantic model.
   - Certify definitions for backlog rate, resolution time, and closed-within-SLA metrics.

6. **Deployment Pipeline**
   - Use dev/test/prod workspaces.
   - Promote notebooks, SQL scripts, semantic models, and reports together.
   - Parameterize sample size, refresh cadence, and storage paths by environment.

## Operating Cadence

- Daily: ingest latest 311 requests and refresh gold KPI tables.
- Weekly: review anomaly events and high-risk backlog combinations.
- Monthly: produce executive trend review with month-over-month growth and agency performance rankings.
