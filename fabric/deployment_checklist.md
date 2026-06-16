# Fabric Deployment Checklist

## Pre-Deployment

- Confirm Fabric tenant and capacity availability.
- Create dev/test/prod workspaces.
- Assign workspace roles for platform owners, developers, analysts, and viewers.
- Confirm naming conventions for Lakehouse, Warehouse, Notebooks, Pipelines, and semantic model.
- Confirm NYC Open Data API access and refresh cadence.
- Confirm KPI definitions and quality thresholds with stakeholders.

## Data Platform Setup

- Create OneLake raw/bronze folder structure.
- Create Lakehouse silver tables.
- Create Warehouse gold schema and KPI marts.
- Configure Data Factory Pipeline or Dataflow Gen2 ingestion.
- Configure Notebook activities for quality checks, anomaly detection, and predictive modeling.

## Power BI Setup

- Create semantic model over gold tables.
- Configure relationships and DAX measures from `powerbi/`.
- Build report pages from `powerbi/page_wireframes.md`.
- Configure refresh schedule.
- Apply workspace roles and report access.

## QA Gates

- Bronze row count matches API extract metadata.
- Silver row count reconciles to bronze.
- Gold fact row count reconciles to silver.
- DAX measures reconcile to SQL KPI tables.
- Quality exceptions are visible and signed off.
- Anomaly thresholds are reviewed by operations owners.
- Predictive model report and model card are reviewed before use.

## Go-Live

- Promote dev to test and prod through deployment pipeline.
- Validate refresh monitoring and alert routing.
- Run user acceptance testing.
- Train executives, analysts, and operations users.
- Establish weekly backlog/anomaly operating cadence.
