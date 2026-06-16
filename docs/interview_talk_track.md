# Interview Talk Track

## 30-Second Pitch For A Senior Consultant Role

I built the NYC 311 Service Intelligence Platform as a Senior Consultant-style analytics and AI portfolio project. It is a working local pipeline on real NYC Open Data, but the broader deliverable is a Fabric-ready implementation blueprint: medallion architecture, Power BI semantic model design, data-quality controls, explainable anomaly monitoring, governance notes, and a client enablement plan. I intentionally avoid claiming Fabric or Power BI deployment because the current artifact is a local prototype.

## 2-Minute Walkthrough

The client scenario is public-sector service operations. Leaders need to understand demand, backlog, resolution performance, and unusual complaint spikes across agencies and boroughs.

I built the pipeline around the NYC Open Data 311 dataset, Socrata ID `erm2-nwe9`. The local pipeline ingests a configurable sample, lands raw data, transforms it through bronze/silver/gold SQL layers, creates a Power BI-ready star schema, exports KPI tables, validates data quality, and runs explainable anomaly detection.

The current sample processed 100,000 requests. It found a 28.0% backlog rate, 15.5-hour average resolution time, 73.6% closed within 7 days, and 15 anomaly events. I also added dashboard mockups, an executive summary, a Fabric migration guide, governance/responsible AI documentation, and a client training plan.

The point is to show how I think as a consultant: not only building code, but designing an architecture, explaining tradeoffs, validating data, preparing stakeholder adoption, and being honest about what is built versus proposed.

## Fabric Architecture Explanation

Locally, the stack is Python, DuckDB, SQL, pandas, and CSV outputs. In a real Fabric implementation:

- Data Factory or Dataflow Gen2 would orchestrate Socrata ingestion.
- OneLake would store raw/bronze extracts and metadata.
- A Fabric Lakehouse would hold cleaned silver service-request tables.
- A Fabric Warehouse or SQL endpoint would serve gold fact/dimension tables and KPI marts.
- A Fabric Notebook would run quality checks and anomaly detection.
- Power BI would use a certified semantic model and report pages.
- Governance controls would cover workspace roles, refresh monitoring, metric certification, and human review of anomaly signals.

## AI / Anomaly Detection Explanation

The anomaly layer is explainable AI-assisted monitoring, not a black-box ML system. For each borough and complaint type, the script compares daily volume against a prior 14-day rolling mean and standard deviation and also checks a 28-day IQR threshold. It flags unusually high spikes and generates recommended action text. This is appropriate for early operational monitoring because stakeholders can understand why a record was flagged.

## Stakeholder Advisory Explanation

I would run this as a consulting engagement in phases:

1. KPI definition and source-data validation.
2. Fabric architecture and security design.
3. Data pipeline and semantic model build.
4. Dashboard UAT with executives, analysts, and operations users.
5. Training, adoption, and weekly operating cadence.

The deliverable is not only a dashboard; it is a decision workflow for backlog triage and anomaly review.

## Likely Interviewer Q&A

**Q: Have you actually used Fabric here?**  
A: No. This repository is a local prototype that maps to Fabric components. I describe it as a Microsoft Fabric-ready implementation blueprint, not as a Fabric deployment. The Fabric docs show how I would migrate it into OneLake, Lakehouse, Warehouse, Data Factory/Dataflow Gen2, Notebooks, and Power BI.

**Q: Why DuckDB locally instead of Fabric?**  
A: DuckDB lets me build a reproducible portfolio project without requiring a cloud tenant. The SQL medallion pattern and star schema are portable to a Fabric Lakehouse or Warehouse, so the local tool proves the logic while the docs explain the target architecture.

**Q: How would you implement this for a real client?**  
A: I would start with KPI and data-quality workshops, create dev/test/prod Fabric workspaces, schedule ingestion into OneLake, build silver and gold tables, implement quality checks and anomaly notebooks, create a certified Power BI semantic model, and train users through a 30/60/90-day adoption plan.

**Q: Is this predictive modeling?**  
A: It is explainable anomaly detection, not forecasting. I would call it AI-assisted monitoring because it identifies unusual patterns and recommends review actions. A next step could be forecasting demand or classifying backlog risk once stakeholders validate the baseline process.

**Q: How do you know the KPIs are trustworthy?**  
A: The project includes quality checks for unique keys, created dates, invalid date ordering, borough normalization, non-negative resolution hours, and status normalization. The Power BI docs also include measure validation checks and metric certification guidance.

**Q: What would you improve next?**  
A: I would build a real `.pbix`, add incremental refresh, add CI tests with fixture data, deploy to a Fabric workspace when available, and extend the AI layer from anomaly detection to demand forecasting or backlog-risk scoring.

**Q: What makes this Senior Consultant-level?**  
A: It includes solution architecture, governance, delivery roadmap, stakeholder training, adoption cadence, and responsible AI notes in addition to the working data pipeline. That is the difference between a coding project and a consulting deliverable.
