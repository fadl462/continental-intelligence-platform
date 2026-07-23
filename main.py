"""
Continental Intelligence Platform — API backend.
Same shape as jmk-tender-monitor-ai: FastAPI + Supabase + Render.

Endpoints:
  GET  /health
  GET  /countries
  GET  /indicators/{iso3}                 -> latest value per indicator
  GET  /indicators/{iso3}/{indicator_id}/series?from=2005&to=2025
  GET  /briefing/{iso3}                   -> latest cached AI briefing
  POST /internal/ingest                   -> triggers run_ingestion (protected by CRON_SECRET)
  POST /internal/briefing/{iso3}          -> (re)generates one country's AI briefing
"""
from __future__ import annotations
import os
import subprocess
import sys

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import anthropic

from ingestion.config import INDICATORS, COUNTRIES

app = FastAPI(title="Continental Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your dashboard's domain in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

CRON_SECRET = os.environ.get("CRON_SECRET", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def sb():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(500, "Supabase not configured")
    return create_client(url, key)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/countries")
def countries():
    return [
        {"iso3": iso3, "name": name, "continent": continent}
        for iso3, (name, continent) in COUNTRIES.items()
    ]


@app.get("/indicators/{iso3}")
def latest_indicators(iso3: str):
    iso3 = iso3.upper()
    if iso3 not in COUNTRIES:
        raise HTTPException(404, f"Unknown country {iso3}")
    client = sb()
    res = client.table("latest_indicator_values").select("*").eq("iso3", iso3).execute()
    return res.data


@app.get("/indicators/{iso3}/{indicator_id}/series")
def indicator_series(iso3: str, indicator_id: str, from_: int = 2005, to: int = 2025):
    iso3 = iso3.upper()
    if indicator_id not in INDICATORS:
        raise HTTPException(404, f"Unknown indicator {indicator_id}")
    client = sb()
    res = (
        client.table("indicator_values")
        .select("year,value")
        .eq("iso3", iso3)
        .eq("indicator_id", indicator_id)
        .gte("year", from_)
        .lte("year", to)
        .order("year")
        .execute()
    )
    return res.data


@app.get("/briefing/{iso3}")
def get_briefing(iso3: str):
    iso3 = iso3.upper()
    client = sb()
    res = (
        client.table("briefings")
        .select("*")
        .eq("iso3", iso3)
        .order("generated_at", desc=True)
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(404, "No briefing generated yet for this country")
    return res.data[0]


def _require_cron_secret(x_cron_secret: str | None):
    if not CRON_SECRET or x_cron_secret != CRON_SECRET:
        raise HTTPException(401, "Invalid or missing cron secret")


@app.post("/internal/ingest")
def trigger_ingest(x_cron_secret: str | None = Header(default=None)):
    """Lets cron-job.org (or GitHub Actions) trigger ingestion via HTTP instead
    of needing shell access to the Render instance."""
    _require_cron_secret(x_cron_secret)
    result = subprocess.run(
        [sys.executable, "-m", "ingestion.run_ingestion"],
        capture_output=True, text=True, timeout=1800,
    )
    if result.returncode != 0:
        raise HTTPException(500, f"Ingestion failed: {result.stderr[-2000:]}")
    return {"status": "ok", "log": result.stdout[-2000:]}


@app.post("/internal/briefing/{iso3}")
def generate_briefing(iso3: str, x_cron_secret: str | None = Header(default=None)):
    _require_cron_secret(x_cron_secret)
    iso3 = iso3.upper()
    if iso3 not in COUNTRIES:
        raise HTTPException(404, f"Unknown country {iso3}")

    client = sb()
    rows = client.table("latest_indicator_values").select("*").eq("iso3", iso3).execute().data
    if not rows:
        raise HTTPException(404, "No ingested data for this country yet — run /internal/ingest first")

    id_to_label = {k: v[2] for k, v in INDICATORS.items()}
    data_lines = "\n".join(
        f"- {id_to_label.get(r['indicator_id'], r['indicator_id'])}: {r['value']} (year {r['year']})"
        for r in rows
    )
    country_name = COUNTRIES[iso3][0]

    anthropic_client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    prompt = (
        f"You are writing a one-paragraph executive intelligence briefing on {country_name} "
        f"for a strategy/decision-making audience. Use only the data below — do not invent figures. "
        f"Flag 1-2 notable risks or opportunities if the data supports it. Keep it under 150 words, "
        f"plain prose, no headers or bullet points.\n\nData:\n{data_lines}"
    )
    message = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    summary = "".join(block.text for block in message.content if block.type == "text")

    client.table("briefings").insert({
        "iso3": iso3,
        "summary": summary,
        "risk_flags": None,
        "model": ANTHROPIC_MODEL,
    }).execute()

    return {"iso3": iso3, "summary": summary}
