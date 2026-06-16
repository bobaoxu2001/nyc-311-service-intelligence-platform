# Azure ML Implementation Package

This folder contains Azure ML-ready training assets for the backlog-risk predictive model. No Azure ML job has been submitted from this repository unless a real Azure CLI login, subscription, resource group, and workspace are configured.

## Prerequisites

```bash
az login
az extension add --name ml
az account set --subscription "<subscription-id>"
```

Required Azure resources:

- Azure ML workspace.
- Resource group.
- Compute target or serverless job support.
- Access to generated project CSV outputs, especially `outputs/sample_dashboard_data/backlog_kpis.csv`.

## Local Input Expected

The training script expects this file:

```text
outputs/sample_dashboard_data/backlog_kpis.csv
```

Generate it locally first:

```bash
make transform
```

## Submit The Job

From the repository root:

```bash
az ml job create \
  --file azureml/job.yml \
  --resource-group "<resource-group>" \
  --workspace-name "<workspace-name>"
```

## Expected Outputs

The job writes:

- `ml_predictions.csv`
- `predictive_model_report.md`
- `model_card.md`

In a production Azure ML setup, these should be stored as job outputs and optionally registered with the model package or pushed to a governed storage location.

## Truthfulness Note

This package is **Azure ML-ready**. It does not prove an Azure ML deployment or submitted run unless a real job ID, workspace, logs, and outputs are produced in a configured Azure environment.
