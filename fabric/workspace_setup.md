# Fabric Workspace Setup

Recommended workspace structure:

| Workspace | Purpose |
|---|---|
| `nyc311-dev` | Development and experimentation. |
| `nyc311-test` | UAT, refresh validation, and stakeholder signoff. |
| `nyc311-prod` | Certified semantic model and production report. |

## Core Items

- Lakehouse: `lh_nyc311_service_intelligence`
- Warehouse: `wh_nyc311_service_intelligence`
- Pipeline: `pl_nyc311_daily_refresh`
- Notebooks:
  - `nb_quality_checks`
  - `nb_anomaly_detection`
  - `nb_predictive_modeling`
- Semantic model: `sm_nyc311_service_intelligence`
- Report: `rpt_nyc311_service_intelligence`

## Security

- Use security groups for workspace access.
- Restrict edit/admin permissions to delivery and platform owners.
- Use viewer roles for broad dashboard consumers.
- Review request-level location access before enabling drillthrough pages.
- Certify the semantic model only after KPI signoff.

## Monitoring

- Track pipeline duration, refresh failures, quality failures, and anomaly counts.
- Route failures to named owners.
- Review usage metrics monthly after deployment.
