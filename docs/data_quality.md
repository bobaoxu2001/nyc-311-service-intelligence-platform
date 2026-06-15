# Data Quality Framework

The project validates the silver layer before using it for gold KPI tables and Power BI reporting.

## Validation Rules

| Rule | Business Reason | Expected Result |
|---|---|---|
| `unique_key` uniqueness | One request should map to one operational case. | No duplicated keys. |
| `created_date` not null | Trend, SLA, and backlog metrics require a request start date. | No null created timestamps. |
| `closed_date >= created_date` when closed | Negative resolution time indicates source or parsing issues. | No invalid date ordering. |
| Valid borough values | Borough reporting should use NYC boroughs plus `UNKNOWN`. | All values are standardized. |
| `resolution_hours` non-negative | Resolution KPIs must be interpretable. | No negative resolution durations. |
| Status normalization | Open/closed KPIs require consistent status logic. | Blank statuses are converted to `UNKNOWN`. |

## Outputs

Running `python src/quality_checks.py` creates:

- `outputs/insights/data_quality_report.csv`
- `outputs/insights/data_quality_report.md`

## Consulting Interpretation

Data-quality exceptions are not automatically removed from the dataset. They are flagged so analysts can quantify their impact, discuss them with process owners, and decide whether a KPI should be certified for executive reporting.
