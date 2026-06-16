# Power BI Service / Fabric Workspace Deployment Plan

This is a deployment plan, not proof of a published Power BI Service report.

## Prerequisites

- Fabric or Power BI workspace access.
- Gold tables available through Fabric Warehouse, Lakehouse SQL endpoint, or imported CSVs for a prototype.
- Approved KPI definitions.
- Workspace security groups.

## Deployment Steps

1. Create semantic model from gold tables.
2. Configure relationships and DAX measures.
3. Build report pages from `page_wireframes.md`.
4. Validate semantic model using `semantic_model_validation.md`.
5. Configure refresh schedule.
6. Apply workspace roles.
7. Promote semantic model/report from dev to test to prod.
8. Certify or promote semantic model after stakeholder signoff.

## Deployment Pipeline Notes

- Use dev/test/prod workspaces.
- Use parameterized data source connections.
- Validate refresh and row counts after each promotion.
- Keep DAX and report changes under change control.

## Security / Roles

- Executives: report viewer access.
- Analysts: build permission on certified semantic model.
- Developers: workspace contributor in dev/test only.
- Admins: limited platform ownership group.

## Remaining Gap

No `.pbix`, `.pbip`, or Power BI Service artifact is included unless created in a real Power BI environment.
