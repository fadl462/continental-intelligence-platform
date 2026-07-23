"""
WHO Global Health Observatory (GHO) OData API client.
No API key required. Docs: https://www.who.int/data/gho/info/gho-odata-api
"""
from __future__ import annotations
import time
import requests

WHO_BASE = "https://ghoapi.azureedge.net/api"


def _rows(iso3: str, code: str, retries: int = 2) -> list[dict]:
    url = f"{WHO_BASE}/{code}"
    params = {"$filter": f"SpatialDim eq '{iso3}'"}

    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            body = resp.json()
            return [r for r in body.get("value", []) if r.get("NumericValue") is not None]
        except (requests.RequestException, ValueError) as exc:
            if attempt == retries:
                print(f"[who] FAILED {iso3}/{code}: {exc}")
                return []
            time.sleep(1.5 * (attempt + 1))
    return []


def fetch_series(iso3: str, code: str, from_year: int, to_year: int) -> list[dict]:
    """Return [{'year': int, 'value': float}, ...], deduped by year (first match wins
    when WHO returns sex/age-disaggregated rows for the same year)."""
    rows = _rows(iso3, code)
    by_year: dict[int, float] = {}
    for r in rows:
        year = int(r["TimeDim"])
        if from_year <= year <= to_year and year not in by_year:
            by_year[year] = r["NumericValue"]
    return [{"year": y, "value": v} for y, v in sorted(by_year.items())]


def fetch_latest(iso3: str, code: str) -> dict | None:
    rows = _rows(iso3, code)
    if not rows:
        return None
    rows.sort(key=lambda r: r["TimeDim"], reverse=True)
    latest = rows[0]
    return {"year": int(latest["TimeDim"]), "value": latest["NumericValue"]}
