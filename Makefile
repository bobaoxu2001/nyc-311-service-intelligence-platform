PYTHON ?= python3
LIMIT ?= 100000

.PHONY: install ingest transform quality anomalies insights predictive-model dashboard-mockups all clean-outputs

install:
	$(PYTHON) -m pip install -r requirements.txt

ingest:
	$(PYTHON) src/ingest_311.py --limit $(LIMIT)

transform:
	$(PYTHON) src/transform_311.py

quality:
	$(PYTHON) src/quality_checks.py

anomalies:
	$(PYTHON) src/anomaly_detection.py

insights:
	$(PYTHON) src/generate_insights.py

predictive-model:
	$(PYTHON) src/predictive_modeling.py

dashboard-mockups:
	$(PYTHON) src/generate_dashboard_mockups.py

all: ingest transform quality anomalies insights predictive-model dashboard-mockups

clean-outputs:
	rm -f outputs/insights/*.md outputs/insights/*.csv
	rm -f outputs/sample_dashboard_data/*.csv
	rm -f docs/dashboard_mockups/*.png
