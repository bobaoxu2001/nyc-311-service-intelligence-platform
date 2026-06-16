# Azure AI Extension Options

These are optional future extensions. They are not implemented in the current repository. The repository does include local scikit-learn predictive modeling and Azure ML-ready job assets, but it does not call Azure Cognitive Services.

## Azure AI Language

Use case:

- Classify or cluster resolution descriptions.
- Extract complaint themes from free-text fields.
- Summarize common resolution patterns by agency or complaint type.

Responsible use:

- Review text fields for privacy and sensitivity.
- Keep human review for generated themes.
- Validate taxonomy quality with operations users.

## Azure OpenAI / Copilot-Style Executive Narrative

Use case:

- Generate draft executive summaries from certified KPI tables.
- Produce weekly narrative updates for backlog and anomaly review.

Responsible use:

- Ground prompts only in certified data outputs.
- Require human approval before sharing.
- Log source tables and generated narrative versions.
- Avoid hallucinated causes for anomalies.

## Azure ML Demand Forecasting

Use case:

- Forecast request volume by borough and complaint type.
- Predict backlog risk using historical demand, closure rates, and agency capacity proxies.

Responsible use:

- Monitor model drift and seasonal effects.
- Document limitations and confidence intervals.
- Use predictions for planning, not automated service decisions.

## Cognitive Services Not Added Here

The current repo does not call Azure Cognitive Services because the local public-data prototype has no configured Azure credentials and no validated need for external cognitive APIs. The implemented AI component is local, explainable backlog-risk modeling and anomaly detection.
