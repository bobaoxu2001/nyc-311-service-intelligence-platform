# Fabric Deployment Guide

This repository is a **Microsoft Fabric-ready implementation blueprint**, not a deployed Fabric solution. It runs locally with Python, DuckDB, SQL, and CSV outputs. The steps below explain how the local artifacts would migrate into a real client Fabric environment.

## What Is Already Built Locally

| Capability | Local Artifact |
|---|---|
| API ingestion | `src/ingest_311.py` |
| Raw landing | `data/raw/nyc_311_raw.parquet` generated locally and ignored by git |
| Source metadata | `data/raw/source_metadata.json` generated locally |
| Bronze table | `sql/bronze/01_create_bronze.sql` |
| Silver transformation | `sql/silver/01_create_silver_service_requests.sql` |
| Gold star schema | `sql/gold/01_create_gold_star_schema.sql` |
| Gold KPI marts | `sql/gold/02_create_gold_kpis.sql` |
| Data quality checks | `src/quality_checks.py` |
| Anomaly monitoring | `src/anomaly_detection.py` |
| Executive summary | `src/generate_insights.py` |
| Dashboard previews | `src/generate_dashboard_mockups.py` |
| Power BI design | `powerbi/README.md`, `powerbi/dax_measures.md` |

## What A Real Client Environment Must Configure

- Fabric tenant and workspace access.
- OneLake storage paths and retention policy.
- Data Factory Pipeline or Dataflow Gen2 connection to Socrata/API.
- Lakehouse or Warehouse objects and naming standards.
- Secrets or managed identity strategy if private data sources are added.
- Power BI semantic model, report, refresh schedule, and endorsement/certification.
- Workspace roles, security groups, and deployment pipeline.
- Monitoring, support ownership, and incident process.

## Local Artifact To Fabric Component Mapping

| Local Artifact | Fabric Component | Migration Notes |
|---|---|---|
| `src/ingest_311.py` | Data Factory Pipeline, Dataflow Gen2, or Fabric Notebook | Parameterize limit, date window, API URL, and landing path. |
| Raw parquet output | OneLake raw/bronze zone | Partition by ingestion date and preserve source metadata. |
| `sql/silver/` | Lakehouse table transform or Warehouse staging SQL | Convert DuckDB syntax where needed and validate types. |
| `sql/gold/` | Warehouse or Lakehouse SQL endpoint | Publish star schema and KPI marts for semantic model consumption. |
| `src/quality_checks.py` | Fabric Notebook or Data Activator-style monitoring pattern | Persist quality results and fail/alert on thresholds. |
| `src/anomaly_detection.py` | Scheduled Fabric Notebook | Write anomaly events to a gold table consumed by Power BI. |
| CSV outputs | Power BI semantic model over Fabric tables | CSVs are a local handoff only; production should query Fabric tables. |
| Dashboard mockup PNGs | Power BI report pages | Rebuild as real visuals using DAX measures and relationships. |

## Step-By-Step Fabric Migration Plan

### Step 1: Discovery And Environment Setup

- Confirm business owner, analytics owner, and platform owner.
- Confirm Fabric capacity and workspace strategy.
- Create dev/test/prod workspaces.
- Define naming conventions for Lakehouse, Warehouse, Notebook, Pipeline, semantic model, and report assets.

### Step 2: Bronze Ingestion

- Create Data Factory Pipeline or Dataflow Gen2 for NYC Open Data extraction.
- Store raw extracts in OneLake by ingestion date.
- Store source metadata including dataset ID, URL, refresh timestamp, row count, and parameter values.
- Add retry and failure notification behavior.

### Step 3: Silver Lakehouse Transformation

- Create silver table for cleaned service requests.
- Convert local parsing and normalization logic from DuckDB SQL to Fabric-compatible SQL/Spark SQL where needed.
- Persist quality flags on the silver table.
- Validate row counts and date parsing against local prototype output.

### Step 4: Gold Warehouse Marts

- Create `fact_service_requests` and conformed dimensions.
- Create KPI marts for dashboard performance and QA.
- Define table ownership and refresh dependencies.
- Validate totals against silver and source metadata.

### Step 5: Quality And Responsible AI Controls

- Schedule data-quality checks after silver refresh.
- Persist quality results to a governed table.
- Define thresholds that block report certification or trigger warnings.
- Schedule anomaly detection and require human review before escalation.

### Step 6: Power BI Semantic Model And Report

- Build relationships from fact to dimensions.
- Add DAX measures from `powerbi/dax_measures.md`.
- Create Executive Operations, Agency Performance, Borough/Complaint, and AI Risk pages.
- Validate all measures against gold tables.
- Mark the model as promoted/certified only after stakeholder signoff.

### Step 7: Deployment Pipeline And Operations

- Promote assets from dev to test to prod.
- Configure refresh schedules and monitoring.
- Document support ownership and rollback procedure.
- Train users and establish weekly operating cadence.

## QA Checklist Before Production

- Source row counts reconcile to bronze ingestion metadata.
- Silver row counts reconcile to bronze after expected filters.
- Gold fact row count reconciles to silver.
- DAX totals reconcile to gold fact and KPI tables.
- Invalid date-order records are quantified and treated consistently.
- Open-request logic is approved by stakeholders.
- Anomaly thresholds are reviewed by operations owners.
- Workspace roles and report access are approved.
- Refresh failure notifications are routed to named owners.

## Explicit Disclaimer

Correct wording for this portfolio:

- "Fabric-ready implementation blueprint."
- "Local prototype that maps to Fabric components."
- "Power BI-ready semantic model design."

Do not describe this repository as:

- Fabric-deployed.
- Published to Power BI Service.
- A completed `.pbix` report.
- Azure ML or Cognitive Services implementation.

Those statements should only be added after real artifacts exist.

## Implementation Assets Added In `/fabric`

The `/fabric` folder provides implementation-ready assets for a real Fabric build:

- Notebook-ready scripts for quality checks, anomaly detection, and predictive modeling.
- Pipeline blueprint for ingestion, transformation, quality checks, ML, and semantic model refresh.
- Lakehouse/Warehouse table mapping.
- Warehouse gold marts SQL blueprint.
- Workspace setup and deployment checklist.

These are still blueprints. They were not deployed because Fabric tooling and authenticated workspace access were not available in the current environment.
