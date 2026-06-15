# DAX Measures

Use these measures after importing the CSV outputs into Power BI Desktop.

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

Avg Resolution Hours =
AVERAGE ( fact_service_requests[resolution_hours] )

Median Resolution Hours =
MEDIAN ( fact_service_requests[resolution_hours] )

Closed Within 24 Hours % =
DIVIDE (
    CALCULATE ( [Total Requests], fact_service_requests[closed_within_24h] = TRUE () ),
    [Total Requests]
)

Closed Within 7 Days % =
DIVIDE (
    CALCULATE ( [Total Requests], fact_service_requests[closed_within_7d] = TRUE () ),
    [Total Requests]
)

Prior Month Requests =
CALCULATE (
    [Total Requests],
    DATEADD ( dim_date[date_day], -1, MONTH )
)

MoM Request Growth % =
DIVIDE ( [Total Requests] - [Prior Month Requests], [Prior Month Requests] )

Anomaly Count =
COUNTROWS ( anomalies )

High Risk Backlog Flag =
IF (
    COUNTROWS (
        FILTER ( backlog_kpis, backlog_kpis[high_risk_backlog_flag] = TRUE () )
    ) > 0,
    "High Risk",
    "Monitor"
)
```

## Display Formatting

- Format `Backlog Rate`, `Closed Within 24 Hours %`, `Closed Within 7 Days %`, and `MoM Request Growth %` as percentages.
- Format average and median resolution hours with one decimal place.
- Use conditional formatting on `High Risk Backlog Flag`.
