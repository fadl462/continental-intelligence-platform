# Continental Intelligence Platform — Backend (Phase 2)

Turns the static `continental_intelligence_platform.html` MVP into a real
service: Supabase stores ingested World Bank + WHO data, a scheduled job
refreshes it weekly, and a FastAPI layer serves the data plus AI-generated
executive briefings. Same architecture as `jmk-tender-monitor-ai`
(FastAPI + Supabase + Render + GitHub Actions + cron-job.org).

## 1. Supabase setup

1. Create a new Supabase project (or reuse an existing one on a separate schema).
2. Run `supabase/schema.sql` in the SQL editor. This creates:
   - `countries`, `indicators` — reference tables
   - `indicator_values` — the raw time series (World Bank + WHO)
   - `briefings` — cached AI-generated executive summaries
   - `latest_indicator_values` — a view of the most recent value per
     country/indicator, which is what the API and dashboard actually query
3. Grab your project URL and **service role key** (not anon — ingestion writes data).

## 2. Environment variables

| Variable | Used by | Notes |
|---|---|---|
| `SUPABASE_URL` | ingestion, API | Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ingestion, API | Service role, keep secret |
| `ANTHROPIC_API_KEY` | API (`/internal/briefing`) | For AI briefing generation |
| `ANTHROPIC_MODEL` | API | Defaults to `claude-sonnet-5` |
| `CRON_SECRET` | API | Same pattern as JMK Tender Monitor — protects `/internal/*` routes |
| `API_BASE_URL` | GitHub Actions | Your deployed Render URL, used to call `/internal/briefing/*` after ingestion |

## 3. Local run

```bash
pip install -r requirements.txt
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
python -m ingestion.run_ingestion      # one-off data pull
uvicorn main:app --reload              # API on http://localhost:8000
```

## 4. Deploy (Render — same as your other services)

1. New Web Service → connect this repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the environment variables from the table above.
5. Once deployed, do one manual ingest to seed data:
   ```
   curl -X POST https://<your-render-url>/internal/ingest \
     -H "x-cron-secret: <CRON_SECRET>"
   ```

## 5. Scheduling

Two options, pick one (or both, redundantly, like you do with JMK):

- **GitHub Actions** (`.github/workflows/ingest.yml`): runs weekly, calls
  `run_ingestion.py` directly in the Actions runner, then hits
  `/internal/briefing/{iso3}` for a shortlist of countries. Needs
  `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `CRON_SECRET`, `API_BASE_URL`
  as GitHub repo secrets.
- **cron-job.org**: point it at `POST /internal/ingest` on your Render URL
  with header `x-cron-secret: <CRON_SECRET>` — same pattern as the JMK
  Tender Monitor scan job.

## 6. Wiring the frontend to this instead of client-side fetches

The current `continental_intelligence_platform.html` calls World Bank/WHO
directly from the browser (no backend needed, but no caching, no AI
briefings, no rate-limit protection). To point it at this API instead:

- Replace `wbFetch`/`whoRows` calls with `fetch('https://<render-url>/indicators/' + iso3)`
- Add a briefing panel that calls `GET /briefing/{iso3}` and renders `summary`
- Everything else (charts, KPI cards, ranking bars) stays the same shape —
  just swap the data source functions.

Say the word if you want that wiring done as a follow-up; it's a fairly
mechanical swap once this backend is deployed and seeded.
