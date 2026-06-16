# DAX Measures

These measures are written for a Power BI model with `fact_service_requests` as the request-grain fact table and dimensions related as described in `powerbi/README.md`. They are design-ready DAX definitions, not proof that a `.pbix` or Power BI Service semantic model has been created.

## Core Volume Measures

```DAX
Total Requests =
COUNTROWS ( fact_service_requests )

Open Requests =
CALCULATE (
    [Total Requests],
    fact_service_requests[is_open] = TRUE ()
)

Closed Requests =
CALCULATE (
    [Total Requests],
    fact_service_requests[is_closed] = TRUE ()
)

Backlog Rate =
DIVIDE ( [Open Requests], [Total Requests] )
```

## Resolution Measures

```DAX
Avg Resolution Hours =
AVERAGE ( fact_service_requests[resolution_hours] )

Median Resolution Hours =
MEDIAN ( fact_service_requests[resolution_hours] )

Closed Within 24 Hours =
CALCULATE (
    [Total Requests],
    fact_service_requests[closed_within_24h] = TRUE ()
)

Closed Within 24 Hours % =
DIVIDE ( [Closed Within 24 Hours], [Total Requests] )

Closed Within 7 Days =
CALCULATE (
    [Total Requests],
    fact_service_requests[closed_within_7d] = TRUE ()
)

Closed Within 7 Days % =
DIVIDE ( [Closed Within 7 Days], [Total Requests] )
```

## Trend Measures

```DAX
Prior Month Requests =
CALCULATE (
    [Total Requests],
    DATEADD ( dim_date[date_day], -1, MONTH )
)

MoM Request Growth % =
DIVIDE (
    [Total Requests] - [Prior Month Requests],
    [Prior Month Requests]
)
```

If the current imported sample covers only one month, `MoM Request Growth %` will be blank. That is expected and should be explained in the report notes.

## Anomaly And Risk Measures

If `anomalies` is imported as a standalone table:

```DAX
Anomaly Count =
COUNTROWS ( anomalies )

Max Anomaly Z-Score =
MAX ( anomalies[z_score] )
```

If `backlog_kpis` is imported as a standalone table:

```DAX
High Risk Backlog Count =
COUNTROWS (
    FILTER (
        backlog_kpis,
        backlog_kpis[high_risk_backlog_flag] = TRUE ()
    )
)

High Risk Backlog Flag =
IF ( [High Risk Backlog Count] > 0, "High Risk", "Monitor" )
```

If `ml_predictions` is imported as a standalone table:

```DAX
Predicted High Risk Count =
COUNTROWS (
    FILTER (
        ml_predictions,
        ml_predictions[predicted_high_risk_flag] = TRUE ()
    )
)

Avg Predicted Risk Probability =
AVERAGE ( ml_predictions[predicted_high_risk_probability] )

Max Predicted Risk Probability =
MAX ( ml_predictions[predicted_high_risk_probability] )
```

## Optional Closed-Date Measure

Use this only if `fact_service_requests[closed_date_key]` has an inactive relationship to `dim_date[date_key]`.

```DAX
Closed Requests By Closed Date =
CALCULATE (
    [Closed Requests],
    USERELATIONSHIP (
        fact_service_requests[closed_date_key],
        dim_date[date_key]
    )
)
```

## Formatting Guidance

| Measure | Format |
|---|---|
| `Total Requests`, `Open Requests`, `Closed Requests` | Whole number with thousands separator |
| `Backlog Rate` | Percentage, 1 decimal |
| `Avg Resolution Hours`, `Median Resolution Hours` | Decimal, 1 decimal |
| `Closed Within 24 Hours %`, `Closed Within 7 Days %` | Percentage, 1 decimal |
| `MoM Request Growth %` | Percentage, 1 decimal |
| `Max Anomaly Z-Score` | Decimal, 1 decimal |
| `Avg Predicted Risk Probability` | Percentage, 1 decimal |

## QA Tests For Measures

- `[Total Requests]` should match the number of rows in `fact_service_requests`.
- `[Backlog Rate]` should equal `[Open Requests] / [Total Requests]`.
- `[Closed Requests] + [Open Requests]` should equal `[Total Requests]` when status is normalized as closed versus not closed.
- Resolution-hour measures should ignore null values from open requests or invalid date-order records.
- Date slicers should use `dim_date[date_day]`, not raw date columns from the fact table.
- Predictive model measures should reconcile to `ml_predictions.csv` and remain clearly labeled as model outputs.

## Measure Certification Checklist

For a client implementation, each measure should be certified with:

| Field | Example |
|---|---|
| Business owner | Service operations lead |
| Technical owner | BI semantic model owner |
| Grain | Request-level fact table |
| Filters | Date, agency, borough, complaint type |
| Null handling | Resolution measures ignore null `resolution_hours` |
| Exception handling | Invalid date-order rows reviewed before SLA certification |
| Validation source | Gold SQL table row counts and KPI marts |

## Executive And Analyst Measure Use

Executive pages should prioritize:

- `Total Requests`
- `Backlog Rate`
- `Avg Resolution Hours`
- `Closed Within 7 Days %`
- `Anomaly Count`

Analyst pages can add:

- `Median Resolution Hours`
- `Closed Within 24 Hours %`
- `MoM Request Growth %`
- `Max Anomaly Z-Score`
- `High Risk Backlog Count`

## Governance Notes

- Treat closure-rate measures as operational proxies unless official SLA definitions are confirmed.
- Keep anomaly measures labeled as AI-assisted monitoring, not automated decisions.
- Keep predictive risk scores labeled as local model outputs unless an Azure ML deployment is actually configured.
- Do not certify measures until data-quality exception handling is agreed.
- If Power BI Service is used, document model endorsement, refresh ownership, and access controls.
