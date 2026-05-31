import os
import asyncio
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from models import SearchRequest, Company, Founder
from sse_helpers import format_sse
from crustdata import get_client, fetch_companies, fetch_all_founders
from claude_client import rank_with_claude

logger = logging.getLogger(__name__)

load_dotenv()

CRUSTDATA_API_KEY = os.getenv("CRUSTDATA_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI(title="Scout - Founder Discovery Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=True,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


async def stream_search(request: SearchRequest) -> AsyncGenerator[str, None]:
    """
    Main search logic that yields SSE events.
    """
    if not CRUSTDATA_API_KEY or not ANTHROPIC_API_KEY:
        yield format_sse(
            {
                "type": "error",
                "code": "missing_keys",
                "message": "API keys not configured. Please set CRUSTDATA_API_KEY and ANTHROPIC_API_KEY.",
            }
        )
        return

    try:
        # Fetch companies
        yield format_sse(
            {
                "type": "progress",
                "step": "companies",
                "message": "Searching for companies matching your criteria...",
            }
        )

        async with get_client(CRUSTDATA_API_KEY) as client:
            companies = await fetch_companies(
                client,
                request.industry,
                request.country,
                request.stage,
                limit=30,
            )

        logger.info(f"[PIPELINE] 1. companies_from_crustdata={len(companies)}")

        if not companies:
            yield format_sse(
                {
                    "type": "error",
                    "code": "no_companies",
                    "message": f"No companies found matching {request.industry} in {request.country} at {request.stage} stage.",
                }
            )
            return

        yield format_sse(
            {
                "type": "progress",
                "step": "companies",
                "message": f"Found {len(companies)} companies. Fetching founders...",
            }
        )

        # Fetch founders
        async with get_client(CRUSTDATA_API_KEY) as client:
            pairs, skipped = await fetch_all_founders(client, companies)

        total_founders = sum(len(founders) for _, founders in pairs)
        logger.info(f"[PIPELINE] 2. companies_with_founders={len(pairs)}, skipped={skipped}")
        logger.info(f"[PIPELINE] 3. founders_fetched={total_founders}")
        logger.info(f"[PIPELINE] 4. founders_sent_to_claude={total_founders}")

        if not pairs:
            yield format_sse(
                {
                    "type": "error",
                    "code": "no_founders",
                    "message": "No founders found in the companies. Try different search criteria.",
                }
            )
            return

        founder_count = sum(len(founders) for _, founders in pairs)
        yield format_sse(
            {
                "type": "progress",
                "step": "founders",
                "message": f"Found {founder_count} founders across {len(pairs)} companies. Analyzing with AI...",
            }
        )

        # Prepare data for Claude
        pairs_for_claude = [
            {"founder": founder, "company": company}
            for company, founders in pairs
            for founder in founders
        ]

        # Rank with Claude
        yield format_sse(
            {
                "type": "progress",
                "step": "ai",
                "message": "Claude is ranking and writing personalized outreach messages...",
            }
        )

        # Cap at 25 founders to keep Claude response manageable
        if len(pairs_for_claude) > 25:
            logger.info(f"[PIPELINE] Limiting to 25 of {len(pairs_for_claude)} founders for Claude")
            pairs_for_claude = pairs_for_claude[:25]

        results = await rank_with_claude(pairs_for_claude, request)

        logger.info(f"[PIPELINE] 5. founders_returned_by_claude={len(results)}")

        yield format_sse(
            {
                "type": "results",
                "founders": results,
                "skipped_companies": skipped,
            }
        )

    except ValueError as e:
        yield format_sse(
            {
                "type": "error",
                "code": "analysis_error",
                "message": str(e),
            }
        )
    except Exception as e:
        yield format_sse(
            {
                "type": "error",
                "code": "unknown_error",
                "message": f"An unexpected error occurred: {str(e)}",
            }
        )


@app.post("/api/search")
async def search(request: SearchRequest):
    return StreamingResponse(
        stream_search(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
