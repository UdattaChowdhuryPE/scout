# Scout - Founder Discovery Agent

A full-stack web application that helps engineers discover startup founders to reach out to for job opportunities.

## Overview

Scout uses:
- **Backend**: FastAPI (Python) + Crustdata API + Claude AI
- **Frontend**: Next.js 16 (React) + Tailwind CSS
- **Streaming**: Server-Sent Events (SSE) for real-time progress updates

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

## Usage

1. Open http://localhost:3000 in your browser
2. Fill in your preferences:
   - **Industry**: e.g., AI, FinTech, HealthTech
   - **Country**: Where you want to find founders
   - **Company Stage**: Pre-seed, Seed, Series A, Series B
   - **Role Interest**: e.g., AI Engineer, Full-stack Engineer
3. Click "Find Founders"
4. Watch the real-time progress as the app:
   - Searches for matching companies
   - Fetches founder information
   - Analyzes fit with Claude
5. Copy personalized outreach messages for each founder

### Usage Tips

- **Be specific with role interest** — "AI Engineer" returns better matches than "Engineer"
- **Narrow by geography** — Searching within a specific country is faster
- **Series A/B works better** — Pre-seed companies have less data in Crustdata; Series A/B returns more results
- **Search multiple times** — Try different criteria to build a larger list

## Architecture

### Backend Flow

```
POST /api/search → Crustdata Companies → Crustdata Founders → Claude Analysis → SSE Results
```

SSE Events:
- `progress` — updates on finding companies, fetching founders, AI analysis
- `results` — final ranked list of founders
- `error` — if something goes wrong

### Frontend State Machine

```
idle → companies → founders → ai → done (or error)
```

### TypeScript Types

All shared types are in `frontend/lib/types.ts` and mirrored from `backend/models.py`.

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

## Future Improvements

- Store results in a local database
- Add filtering/sorting in the frontend
- Support LinkedIn direct messaging integration
- Email templates for outreach
- User authentication and saved searches
- More detailed company metrics (growth, hiring status)
