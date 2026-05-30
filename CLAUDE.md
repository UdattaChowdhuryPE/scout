# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Scout** — Founder discovery agent. Backend searches startups via CrustData API, Claude ranks founders & generates personalized outreach messages, frontend displays results.

## Setup

```bash
# Backend (Python 3.12, FastAPI)
cd backend && uv sync && python main.py  # http://localhost:8000

# Frontend (Next.js 16, React 19, TailwindCSS 4)
cd frontend && npm install && npm run dev  # http://localhost:3000

# Required env vars (backend/.env)
CRUSTDATA_API_KEY=...
ANTHROPIC_API_KEY=...
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, `/api/search` endpoint, SSE streaming |
| `backend/claude_client.py` | Claude ranking/outreach (uses Haiku, system prompt defines recruiter role) |
| `backend/crustdata.py` | CrustData API client (company/founder fetching) |
| `backend/models.py` | TypedDicts: SearchRequest, Company, Founder, FounderResult |
| `frontend/app/page.tsx` | Main UI (currently default template, needs search form & results) |

## Architecture

User search → POST `/api/search` → fetch companies (CrustData) → fetch founders → rank with Claude → SSE stream results

## Design System

Scout has a dark, sharp, precise design system defined in [`PRODUCT.md`](PRODUCT.md) (strategic) and [`DESIGN.md`](DESIGN.md) (visual). Key principles: signal before structure, zero wasted steps, earned decoration, honest density. Dark theme with teal accent, OKLCH palette, Geist typefaces. Live iteration available via `/impeccable live`.

## Notes

- Claude uses `claude-haiku-4-5-20251001`, evaluates founders for engineer moving into AI engineering
- Frontend: Next.js 16 has breaking changes, check docs before coding (see `frontend/AGENTS.md`)
- CORS allows localhost:3000 & 3001
- No tests yet
