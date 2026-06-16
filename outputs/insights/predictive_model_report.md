# Predictive Model Report

## Business Objective

Prioritize agency/borough combinations that are likely to require backlog triage. The model is a local ML demonstration that supports operational review; it is not an automated decisioning system.

## Target Variable

- `high_risk_backlog_flag` from `backlog_kpis.csv`.
- Positive class means the agency/borough row meets the backlog-risk rule used in the gold KPI layer.

## Features Used

- `agency`
- `borough`
- `total_requests`
- `avg_resolution_hours`
- `log_total_requests`
- `resolution_missing`

## Train/Test Split

- 70/30 split with `random_state=42`.
- Stratified split is used when both target classes have enough examples.
- Training rows available: **76** agency/borough combinations.

## Evaluation Metrics

| Metric | Value |
|---|---:|
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| ROC AUC | 1.000 |

## Confusion Matrix

| Actual / Predicted | Low Risk | High Risk |
|---|---:|---:|
| Low Risk | 9 | 0 |
| High Risk | 0 | 14 |

## Top Drivers

| Feature | Importance |
|---|---:|
| `numeric__total_requests` | 0.272 |
| `numeric__avg_resolution_hours` | 0.247 |
| `numeric__log_total_requests` | 0.196 |
| `categorical__agency_NYPD` | 0.083 |
| `numeric__resolution_missing` | 0.037 |
| `categorical__agency_DHS` | 0.032 |
| `categorical__agency_DEP` | 0.022 |
| `categorical__borough_BROOKLYN` | 0.014 |
| `categorical__borough_MANHATTAN` | 0.013 |
| `categorical__borough_STATEN ISLAND` | 0.012 |
| `categorical__borough_BRONX` | 0.011 |
| `categorical__borough_UNKNOWN` | 0.010 |

## Classification Report

```text
precision    recall  f1-score   support

           0       1.00      1.00      1.00         9
           1       1.00      1.00      1.00        14

    accuracy                           1.00        23
   macro avg       1.00      1.00      1.00        23
weighted avg       1.00      1.00      1.00        23
```

## Limitations

- The sample is small at the agency/borough grain.
- The target is derived from the current backlog rule, so the model demonstrates supervised prioritization rather than an independently observed future outcome.
- Direct same-period backlog-rate features are intentionally excluded to reduce target leakage in this portfolio model.
- Results should be validated with operations stakeholders before use.
- This is local scikit-learn training, not an Azure ML registered model.

## Productionization Path

- In Fabric: run as a scheduled Notebook after gold KPI marts refresh.
- In Azure ML: submit `azureml/job.yml` to train and register the model using generated KPI CSV inputs.
- In Power BI: import `ml_predictions.csv` as an AI risk prioritization table and expose the probability score on the AI Risk Monitor page.

## Responsible AI Notes

- Use the score to prioritize review, not to automate service decisions.
- Keep a human-in-the-loop review for high-risk flags.
- Monitor drift, false positives, and stakeholder feedback before production rollout.