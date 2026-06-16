"""Azure ML-ready training entrypoint for NYC 311 backlog risk model."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


CATEGORICAL_FEATURES = ["agency", "borough"]
NUMERIC_FEATURES = [
    "total_requests",
    "avg_resolution_hours",
    "log_total_requests",
    "resolution_missing",
]
TARGET = "high_risk_backlog_flag"


def prepare_data(input_dir: Path) -> pd.DataFrame:
    path = input_dir / "backlog_kpis.csv"
    if not path.exists():
        raise FileNotFoundError(f"Expected training data at {path}")
    data = pd.read_csv(path)
    data[TARGET] = data[TARGET].astype(bool).astype(int)
    data["log_total_requests"] = np.log1p(data["total_requests"])
    data["resolution_missing"] = data["avg_resolution_hours"].isna().astype(int)
    data["avg_resolution_hours"] = data["avg_resolution_hours"].fillna(data["avg_resolution_hours"].median())
    return data


def build_model() -> Pipeline:
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", encoder, CATEGORICAL_FEATURES),
            ("numeric", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
    )
    return Pipeline(steps=[("preprocess", preprocessor), ("model", classifier)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = prepare_data(args.input_dir)
    X = data[CATEGORICAL_FEATURES + NUMERIC_FEATURES]
    y = data[TARGET]
    stratify = y if y.nunique() == 2 and y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42, stratify=stratify)

    model = build_model()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_score = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_score) if y_test.nunique() == 2 else float("nan")

    predictions = data[["agency", "borough", "total_requests", "backlog_rate", TARGET]].copy()
    predictions["predicted_high_risk_probability"] = model.predict_proba(X)[:, 1]
    predictions["predicted_high_risk_flag"] = model.predict(X).astype(bool)
    predictions.to_csv(args.output_dir / "ml_predictions.csv", index=False)

    report = "\n".join(
        [
            "# Azure ML Backlog Risk Training Report",
            "",
            f"- Rows: {len(data):,}",
            f"- Accuracy: {accuracy_score(y_test, y_pred):.3f}",
            f"- Precision: {precision_score(y_test, y_pred, zero_division=0):.3f}",
            f"- Recall: {recall_score(y_test, y_pred, zero_division=0):.3f}",
            f"- F1: {f1_score(y_test, y_pred, zero_division=0):.3f}",
            f"- ROC AUC: {roc_auc:.3f}",
            "",
            "This report is produced by an Azure ML-ready script. A real Azure ML run requires workspace configuration and job submission.",
        ]
    )
    (args.output_dir / "predictive_model_report.md").write_text(report, encoding="utf-8")
    (args.output_dir / "model_card.md").write_text(
        "# Model Card\n\nBacklog risk classifier for operational triage. Use with human review; not for automated decisions.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
