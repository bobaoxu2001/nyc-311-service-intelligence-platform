# Power BI Page Wireframes

These wireframes describe report design. They are not Power BI screenshots.

## Page 1: Executive Operations Overview

- KPI cards: Total Requests, Backlog Rate, Avg Resolution Hours, Closed Within 7 Days %.
- Line chart: requests by day/month.
- Bar chart: top complaint types.
- Bar/line combo: borough volume and backlog rate.
- Text box: data-quality caveat and latest executive recommendation.

## Page 2: Agency Performance & Backlog Risk

- Ranking table: agency, total requests, backlog rate, avg resolution hours.
- Scatter plot: volume versus backlog rate, sized by resolution time.
- Matrix: agency by borough high-risk flag.
- Conditional formatting for backlog and SLA risk.

## Page 3: Borough & Complaint Demand Intelligence

- Borough volume bar chart.
- Complaint mix heatmap.
- Map visual using latitude/longitude if governance permits.
- Drillthrough button to complaint detail.

## Page 4: AI Risk & Anomaly Monitor

- KPI cards: anomaly count, max z-score, latest spike.
- Table: date, borough, complaint type, total requests, baseline, z-score, recommended action.
- Trend chart with anomaly markers.
- Human review status field for production implementation.

## Page 5: Predictive Backlog Risk

- KPI cards: predicted high-risk count, average risk probability.
- Table: agency, borough, current backlog rate, predicted probability, predicted flag.
- Bar chart: top predicted risk combinations.
- Model notes panel: local scikit-learn model, not Azure ML deployment unless submitted.
