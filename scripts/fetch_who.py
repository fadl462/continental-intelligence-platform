"""WHO Global Health Observatory (GHO) OData API client. No API key required."""
from __future__ import annotations
import time
import requests

WHO_BASE = "https://ghoapi.azureedge.net/api"


def fetch_latest(iso3: str, code: str, retries: int = 2) -> dict | None:
    url = f"{WHO_BASE}/{code}"
    params = {"$filter": f"SpatialDim eq '{iso3}'"}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            body = resp.json()
            rows = [r for r in body.get("value", []) if r.get("NumericValue") is not None]
            if not rows:
                return None
            rows.sort(key=lambda r: r["TimeDim"], reverse=True)
            latest = rows[0]
            return {"year": int(latest["TimeDim"]), "value": latest["NumericValue"]}
        except (requests.RequestException, ValueError, KeyError) as exc:
            if attempt == retries:
                print(f"[who] FAILED {iso3}/{code}: {exc}")
                return None
            time.sleep(1.5 * (attempt + 1))
    return None
