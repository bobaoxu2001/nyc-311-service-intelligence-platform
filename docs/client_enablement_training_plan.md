# Client Enablement And Training Plan

This plan describes how a consulting team would help a client adopt the NYC 311 Service Intelligence Platform after the analytics model and dashboards are built.

## Stakeholder Groups

| Stakeholder | Needs |
|---|---|
| Executives | High-level demand, backlog, SLA proxy, and risk narrative. |
| Agency managers | Agency performance, queue triage, and operational actions. |
| Analysts | Semantic model, DAX measures, data-quality rules, anomaly outputs. |
| Operations users | Weekly action queue, anomaly validation, escalation workflow. |
| Data platform owners | Refresh cadence, security, monitoring, deployment pipeline. |

## KPI Certification Workshop

Workshop agenda:

1. Review source fields and known data limitations.
2. Confirm definitions for total, open, and closed requests.
3. Confirm resolution-hour logic and invalid date handling.
4. Confirm SLA proxy metrics.
5. Approve backlog risk thresholds.
6. Assign metric owners and review cadence.

Outputs:

- Certified KPI list.
- Exception-handling rules.
- Semantic model owner.
- Change-control process.

## Training Plan

### Executive Training

Duration: 45 minutes

Focus:

- Reading the Executive Operations Overview.
- Interpreting backlog rate and resolution-time trends.
- Understanding what anomaly flags mean and do not mean.
- Using the dashboard for monthly operating reviews.

### Analyst Training

Duration: 90 minutes

Focus:

- Star schema and relationships.
- DAX measure definitions.
- Data-quality outputs.
- Anomaly detection methodology.
- How to validate totals against gold tables.

### Operations User Training

Duration: 60 minutes

Focus:

- Agency and borough drilldowns.
- Backlog action queue.
- Human-in-the-loop anomaly review.
- Escalation and documentation workflow.

## Dashboard Adoption Plan

- Pilot with a small group of analysts and agency managers.
- Collect feedback on KPI wording, filters, and actionability.
- Publish certified report pages after UAT.
- Create a recurring weekly operations review using the same dashboard.
- Track adoption through active users, review attendance, and action closure.

## Operating Cadence

| Cadence | Activity | Owner |
|---|---|---|
| Daily | Refresh data, run quality checks, generate anomaly events. | Data platform owner |
| Weekly | Review backlog risk and anomaly queue. | Operations lead |
| Monthly | Executive service performance review. | Executive sponsor |
| Quarterly | KPI, threshold, and roadmap review. | Analytics product owner |

## Documentation Handoff

Handoff package:

- Architecture diagram.
- Source-to-target mapping.
- KPI and DAX catalog.
- Data-quality rules and exception process.
- Dashboard user guide.
- Refresh monitoring runbook.
- Responsible AI and anomaly methodology note.

## 30/60/90-Day Rollout Plan

### First 30 Days

- Validate KPI definitions.
- Build or confirm Fabric workspace structure.
- Run dashboard pilot on sample or limited production data.
- Review quality exceptions with stakeholders.

### First 60 Days

- Implement scheduled refresh.
- Publish certified semantic model.
- Train executives, analysts, and operations users.
- Establish weekly anomaly and backlog review.

### First 90 Days

- Expand to full-history incremental refresh.
- Add backlog aging and SLA tiering.
- Tune anomaly thresholds based on feedback.
- Formalize support ownership and enhancement backlog.
