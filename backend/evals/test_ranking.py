import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_client import rank_with_claude
from evals.fixtures import SEARCH_REQUEST, STRONG_FIT_COMPANY, STRONG_FIT_FOUNDER, WEAK_FIT_COMPANY, WEAK_FIT_FOUNDER
from models import FounderResult


@pytest.mark.llm
async def test_schema_validity():
    """Verify that Claude returns valid FounderResult objects with all required fields."""
    pairs = [
        {"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER},
        {"company": WEAK_FIT_COMPANY, "founder": WEAK_FIT_FOUNDER},
    ]
    results = await rank_with_claude(pairs, SEARCH_REQUEST)

    assert isinstance(results, list)
    assert len(results) == 2

    for result in results:
        assert isinstance(result, dict)
        assert "fit_score" in result
        assert "fit_explanation" in result
        assert "outreach_message" in result
        assert "full_name" in result
        assert "company_name" in result

        # Validate types and ranges
        assert isinstance(result["fit_score"], int)
        assert 1 <= result["fit_score"] <= 10
        assert isinstance(result["fit_explanation"], str)
        assert len(result["fit_explanation"]) > 0
        assert isinstance(result["outreach_message"], str)
        assert len(result["outreach_message"]) > 0


@pytest.mark.llm
async def test_score_ordering():
    """Verify that strong-fit founder scores higher than weak-fit founder."""
    pairs = [
        {"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER},
        {"company": WEAK_FIT_COMPANY, "founder": WEAK_FIT_FOUNDER},
    ]
    results = await rank_with_claude(pairs, SEARCH_REQUEST)

    # Find results by founder name
    strong_result = next((r for r in results if r["full_name"] == STRONG_FIT_FOUNDER["full_name"]), None)
    weak_result = next((r for r in results if r["full_name"] == WEAK_FIT_FOUNDER["full_name"]), None)

    assert strong_result is not None
    assert weak_result is not None
    assert strong_result["fit_score"] > weak_result["fit_score"]


@pytest.mark.llm
async def test_score_ranges():
    """Verify that strong fit scores >= 7 and weak fit scores <= 5."""
    pairs = [
        {"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER},
        {"company": WEAK_FIT_COMPANY, "founder": WEAK_FIT_FOUNDER},
    ]
    results = await rank_with_claude(pairs, SEARCH_REQUEST)

    strong_result = next((r for r in results if r["full_name"] == STRONG_FIT_FOUNDER["full_name"]), None)
    weak_result = next((r for r in results if r["full_name"] == WEAK_FIT_FOUNDER["full_name"]), None)

    assert strong_result is not None
    assert weak_result is not None
    assert strong_result["fit_score"] >= 7, f"Strong fit score {strong_result['fit_score']} should be >= 7"
    assert weak_result["fit_score"] <= 5, f"Weak fit score {weak_result['fit_score']} should be <= 5"


@pytest.mark.llm
async def test_outreach_template_adherence():
    """Verify that outreach messages follow the template and don't have unfilled placeholders."""
    pairs = [{"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER}]
    results = await rank_with_claude(pairs, SEARCH_REQUEST)

    for result in results:
        msg = result["outreach_message"]

        # Should not contain literal placeholder
        assert "[specific_detail]" not in msg, "Outreach message has unfilled placeholder"

        # Should contain the company name
        assert STRONG_FIT_COMPANY["company_name"] in msg or STRONG_FIT_COMPANY["company_name"].lower() in msg.lower(), (
            f"Outreach message does not mention company name: {msg}"
        )

        # Should mention the founder by name
        assert (
            STRONG_FIT_FOUNDER["full_name"] in msg or "you" in msg.lower() or "your" in msg.lower()
        ), f"Outreach message doesn't address the founder: {msg}"

        # Length sanity check
        assert 50 <= len(msg) <= 600, f"Outreach message length {len(msg)} out of reasonable bounds"


@pytest.mark.llm
async def test_results_sorted_by_score():
    """Verify that results are sorted by fit_score in descending order."""
    pairs = [
        {"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER},
        {"company": WEAK_FIT_COMPANY, "founder": WEAK_FIT_FOUNDER},
    ]
    results = await rank_with_claude(pairs, SEARCH_REQUEST)

    scores = [r["fit_score"] for r in results]
    assert scores == sorted(scores, reverse=True), f"Results not sorted by score descending: {scores}"


@pytest.mark.llm
async def test_founder_company_consistency():
    """Verify that full_name and company_name match the input."""
    pairs = [
        {"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER},
        {"company": WEAK_FIT_COMPANY, "founder": WEAK_FIT_FOUNDER},
    ]
    results = await rank_with_claude(pairs, SEARCH_REQUEST)

    # Check strong fit
    strong = next((r for r in results if r["full_name"] == STRONG_FIT_FOUNDER["full_name"]), None)
    assert strong is not None
    assert strong["company_name"] == STRONG_FIT_COMPANY["company_name"]

    # Check weak fit
    weak = next((r for r in results if r["full_name"] == WEAK_FIT_FOUNDER["full_name"]), None)
    assert weak is not None
    assert weak["company_name"] == WEAK_FIT_COMPANY["company_name"]
