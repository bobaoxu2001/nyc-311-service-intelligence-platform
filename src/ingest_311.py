"""Ingest NYC 311 Service Requests from NYC Open Data.

The default sample is intentionally manageable for a portfolio project while
the --limit argument keeps the pipeline scalable for larger local runs.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATASET_ID = "erm2-nwe9"
API_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"
DATASET_PAGE = "https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9"

SELECT_COLUMNS = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "location_type",
    "incident_zip",
    "incident_address",
    "street_name",
    "cross_street_1",
    "cross_street_2",
    "status",
    "due_date",
    "resolution_description",
    "borough",
    "latitude",
    "longitude",
]


def fetch_chunk(limit: int, offset: int) -> list[dict[str, Any]]:
    params = {
        "$select": ",".join(SELECT_COLUMNS),
        "$order": "created_date DESC",
        "$limit": limit,
        "$offset": offset,
    }
    response = requests.get(API_URL, params=params, timeout=90)
    response.raise_for_status()
    return response.json()


def ingest(limit: int, chunk_size: int) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    for offset in range(0, limit, chunk_size):
        current_limit = min(chunk_size, limit - offset)
        chunk = fetch_chunk(current_limit, offset)
        if not chunk:
            break
        records.extend(chunk)
        print(f"Fetched {len(records):,} records")
        if len(chunk) < current_limit:
            break

    if not records:
        raise RuntimeError("No records returned from NYC Open Data.")

    raw = pd.DataFrame.from_records(records)
    for column in SELECT_COLUMNS:
        if column not in raw.columns:
            raw[column] = pd.NA
    raw = raw[SELECT_COLUMNS]

    output_path = RAW_DIR / "nyc_311_raw.parquet"
    raw.to_parquet(output_path, index=False)

    metadata = {
        "dataset_id": DATASET_ID,
        "dataset_name": "311 Service Requests from 2020 to Present",
        "source_url": DATASET_PAGE,
        "api_url": API_URL,
        "public_data_owner": "NYC Open Data",
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_limit": limit,
        "records_ingested": int(len(raw)),
        "storage_file": str(output_path.relative_to(PROJECT_ROOT)),
        "note": "Public NYC Open Data sample for local analytics portfolio use.",
    }
    (RAW_DIR / "source_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved raw sample to {output_path}")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest NYC 311 Service Requests from NYC Open Data.")
    parser.add_argument("--limit", type=int, default=100_000, help="Number of recent records to ingest.")
    parser.add_argument("--chunk-size", type=int, default=50_000, help="Socrata API page size.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ingest(limit=args.limit, chunk_size=args.chunk_size)
