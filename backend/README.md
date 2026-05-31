# Scout Backend

FastAPI service that drives the founder discovery pipeline. Receives search parameters, queries CrustData for companies and founders in parallel, sends them to Claude Haiku for batch ranking and outreach generation, and streams results back as Server-Sent Events.

## Requirements

- Python 3.12+
- UV package manager (`pip install uv`)
- CrustData API key — https://crustdata.com
- Anthropic API key — https://console.anthropic.com

## Setup

```bash
cd backend
cp .env.example .env          # then fill in your keys
uv sync                        # install dependencies
uv run uvicorn main:app --reload   # starts at http://localhost:8000
```

Required environment variables in `backend/.env`:

| Variable | Required | Description |
|---|---|---|
| CRUSTDATA_API_KEY | Yes | CrustData API key for company/founder data |
| ANTHROPIC_API_KEY | Yes | Anthropic API key for Claude Haiku |
| LANGFUSE_PUBLIC_KEY | No | Enables Langfuse LLM observability tracing |
| LANGFUSE_SECRET_KEY | No | Required if LANGFUSE_PUBLIC_KEY is set |
| LANGFUSE_HOST | No | Defaults to https://cloud.langfuse.com |

## Architecture

```
POST /api/search
  │
  ├─ fetch_companies()          # CrustData: filter by industry/country/stage
  │
  ├─ fetch_all_founders()       # CrustData: parallel per company, semaphore=5
  │
  ├─ rank_with_claude()         # Single batch call to Claude Haiku (max 25 founders)
  │     └─ returns JSON array sorted by fit_score descending
  │
  └─ StreamingResponse          # SSE: progress events + final results event
```

Each stage emits `progress` SSE events so the frontend can display real-time status.

## Key Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app, `/health` and `/api/search` endpoints, RequestID middleware |
| `claude_client.py` | Batch ranking via Claude Haiku; builds system/user prompts; Langfuse tracing |
| `crustdata.py` | CrustData API client — company screening and concurrent founder fetching |
| `models.py` | TypedDicts: Company, Founder, FounderResult; Pydantic SearchRequest |
| `observability.py` | Optional Langfuse client — only initializes if LANGFUSE_PUBLIC_KEY is set |
| `sse_helpers.py` | `format_sse(dict) → str` — formats dicts as SSE frames |

## API

### Health check

```bash
GET /health
→ {"status": "ok"}
```

### Search (SSE stream)

```bash
POST /api/search
Content-Type: application/json

{
  "industry": "AI",
  "country": "India",
  "stage": "Series A",
  "role_interest": "AI Engineer"
}
```

Response is a `text/event-stream` of JSON objects:

```
data: {"type":"progress","step":"companies","message":"Searching for companies..."}

data: {"type":"progress","step":"founders","message":"Found 12 companies. Fetching founders..."}

data: {"type":"progress","step":"ai","message":"Claude is ranking..."}

data: {"type":"results","founders":[...FounderResult array...],"skipped_companies":3}
```

Or on failure:

```
data: {"type":"error","code":"no_companies","message":"No companies found matching your criteria."}
```

Error codes: `no_companies`, `no_founders`, `crustdata_error`, `ai_error`, `missing_keys`, `network_error`, `analysis_error`, `unknown_error`

### Test with curl

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "AI",
    "country": "India",
    "stage": "Series A",
    "role_interest": "AI Engineer"
  }'
```

## Structured Logging

Every request gets an 8-character UUID via `RequestIDMiddleware`. Log format:

```
2025-01-15 10:23:41 INFO     main Searching for companies... [req=a1b2c3d4]
```

The `[req=...]` suffix traces all log lines for a single search request. Use this to correlate logs across the pipeline.

## LLM Evals

The `evals/` directory contains pytest-based LLM evaluation tests that make real Claude API calls. They are marked `@pytest.mark.llm` to separate them from unit tests.

```bash
cd backend
# Run all evals (costs ~$0.01 in Claude API credits)
uv run pytest evals/ -m llm -v
```

### What each test covers

- **test_schema_validity** — Claude returns valid FounderResult fields (fit_score, fit_explanation, outreach_message)
- **test_score_ordering** — Strong-fit founder scores higher than weak-fit founder
- **test_score_ranges** — Strong fit >= 7, weak fit <= 5
- **test_outreach_template_adherence** — No unfilled placeholders, company name present in message
- **test_results_sorted_by_score** — Results in descending fit_score order
- **test_founder_company_consistency** — full_name/company_name match input

Fixtures in `evals/fixtures.py` define a strong-fit (LLMCore, seed AI infra startup) and a weak-fit (StyleHub, Series D fashion retail) founder pair.

## Design Decisions

**Single batch Claude call**: All founders (capped at 25) are analyzed in one API call. This enables cross-founder comparison (holistic ranking), costs ~50% less per founder than serial calls, and reduces latency. The system prompt encodes a specific candidate persona (engineer moving into AI engineering).

**Semaphore-gated parallelism**: CrustData founder fetches run concurrently with a semaphore of 5 to avoid rate-limit errors on larger searches.

**Stateless**: No database. Each search is ephemeral. Simplifies deployment and supports one-off usage patterns.

**SSE streaming**: Allows the frontend to display real-time progress without polling. Frontend sees "Finding companies… Fetching founders… AI analysis…" as each stage completes.

**Optional Langfuse tracing**: When `LANGFUSE_PUBLIC_KEY` is set, all searches are traced with generation metrics (model, tokens, latency). If the env var is absent, observability silently no-ops — no code changes needed.
