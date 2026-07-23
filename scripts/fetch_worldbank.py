"""World Bank Indicators API client. No API key required."""
from __future__ import annotations
import time
import requests

WB_BASE = "https://api.worldbank.org/v2"


def fetch_latest(iso3: str, code: str, retries: int = 2) -> dict | None:
    url = f"{WB_BASE}/country/{iso3}/indicator/{code}"
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params={"format": "json", "mrnev": 1}, timeout=20)
            resp.raise_for_status()
            body = resp.json()
            if not isinstance(body, list) or len(body) < 2 or not body[1]:
                return None
            row = body[1][0]
            return {"year": int(row["date"]), "value": row["value"]}
        except (requests.RequestException, ValueError, KeyError) as exc:
            if attempt == retries:
                print(f"[worldbank] FAILED {iso3}/{code}: {exc}")
                return None
            time.sleep(1.5 * (attempt + 1))
    return None
