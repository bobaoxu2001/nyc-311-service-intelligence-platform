# Model Card: Backlog Risk Classifier

## Model Details

- Model type: `RandomForestClassifier`.
- Framework: scikit-learn.
- Training data: `outputs/sample_dashboard_data/backlog_kpis.csv`.
- Prediction output: `outputs/sample_dashboard_data/ml_predictions.csv`.

## Intended Use

Prioritize agency/borough combinations for backlog review and stakeholder discussion.

## Not Intended For

- Automated enforcement or staffing decisions.
- Individual-level decisioning.
- Production deployment without stakeholder validation and monitoring.

## Data

- Rows: 76.
- Positive target rate: 59.2%.
- Source data: public NYC Open Data 311 service requests transformed into gold KPI tables.

## Performance Snapshot

- F1: 1.000.
- Recall: 1.000.
- ROC AUC: 1.000.

## Top Features

- `numeric__total_requests`: 0.272
- `numeric__avg_resolution_hours`: 0.247
- `numeric__log_total_requests`: 0.196
- `categorical__agency_NYPD`: 0.083
- `numeric__resolution_missing`: 0.037
- `categorical__agency_DHS`: 0.032
- `categorical__agency_DEP`: 0.022
- `categorical__borough_BROOKLYN`: 0.014

## Ethical And Operational Considerations

- Scores should support human triage, not replace manager judgment.
- Public data can still contain granular location context; report broad audiences should use aggregated views.
- Thresholds should be reviewed with operations owners before production use.
- Model performance should be monitored after each major refresh or process change.