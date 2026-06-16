# Dashboard Design

The PNGs in `docs/dashboard_mockups/` are static previews generated from CSV outputs. They are intended to show dashboard design thinking for portfolio review. A real Power BI implementation would use the documented semantic model relationships and DAX measures in `powerbi/`.

## Page 1: Executive Operations Overview

Audience: city operations executives or client service leaders.

Visuals:

- KPI cards: total requests, backlog rate, average resolution hours, closed within 7 days.
- Monthly request trend with month-over-month growth.
- Top complaint types by request volume.
- Borough request volume summary.
- Executive recommendation text box from `outputs/insights/executive_summary.md`.

Primary question: Where is demand rising, and is service performance keeping up?

## Page 2: Agency Performance & Backlog Risk

Audience: agency managers and transformation leads.

Visuals:

- Agency ranking table by volume, backlog rate, average resolution time, and closed within 7 days.
- Scatter plot: total request volume versus backlog rate, sized by average resolution hours.
- High-risk agency/borough matrix using `backlog_kpis`.

Primary question: Which agencies need workflow review, staffing support, or SLA escalation?

## Page 3: Borough / Complaint Demand Intelligence

Audience: operations analysts and local service teams.

Visuals:

- Borough comparison bar chart.
- Complaint type mix by borough.
- Map visual using latitude and longitude where available.
- Drillthrough table for request-level examples.

Primary question: Which borough and complaint combinations are driving demand?

## Page 4: AI Risk & Anomaly Monitor

Audience: analytics leads and operations response teams.

Visuals:

- Anomaly table by date, complaint type, borough, total requests, z-score, and recommended action.
- Daily trend chart with anomaly markers.
- High-risk backlog flag table.
- Action tracker panel for root-cause review, staffing review, and communications follow-up.

Primary question: Which unusual spikes or backlog risks require proactive intervention?

Important note: anomaly outputs should be framed as explainable AI-assisted monitoring that supports human review, not as automated decisioning.
