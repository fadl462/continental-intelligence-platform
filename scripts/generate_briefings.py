"""
Generates data/briefings.json — a static file the dashboard fetches directly
from GitHub Pages. This is the entire "backend": no server, no database.
GitHub Actions runs this on a schedule and commits the result back to the repo.

Env vars:
  ANTHROPIC_API_KEY   required
  ANTHROPIC_MODEL     optional, defaults to claude-sonnet-5
  BRIEFING_COUNTRIES  optional, comma-separated ISO3 list to limit scope
                      (defaults to all countries in config.COUNTRIES —
                      36 countries x 1 short call each, well within a
                      single Actions run)
"""
from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent))
from config import COUNTRIES, BRIEFING_INDICATORS  # noqa: E402
import fetch_worldbank  # noqa: E402
import fetch_who  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "data" / "briefings.json"
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def collect_indicators(iso3: str) -> dict:
    """Fetch latest value for every briefing indicator for one country."""
    out = {}
    for ind_id, (source, code, label, unit) in BRIEFING_INDICATORS.items():
        fetcher = fetch_worldbank if source == "worldbank" else fetch_who
        result = fetcher.fetch_latest(iso3, code)
        if result:
            out[ind_id] = {"label": label, "unit": unit, "value": result["value"], "year": result["year"]}
        time.sleep(0.1)  # be polite to both free public APIs
    return out


def build_prompt(country_name: str, data: dict) -> str:
    lines = [f"- {v['label']}: {v['value']} {v['unit']} (year {v['year']})" for v in data.values()]
    return (
        f"You are writing a one-paragraph executive intelligence briefing on {country_name} "
        f"for a strategy/decision-making audience. Use only the data below — do not invent "
        f"figures or cite anything not listed. Flag 1-2 notable risks or opportunities only if "
        f"the data genuinely supports it. Keep it under 130 words, plain prose, no headers, "
        f"no bullet points, no markdown.\n\nData:\n" + "\n".join(lines)
    )


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    scope = os.environ.get("BRIEFING_COUNTRIES")
    targets = [c.strip().upper() for c in scope.split(",")] if scope else list(COUNTRIES)

    client = anthropic.Anthropic(api_key=api_key)
    briefings = {}

    # Preserve any existing briefings for countries not in this run's scope
    if OUTPUT_PATH.exists():
        try:
            briefings = json.loads(OUTPUT_PATH.read_text())
        except json.JSONDecodeError:
            briefings = {}

    for iso3 in targets:
        if iso3 not in COUNTRIES:
            print(f"[skip] unknown country {iso3}")
            continue
        country_name = COUNTRIES[iso3][0]
        print(f"[briefing] {country_name} ({iso3})...")

        data = collect_indicators(iso3)
        if not data:
            print(f"[briefing] no data available for {iso3}, skipping")
            continue

        prompt = build_prompt(country_name, data)
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=350,
                messages=[{"role": "user", "content": prompt}],
            )
            summary = "".join(block.text for block in message.content if block.type == "text").strip()
        except Exception as exc:  # noqa: BLE001 — log and continue, one bad country shouldn't kill the run
            print(f"[briefing] Anthropic call failed for {iso3}: {exc}")
            continue

        briefings[iso3] = {
            "country": country_name,
            "summary": summary,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "data_used": data,
        }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(briefings, indent=2, ensure_ascii=False))
    print(f"[briefing] wrote {len(briefings)} briefings to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
