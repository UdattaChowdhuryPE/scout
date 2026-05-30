# Scout

An autonomous founder discovery engine for engineers hunting startup opportunities. Given a set of search criteria (industry, country, company stage, desired role), Scout queries the CrustData API to find matching companies, fetches their founders, ranks them with Claude AI for cultural and technical fit, and streams personalized outreach messages in real-time. Built with FastAPI, Claude Haiku, and Next.js.

## Features

- **AI-ranked founders**: Claude analyzes each founder's background and company trajectory; ranks them by fit to your profile in a single batch call
- **Personalized outreach**: Generates tailored recruitment messages for each founder based on their expertise and the company's stage
- **Real-time streaming**: SSE pipeline streams progress (company search → founder fetch → AI analysis) live to the frontend; no polling
- **Parallel data fetching**: Fetches founder data for all companies concurrently with semaphore-gated rate limiting
- **Cost-efficient ranking**: Uses Claude Haiku (~10x cheaper than Sonnet) for batch scoring; single API call enables cross-founder comparison
- **Stateless design**: No database — all processing is ephemeral, simplifying deployment and enabling one-off searches

## Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- UV package manager
- Crustdata API key ([sign up](https://crustdata.com))
- Anthropic API key ([get here](https://console.anthropic.com))

## Setup

### 1. Configure API Keys

Add your API keys to both `.env` files:

```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your actual API keys

# Frontend
cd ../frontend
cp .env.local.example .env.local
# Verify NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Start the Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

Backend will start at `http://localhost:8000`

### 3. Start the Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will start at `http://localhost:3000`

## Architecture

### Backend

FastAPI application that orchestrates the founder discovery pipeline. Receives search parameters via POST `/api/search`, fetches companies and founders in parallel from CrustData, sends them to Claude for ranking, and streams results back as SSE events. Request flow: POST → fetch companies → fetch founders for each company (concurrent, semaphore-gated) → batch rank with Claude → stream results. Each stage emits `progress` events so the frontend can display real-time status updates.

**Key files**:
- **`backend/main.py`** — FastAPI app, `/health` and `/api/search` endpoints, SSE event streaming
- **`backend/crustdata.py`** — CrustData API client, company screening and founder person search
- **`backend/claude_client.py`** — Claude integration for ranking founders, system prompt defines recruiter persona
- **`backend/models.py`** — TypeScript-like models: SearchRequest, Company, Founder, FounderResult
- **`backend/sse_helpers.py`** — SSE frame formatting utility

### Frontend

Next.js 16 application with a search form and live results UI. Consumes the backend SSE stream via `useFounderSearch` hook and maintains a state machine (idle → companies → founders → ai → done/error). Displays search form in idle state, progress feed during investigation, and a grid of ranked founder cards once complete. Each card shows fit score, explanation, and a copyable outreach message.

**Key files**:
- **`frontend/app/page.tsx`** — main page component, routes between form/results/error states
- **`frontend/hooks/useFounderSearch.ts`** — SSE consumer hook, state machine, abort handling
- **`frontend/app/layout.tsx`** — root layout with Geist fonts and metadata
- **`frontend/app/globals.css`** — design tokens (OKLCH palette, typography, spacing) and TailwindCSS v4
- **`frontend/lib/types.ts`** — TypeScript definitions mirrored from backend models
- **`frontend/lib/constants.ts`** — dropdown options (industries, countries, stages)
- **`frontend/components/`** — SearchForm, FounderCard, ResultsGrid, ProgressFeed, ErrorBanner, CopyButton

## How It Works

1. **User submits**: Opens http://localhost:3000, fills in industry/country/stage/role interest, clicks "Find Founders"
2. **Session starts**: Frontend POSTs to `/api/search` with search parameters; backend creates a generator
3. **Company search**: Backend calls CrustData API to find matching companies by industry/country/stage; emits `progress` event
4. **Founder fetching**: Backend calls CrustData person search for each company in parallel (max 5 concurrent); filters by founder-title keywords; emits `progress` updates
5. **Claude ranking**: Backend sends all founders as a batch to Claude Haiku with system prompt defining the recruiter role; Claude returns a ranked JSON array; emits `results` event
6. **Real-time updates**: Frontend consumes SSE stream, updates progress UI on each event, renders founder cards with scores/explanations/outreach messages once `results` event arrives
7. **Copy and act**: User can copy personalized outreach message to clipboard for each ranked founder

## Key Design Decisions

1. **Single Claude Call**: All founders analyzed in one batch → lower latency, cost-efficient, enables cross-founder ranking
   - **Why**: Batch processing is ~50% cheaper per founder than serial calls; holistic analysis produces better fit rankings
   
2. **SSE Streaming**: Real-time progress updates without polling
   - **Why**: One-way streaming (no client→server messages needed), simpler than WebSockets, minimal overhead
   
3. **Claude Haiku**: Uses `claude-haiku-4-5-20251001` for analysis
   - **Why**: 10x cheaper than Sonnet; quality is sufficient for founder scoring
   
4. **Async Crustdata**: Parallel founder fetches with semaphore (5 concurrent)
   - **Why**: Reduces latency; semaphore prevents rate limit hits
   
5. **No Database**: All processing is stateless
   - **Why**: Simplifies deployment; no persistence requirements for one-shot searches
   
6. **No Auth**: Local development focus
   - **Why**: Faster iteration; can add auth later if needed for multi-user deployment

## API Reference

### Health Check

```bash
GET /health
```

Returns:
```json
{"status": "ok"}
```

### Search Endpoint

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

Response: Server-Sent Events stream with `progress`, `results`, and `error` events.

Test with curl:
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"industry":"AI","country":"India","stage":"Series A","role_interest":"AI Engineer"}'
```

## Error Codes

| Code | Root Cause | What to Do |
|------|-----------|-----------|
| `no_companies` | Crustdata found no matching companies | Broaden search criteria (try different industry/country/stage) |
| `no_founders` | No founders found for matching companies | Some companies lack founder data; try Series A/B instead of Pre-seed |
| `crustdata_error` | API request to Crustdata failed | Check API key validity and rate limits |
| `ai_error` | Claude analysis failed | Check Anthropic API key and quota |
| `missing_keys` | Backend environment variables not set | Verify `.env` has `CRUSTDATA_API_KEY` and `ANTHROPIC_API_KEY` |
| `network_error` | Frontend cannot reach backend | Confirm backend is running on http://localhost:8000 |

## Performance

- Frontend to backend latency: ~200-300ms
- Company search: ~2-3 seconds
- Founder fetching: ~3-5 seconds (15-20 parallel requests)
- Claude analysis: ~3-5 seconds
- **Total time: ~8-15 seconds** for a full search

## Usage Tips

- **Be specific with role interest** — "AI Engineer" returns better matches than "Engineer"
- **Narrow by geography** — Searching within a specific country is faster
- **Series A/B works better** — Pre-seed companies have less data in Crustdata; Series A/B returns more results
- **Search multiple times** — Try different criteria to build a larger list

## Troubleshooting

### "Connection refused" / "Cannot reach backend"
- Make sure `uvicorn main:app --reload` is running on http://localhost:8000
- Check that frontend `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`

### "Port already in use"
Kill the process using the port:
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### "API keys not configured"
- Verify `.env` files in both backend and frontend have actual API keys
- Double-check keys are valid

### "No companies found" / "No founders found"
- Try a broader search (different industry/country/stage)
- Some countries/industries have limited Crustdata coverage
- Check that your Crustdata account has sufficient API quota

### JSON parsing errors from Claude
- May indicate Claude returned malformed JSON
- Check backend logs for the raw Claude response
- Try again — it's often transient
