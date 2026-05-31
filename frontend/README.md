# Scout Frontend

Next.js 16 + React 19 application for the Scout founder discovery agent. Renders a search form, streams real-time progress from the backend via SSE, and displays ranked founder cards with copyable outreach messages.

## Requirements

- Node.js 18+
- npm
- Scout backend running at http://localhost:8000

## Setup

```bash
cd frontend
npm install
npm run dev                         # http://localhost:3000
```

Environment variables in `frontend/.env.local`:

| Variable | Default | Description |
|---|---|---|
| NEXT_PUBLIC_API_URL | http://localhost:8000 | Backend base URL for API calls |

## Component Structure

```
app/
  page.tsx          State machine router — switches between the 4 phases
  layout.tsx        Root layout: Geist fonts, dark background, metadata
  globals.css       Design tokens (OKLCH palette, spacing, radius) + TailwindCSS v4

components/
  SearchForm.tsx    4-field form: industry/country/stage/role_interest dropdowns + submit
  ProgressFeed.tsx  3-step animated tracker (companies → founders → ai)
  ResultsGrid.tsx   Renders FounderCards, segments top (>=6) vs low (<6) results
  FounderCard.tsx   Score badge, fit explanation, outreach message, LinkedIn deep link
  CopyButton.tsx    Clipboard copy with 2-second "Copied!" feedback
  ErrorBanner.tsx   Error code → human-readable hint + retry button

hooks/
  useFounderSearch.ts  SSE consumer, state machine, abort handling

lib/
  types.ts          TypeScript interfaces mirroring backend models
  constants.ts      INDUSTRIES, COUNTRIES, STAGES dropdown options
```

## State Machine

`useFounderSearch` drives a 4-phase state machine:

```
idle  ──(submit)──▶  companies/founders/ai  ──(results event)──▶  done
                              │
                              └──(error event / network failure)──▶  error
```

`page.tsx` switches the UI based on `state.phase`:

- **`idle`** — SearchForm inside a surface card with hero heading ("Scout: Founder Discovery Agent")
- **`companies | founders | ai`** — ProgressFeed with animated 3-step tracker showing real-time progress
- **`done`** — ResultsGrid with ranked FounderCards + "New Search" button; results split by score threshold
- **`error`** — ErrorBanner with code-specific hint + "Try Again" button

## Key Design Decisions

**SSE over WebSockets**: One-way streaming is sufficient (no client→server messages during search). SSE is simpler, native to browsers, and requires no special server setup.

**Results segmentation**: `ResultsGrid` splits results at score >= 6. Founders with high fit_score render immediately; scores < 6 are collapsed in a `<details>` element labeled "Low Relevance — N founders". This keeps the primary view focused on the best matches.

**Abort on re-submit**: `useFounderSearch` holds an `AbortController` ref. Submitting a new search while one is in progress cancels the previous SSE stream before starting the new one.

**LinkedIn deep linking**: Each FounderCard renders an `ExternalLink` icon next to the founder name that opens their LinkedIn profile in a new tab.

**Design system**: Dark theme with teal accent. Tokens are OKLCH-based CSS custom properties defined in `globals.css`. TailwindCSS v4 is used purely for utilities — no configuration file; all tokens live in CSS variables.

## Important: Next.js 16

This project uses Next.js 16, which has breaking changes from prior versions. Read `frontend/AGENTS.md` before writing any frontend code. API routes, file conventions, and some component APIs differ from what training data may suggest.

## Running the App

With both backend and frontend running:

```bash
# Terminal 1 — backend
cd backend && uv run uvicorn main:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

Navigate to http://localhost:3000 to see the search form. Enter search criteria and click "Find Founders" to start a live search.
