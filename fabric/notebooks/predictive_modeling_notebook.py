"""Fabric Notebook-ready predictive modeling blueprint."""

from pathlib import Path
import sys


PROJECT_ROOT = Path.cwd()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predictive_modeling import train_model


if __name__ == "__main__":
    results = train_model()
    print(results["metrics"])
