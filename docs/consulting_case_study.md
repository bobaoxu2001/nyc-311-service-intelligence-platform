# Consulting Case Study

## Client Scenario

A public-sector service operations team receives thousands of 311 requests across agencies, boroughs, and complaint categories. Leadership needs a single view of demand, backlog, resolution performance, and unusual spikes that may require operational response.

## Business Questions

1. Which boroughs and complaint types drive the most service demand?
2. Which agencies have the highest volume, backlog rate, or resolution-time risk?
3. Where are open requests concentrated?
4. Which daily request spikes look unusual compared with recent history?
5. What actions should the client prioritize in the next 30 days?

## Consulting Approach

### 1. Data Foundation

The project ingests public NYC Open Data 311 records from Socrata dataset `erm2-nwe9`. The local default is 100,000 recent records, and the ingestion limit is configurable.

### 2. Analytics Engineering

The pipeline uses a medallion pattern:

- Bronze: raw records stored locally as parquet.
- Silver: cleaned fields, parsed dates, normalized dimensions, resolution metrics, and data-quality flags.
- Gold: Power BI-ready star schema and KPI tables.

### 3. KPI Design

The gold layer calculates total requests, open requests, closed requests, backlog rate, average and median resolution hours, percent closed within 24 hours, percent closed within 7 days, top complaint types, borough volume, agency performance, and high-risk agency/borough combinations.

### 4. AI And Analytics

The anomaly detector flags unusual daily volume spikes by complaint type and borough. It uses rolling mean, z-score, and IQR logic so the method can be explained to non-technical stakeholders.

### 5. Executive Communication

The project produces an executive summary, dashboard mockups, data-quality report, implementation roadmap, and interview talk track. These are designed to show how technical work becomes client-ready communication.

## Current Sample Findings

- The sample contains 100,000 public NYC 311 service requests.
- Open requests represent 28.0% of the sample.
- Average resolution time is 15.5 hours.
- 73.6% of requests were closed within 7 days.
- Illegal Parking is the highest-volume complaint type.
- Brooklyn is the highest-volume borough.
- The anomaly monitor detected 15 daily spikes.
- The data-quality report flagged 17 invalid closed-date ordering records for review.

## Recommended Client Actions

1. Run a backlog triage sprint focused on the highest-risk agency/borough combinations.
2. Validate anomaly events with operations teams to separate real service events from data/reporting artifacts.
3. Certify KPI definitions before executive rollout, especially backlog rate and resolution-time metrics.
4. Stand up a weekly operating cadence for anomaly review, backlog aging, and agency performance.
5. Move the local pattern into Fabric only after KPI definitions and quality thresholds are agreed.

## What This Demonstrates

This project demonstrates analytics consulting judgment: start with a client problem, build a governed data model, validate the data, design decision-ready reporting, add explainable AI where it helps, and translate the results into practical next steps.
