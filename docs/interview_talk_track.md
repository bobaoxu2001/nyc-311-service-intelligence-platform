# Interview Talk Track

## 30-Second Pitch

I built a NYC 311 Service Intelligence Platform as a consulting-style analytics project. It ingests public NYC Open Data, models it through bronze, silver, and gold layers in DuckDB, exports Power BI-ready tables, validates data quality, and adds explainable anomaly detection for complaint spikes. The point is not flashy ML. It is a realistic client deliverable: governed KPIs, backlog-risk monitoring, and clear recommendations a public-sector operations team could use.

## 2-Minute Walkthrough

The client problem is service visibility. A city operations leader needs to know which agencies and boroughs have high demand, which complaint types are driving workload, and where backlog or unusual spikes may require action.

I started with the NYC Open Data 311 dataset, using Socrata dataset `erm2-nwe9`. The ingestion script pulls a configurable recent sample and saves source metadata locally. From there, SQL transformations create a medallion architecture:

- Bronze preserves raw service-request records.
- Silver standardizes dates, agency, borough, complaint type, status, and calculates resolution hours.
- Silver also adds data-quality flags such as missing close date, invalid date ordering, missing borough, and duplicate unique keys.
- Gold creates a Power BI-ready star schema plus KPI tables for daily demand, agency performance, borough performance, complaint type performance, and backlog risk.

The current sample processed 100,000 records. It found a 28.0% backlog rate, 15.5-hour average resolution time, 73.6% closed within 7 days, and 15 anomaly events. I then generated a rule-based executive summary and four static dashboard mockups so an interviewer can quickly see the intended reporting experience.

## Technical Explanation

The project uses Python for ingestion and analytics orchestration, DuckDB for local SQL modeling, pandas for KPI and visualization work, and matplotlib for static dashboard mockups. The SQL is split by bronze, silver, and gold folders so the transformation logic is auditable.

The anomaly detection is intentionally explainable. For each borough and complaint type, it compares daily request volume against a prior 14-day rolling mean and standard deviation, then also checks a prior 28-day IQR threshold. A spike is flagged when the z-score or IQR test indicates unusually high volume and the volume is large enough to matter operationally.

The executive summary does not use an external LLM. It uses deterministic rules and templates based on KPI outputs, which makes it easier to explain, audit, and run without secrets or API cost.

## Fabric And Power BI Mapping

Locally, this project runs with Python, SQL, DuckDB, and CSV exports. In Microsoft Fabric, I would map it this way:

- OneLake/Lakehouse stores bronze and silver tables.
- Data Factory Pipeline or Dataflow Gen2 handles scheduled Socrata ingestion.
- A Fabric Notebook runs Python transformation, quality checks, and anomaly detection.
- A Warehouse or Lakehouse SQL endpoint serves the gold star schema.
- Power BI builds the semantic model, DAX measures, and four report pages.
- Deployment pipelines promote assets from dev to test to prod.

I would be careful to say this repo is Fabric-ready, not Fabric-deployed, because the current implementation runs locally.

## Likely Interviewer Q&A

**Q: Why use DuckDB instead of a cloud warehouse?**  
A: DuckDB makes the portfolio project easy to run locally while still using real SQL modeling patterns. The design maps to Fabric Warehouse or a Lakehouse SQL endpoint for production.

**Q: Why not use a complex ML model?**  
A: For an operations dashboard, explainability matters more than model complexity. Rolling baselines and z-scores are transparent, easy to validate, and actionable for a client team.

**Q: How would you productionize this?**  
A: I would parameterize ingestion, land raw files in OneLake, schedule transformations in Fabric, publish certified semantic-model measures, and add monitoring for refresh failures and data-quality thresholds.

**Q: How do you know the KPIs are trustworthy?**  
A: The pipeline includes explicit quality checks for unique keys, required created dates, invalid date order, borough normalization, non-negative resolution hours, and status normalization. Exceptions are reported rather than hidden.

**Q: What would you improve next?**  
A: I would build an actual `.pbix` report, add incremental refresh logic, add aging-bucket KPIs for open requests, and validate SLA definitions with operational stakeholders.

**Q: What makes this a consulting project instead of just a coding project?**  
A: It includes business framing, KPI definitions, quality notes, a roadmap, stakeholder-ready dashboard mockups, and recommended actions tied to operational risks.
