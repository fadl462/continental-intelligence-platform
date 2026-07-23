"""
World Bank Indicators API client.
No API key required. Docs: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589
"""
from __future__ import annotations
import time
import requests

WB_BASE = "https://api.worldbank.org/v2"


def fetch_series(iso3: str, code: str, from_year: int, to_year: int, retries: int = 2) -> list[dict]:
    """Return [{'year': int, 'value': float}, ...] for one country/indicator, oldest first."""
    url = f"{WB_BASE}/country/{iso3}/indicator/{code}"
    params = {"format": "json", "date": f"{from_year}:{to_year}", "per_page": 1000}

    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            body = resp.json()
            if not isinstance(body, list) or len(body) < 2 or body[1] is None:
                return []
            rows = body[1]
            out = [
                {"year": int(r["date"]), "value": r["value"]}
                for r in rows
                if r.get("value") is not None
            ]
            return sorted(out, key=lambda r: r["year"])
        except (requests.RequestException, ValueError) as exc:
            if attempt == retries:
                print(f"[worldbank] FAILED {iso3}/{code}: {exc}")
                return []
            time.sleep(1.5 * (attempt + 1))
    return []


def fetch_latest(iso3: str, code: str) -> dict | None:
    """Single most-recent-non-empty-value point, using the API's mrnev filter."""
    url = f"{WB_BASE}/country/{iso3}/indicator/{code}"
    try:
        resp = requests.get(url, params={"format": "json", "mrnev": 1}, timeout=20)
        resp.raise_for_status()
        body = resp.json()
        if not isinstance(body, list) or len(body) < 2 or not body[1]:
            return None
        row = body[1][0]
        return {"year": int(row["date"]), "value": row["value"]}
    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"[worldbank] latest FAILED {iso3}/{code}: {exc}")
        return None
