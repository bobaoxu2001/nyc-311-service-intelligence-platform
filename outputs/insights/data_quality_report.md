# Data Quality Report

This report validates the NYC 311 silver layer before the data is used in Power BI-ready gold tables.

| Rule | Severity | Failed Records | Pass Rate | Status |
|---|---:|---:|---:|---|
| unique_key uniqueness | high | 0 | 100.00% | PASS |
| created_date not null | high | 0 | 100.00% | PASS |
| closed_date greater than or equal to created_date when closed | high | 17 | 99.98% | REVIEW |
| valid borough values | medium | 0 | 100.00% | PASS |
| resolution_hours non-negative | high | 0 | 100.00% | PASS |
| status normalization | medium | 0 | 100.00% | PASS |

## Validation Rules

- `unique_key` should identify one service request.
- `created_date` is required for trend, SLA, and backlog analysis.
- `closed_date` should be greater than or equal to `created_date` when present.
- Borough names are normalized to the five NYC boroughs plus `UNKNOWN`.
- `resolution_hours` must be non-negative.
- Status values are trimmed, uppercased, and blank-safe.