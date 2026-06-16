"""Train a local backlog-risk classifier from generated KPI outputs.

This is a real local ML component for the portfolio project. It is deliberately
small, explainable, and fast: the goal is to demonstrate implementation-ready
analytics, not to overstate production ML maturity.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "outputs" / "sample_dashboard_data"
INSIGHTS_DIR = PROJECT_ROOT / "outputs" / "insights"
PREDICTIONS_PATH = DATA_DIR / "ml_predictions.csv"
REPORT_PATH = INSIGHTS_DIR / "predictive_model_report.md"
MODEL_CARD_PATH = INSIGHTS_DIR / "model_card.md"

CATEGORICAL_FEATURES = ["agency", "borough"]
NUMERIC_FEATURES = [
    "total_requests",
    "avg_resolution_hours",
    "log_total_requests",
    "resolution_missing",
]
TARGET = "high_risk_backlog_flag"


def load_training_data() -> pd.DataFrame:
    path = DATA_DIR / "backlog_kpis.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run `make transform` first.")

    data = pd.read_csv(path)
    required = {"agency", "borough", "total_requests", "open_requests", "closed_requests", "backlog_rate", "avg_resolution_hours", TARGET}
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")

    model_data = data.copy()
    model_data[TARGET] = model_data[TARGET].astype(bool).astype(int)
    model_data["log_total_requests"] = np.log1p(model_data["total_requests"])
    model_data["resolution_missing"] = model_data["avg_resolution_hours"].isna().astype(int)
    model_data["avg_resolution_hours"] = model_data["avg_resolution_hours"].fillna(model_data["avg_resolution_hours"].median())
    return model_data


def build_pipeline() -> Pipeline:
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", encoder, CATEGORICAL_FEATURES),
            ("numeric", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
        ],
        remainder="drop",
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
    )

    return Pipeline(steps=[("preprocess", preprocessor), ("model", classifier)])


def get_feature_importance(pipeline: Pipeline) -> pd.DataFrame:
    preprocessor = pipeline.named_steps["preprocess"]
    model = pipeline.named_steps["model"]
    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = np.array(CATEGORICAL_FEATURES + NUMERIC_FEATURES)

    return (
        pd.DataFrame({"feature": feature_names, "importance": model.feature_importances_})
        .sort_values("importance", ascending=False)
        .head(12)
    )


def train_model() -> dict[str, object]:
    data = load_training_data()
    X = data[CATEGORICAL_FEATURES + NUMERIC_FEATURES]
    y = data[TARGET]

    stratify = y if y.nunique() == 2 and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=stratify,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_score = pipeline.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_score) if y_test.nunique() == 2 else np.nan

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc,
    }

    scored = data[["agency", "borough", "total_requests", "open_requests", "closed_requests", "backlog_rate", "avg_resolution_hours", TARGET]].copy()
    scored["predicted_high_risk_probability"] = pipeline.predict_proba(X)[:, 1]
    scored["predicted_high_risk_flag"] = pipeline.predict(X).astype(bool)
    scored["model_name"] = "RandomForestClassifier"
    scored["scoring_note"] = "Local portfolio model; use for prioritization only after stakeholder validation."
    scored = scored.sort_values(["predicted_high_risk_probability", "total_requests"], ascending=[False, False])

    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    scored.to_csv(PREDICTIONS_PATH, index=False)

    importance = get_feature_importance(pipeline)
    write_report(data, metrics, confusion_matrix(y_test, y_pred), classification_report(y_test, y_pred, zero_division=0), importance)
    write_model_card(data, metrics, importance)

    print(f"Saved predictions to {PREDICTIONS_PATH}")
    print(f"Saved model report to {REPORT_PATH}")
    print(f"Saved model card to {MODEL_CARD_PATH}")
    return {"metrics": metrics, "predictions": scored, "importance": importance}


def write_report(
    data: pd.DataFrame,
    metrics: dict[str, float],
    matrix: np.ndarray,
    class_report: str,
    importance: pd.DataFrame,
) -> None:
    lines = [
        "# Predictive Model Report",
        "",
        "## Business Objective",
        "",
        "Prioritize agency/borough combinations that are likely to require backlog triage. The model is a local ML demonstration that supports operational review; it is not an automated decisioning system.",
        "",
        "## Target Variable",
        "",
        "- `high_risk_backlog_flag` from `backlog_kpis.csv`.",
        "- Positive class means the agency/borough row meets the backlog-risk rule used in the gold KPI layer.",
        "",
        "## Features Used",
        "",
        *[f"- `{feature}`" for feature in CATEGORICAL_FEATURES + NUMERIC_FEATURES],
        "",
        "## Train/Test Split",
        "",
        "- 70/30 split with `random_state=42`.",
        "- Stratified split is used when both target classes have enough examples.",
        f"- Training rows available: **{len(data):,}** agency/borough combinations.",
        "",
        "## Evaluation Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Accuracy | {metrics['accuracy']:.3f} |",
        f"| Precision | {metrics['precision']:.3f} |",
        f"| Recall | {metrics['recall']:.3f} |",
        f"| F1 | {metrics['f1']:.3f} |",
        f"| ROC AUC | {metrics['roc_auc']:.3f} |",
        "",
        "## Confusion Matrix",
        "",
        "| Actual / Predicted | Low Risk | High Risk |",
        "|---|---:|---:|",
        f"| Low Risk | {int(matrix[0][0])} | {int(matrix[0][1])} |",
        f"| High Risk | {int(matrix[1][0])} | {int(matrix[1][1])} |",
        "",
        "## Top Drivers",
        "",
        "| Feature | Importance |",
        "|---|---:|",
    ]
    for row in importance.itertuples(index=False):
        lines.append(f"| `{row.feature}` | {row.importance:.3f} |")

    lines.extend(
        [
            "",
            "## Classification Report",
            "",
            "```text",
            class_report.strip(),
            "```",
            "",
            "## Limitations",
            "",
            "- The sample is small at the agency/borough grain.",
            "- The target is derived from the current backlog rule, so the model demonstrates supervised prioritization rather than an independently observed future outcome.",
            "- Direct same-period backlog-rate features are intentionally excluded to reduce target leakage in this portfolio model.",
            "- Results should be validated with operations stakeholders before use.",
            "- This is local scikit-learn training, not an Azure ML registered model.",
            "",
            "## Productionization Path",
            "",
            "- In Fabric: run as a scheduled Notebook after gold KPI marts refresh.",
            "- In Azure ML: submit `azureml/job.yml` to train and register the model using generated KPI CSV inputs.",
            "- In Power BI: import `ml_predictions.csv` as an AI risk prioritization table and expose the probability score on the AI Risk Monitor page.",
            "",
            "## Responsible AI Notes",
            "",
            "- Use the score to prioritize review, not to automate service decisions.",
            "- Keep a human-in-the-loop review for high-risk flags.",
            "- Monitor drift, false positives, and stakeholder feedback before production rollout.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_model_card(data: pd.DataFrame, metrics: dict[str, float], importance: pd.DataFrame) -> None:
    lines = [
        "# Model Card: Backlog Risk Classifier",
        "",
        "## Model Details",
        "",
        "- Model type: `RandomForestClassifier`.",
        "- Framework: scikit-learn.",
        "- Training data: `outputs/sample_dashboard_data/backlog_kpis.csv`.",
        "- Prediction output: `outputs/sample_dashboard_data/ml_predictions.csv`.",
        "",
        "## Intended Use",
        "",
        "Prioritize agency/borough combinations for backlog review and stakeholder discussion.",
        "",
        "## Not Intended For",
        "",
        "- Automated enforcement or staffing decisions.",
        "- Individual-level decisioning.",
        "- Production deployment without stakeholder validation and monitoring.",
        "",
        "## Data",
        "",
        f"- Rows: {len(data):,}.",
        f"- Positive target rate: {data[TARGET].mean():.1%}.",
        "- Source data: public NYC Open Data 311 service requests transformed into gold KPI tables.",
        "",
        "## Performance Snapshot",
        "",
        f"- F1: {metrics['f1']:.3f}.",
        f"- Recall: {metrics['recall']:.3f}.",
        f"- ROC AUC: {metrics['roc_auc']:.3f}.",
        "",
        "## Top Features",
        "",
    ]
    for row in importance.head(8).itertuples(index=False):
        lines.append(f"- `{row.feature}`: {row.importance:.3f}")

    lines.extend(
        [
            "",
            "## Ethical And Operational Considerations",
            "",
            "- Scores should support human triage, not replace manager judgment.",
            "- Public data can still contain granular location context; report broad audiences should use aggregated views.",
            "- Thresholds should be reviewed with operations owners before production use.",
            "- Model performance should be monitored after each major refresh or process change.",
        ]
    )
    MODEL_CARD_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    train_model()
