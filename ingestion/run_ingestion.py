"""
Scheduled ingestion job — the same role as fetch_bounces.py / the scan job in
jmk-tender-monitor-ai, just for a different data source.

Run manually:   python -m ingestion.run_ingestion
Run on schedule: see .github/workflows/ingest.yml (GitHub Actions, weekly)
                 or trigger it from cron-job.org against a protected endpoint
                 on the FastAPI service (see main.py's /internal/ingest route).

Required env vars:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY   (service role, not anon — this writes data)
"""
from __future__ import annotations
import os
import sys
import time

from supabase import create_client

from ingestion import fetch_worldbank, fetch_who
from ingestion.config import INDICATORS, COUNTRIES, SERIES_FROM_YEAR, SERIES_TO_YEAR


def get_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
        sys.exit(1)
    return create_client(url, key)


def upsert_reference_data(sb):
    sb.table("countries").upsert(
        [{"iso3": iso3, "name": name, "region": continent, "continent": continent}
         for iso3, (name, continent) in COUNTRIES.items()]
    ).execute()

    sb.table("indicators").upsert(
        [{"id": ind_id, "source": src, "source_code": code, "label": label,
          "unit": unit, "module": module}
         for ind_id, (src, code, label, unit, module) in INDICATORS.items()]
    ).execute()


def ingest_all(sb):
    total_written = 0
    for ind_id, (source, code, label, unit, module) in INDICATORS.items():
        fetcher = fetch_worldbank if source == "worldbank" else fetch_who
        for iso3 in COUNTRIES:
            series = fetcher.fetch_series(iso3, code, SERIES_FROM_YEAR, SERIES_TO_YEAR)
            if not series:
                continue
            rows = [
                {"iso3": iso3, "indicator_id": ind_id, "year": p["year"], "value": p["value"]}
                for p in series
            ]
            sb.table("indicator_values").upsert(
                rows, on_conflict="iso3,indicator_id,year"
            ).execute()
            total_written += len(rows)
            # Be polite to both free public APIs
            time.sleep(0.15)
        print(f"[ingest] {ind_id} ({source}/{code}) done")
    print(f"[ingest] wrote/updated {total_written} rows total")


def main():
    sb = get_client()
    print("[ingest] upserting reference data (countries, indicators)...")
    upsert_reference_data(sb)
    print("[ingest] pulling series from World Bank + WHO...")
    ingest_all(sb)
    print("[ingest] done.")


if __name__ == "__main__":
    main()
