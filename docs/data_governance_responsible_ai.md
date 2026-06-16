# Data Governance And Responsible AI

This project uses public NYC 311 data and explainable statistical anomaly detection. It does not use a black-box LLM system, Azure ML deployment, or automated decisioning workflow.

## Data Quality Controls

Implemented controls:

- `unique_key` uniqueness check.
- `created_date` required check.
- `closed_date >= created_date` validation when closed date exists.
- Valid borough normalization.
- Non-negative `resolution_hours`.
- Status normalization.

Outputs:

- `outputs/insights/data_quality_report.md`
- `outputs/insights/data_quality_report.csv`

## Metric Certification

Recommended certification workflow:

1. Define each KPI with business stakeholders.
2. Validate formulas against source records.
3. Document exclusions, null handling, and open-request handling.
4. Assign a metric owner.
5. Certify DAX measures in the Power BI semantic model.

Metrics requiring extra review:

- Backlog rate, because "open" depends on status interpretation.
- Resolution hours, because open records and invalid date-order records need explicit treatment.
- Closed-within-24-hours and closed-within-7-days, because these are SLA proxies rather than official service commitments unless confirmed by the client.

## Access And Security Considerations

The source dataset is public, but a client implementation should still apply:

- Least-privilege workspace access.
- Separate dev/test/prod workspaces.
- Certified semantic model permissions.
- Refresh and admin ownership.
- Audit trail for transformations and semantic model changes.
- Clear rules for exporting request-level data.

## Privacy Considerations

NYC 311 data is public, but request-level records may include location details such as address, zip code, latitude, and longitude. A client implementation should:

- Avoid exposing unnecessary request-level location detail to broad audiences.
- Use aggregation for executive dashboards.
- Review map visuals and drillthrough pages for privacy sensitivity.
- Apply row-level or object-level security if internal enrichment data is added.

## Responsible AI Principles

The anomaly layer should follow these principles:

- **Explainability:** use transparent rolling baselines and z-score/IQR logic.
- **Human oversight:** require operational review before escalation.
- **Proportionality:** use anomaly detection for prioritization, not automated enforcement.
- **Reliability:** monitor false positives and threshold drift.
- **Documentation:** publish methodology, limitations, and owner responsibilities.

## Anomaly Detection Explainability

The detector groups records by borough and complaint type, then compares daily volume with recent history:

- Prior 14-day rolling mean.
- Prior 14-day rolling standard deviation.
- Z-score threshold.
- Prior 28-day IQR upper bound.

This makes it possible to explain why a spike was flagged and whether the signal is operationally meaningful.

## Human-In-The-Loop Review

Recommended workflow:

1. Analytics job flags anomaly.
2. Analyst reviews volume, borough, complaint type, and recent baseline.
3. Operations owner confirms whether weather, seasonality, staffing, events, or system changes explain the spike.
4. Escalation is opened only after validation.
5. Outcome is documented for threshold tuning.

## Model Limitations

- The current method detects spikes, not root causes.
- It does not forecast future demand.
- It can flag expected seasonality if the history window is short.
- It depends on source-data timeliness and status accuracy.
- It should be tuned with stakeholder feedback before production use.

## Monitoring And Escalation

Recommended controls:

- Track anomaly count by week.
- Track reviewed versus unresolved anomalies.
- Track false-positive patterns.
- Trigger alerts only after quality checks pass.
- Review thresholds monthly with operations stakeholders.
