import json
import re
import anthropic
from models import Company, Founder, FounderResult, SearchRequest


SYSTEM_PROMPT = """You are a recruiting advisor evaluating startup founders as potential employers for a software engineer.

Candidate profile:
- Background: 3 years in PM and founder's office roles, shipped end-to-end products
- Now moving into AI engineering
- Brings: product thinking, extreme ownership, ability to build AI systems end-to-end
- Seeking: an engineering role in an ambitious team, not optimizing for title

For each founder + company pair, return a JSON object with:
- full_name: the founder's name (exact from input)
- company_name: the company name (exact from input)
- fit_score: integer 1-10 (10 = perfect fit)
- fit_explanation: 2-3 sentences explaining why this is a good fit
- outreach_message: a personalized message following this template (fill in [specific_detail] only):

Hey [founder_name], Love [specific_detail] that you're building at [company_name]. I am moving to AI engineering after 3 years of PM and founder's office roles where I owned 0-1 products and shipped end-to-end. I bring product thinking and crazy ownership along with the ability to build AI systems end to end. I have a genuine desire to learn and I am not looking for a perfect title. Just an engineering role in an ambitious team. Would love to chat :)

[specific_detail] must be a concrete fact about the company (product, mission, funding, tech stack) — never generic praise.

Scoring:
- 9-10: Perfect fit on industry + stage + hiring signals
- 7-8: Strong alignment on 2+ dimensions
- 5-6: Partial match, worth reaching out
- Below 5: Include all founders — return every result ranked by score

Return ONLY a JSON array of ALL founders sorted by fit_score descending. Do not filter out any founder. No markdown, no explanation."""


def build_user_prompt(
    pairs: list[dict],
    request: SearchRequest,
) -> str:
    """Build the user message for Claude with company and founder data."""
    content = f"""Find startup founders for this engineer:

SEARCH CRITERIA:
- Industry: {request.industry}
- Target country: {request.country}
- Preferred stage: {request.stage}
- Role interest: {request.role_interest}

COMPANIES AND FOUNDERS:
"""

    for pair in pairs:
        founder = pair["founder"]
        company = pair["company"]
        funding = company.get("total_funding_usd")
        funding_str = f"${funding/1e6:.1f}M" if funding else "Unknown"
        tags_str = ", ".join(company["company_tags"][:3]) if company["company_tags"] else "N/A"
        description = company.get("description") or "N/A"
        linkedin_url = company.get("linkedin_url") or "N/A"

        content += f"""
---
Company: {company["company_name"]}
Stage: {company.get("funding_stage", "Unknown")} | Country: {company.get("hq_country", "Unknown")} | Funding: {funding_str}
Tags: {tags_str}
Description: {description}
LinkedIn: {linkedin_url}

Founder: {founder["full_name"]} | {founder["current_title"]}
Email: {founder.get("email", "N/A")}
LinkedIn: {founder.get("linkedin_url", "N/A")}
"""

    return content


async def rank_with_claude(
    pairs: list[dict],
    request: SearchRequest,
    model: str = "claude-haiku-4-5-20251001",
) -> list[FounderResult]:
    """
    Call Claude to rank and analyze founders in a single batch call.
    Returns a list of FounderResult TypedDicts sorted by fit_score.
    """
    client = anthropic.Anthropic()

    user_prompt = build_user_prompt(pairs, request)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )

        raw_text = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1].rsplit("```", 1)[0]

        # Parse JSON
        results_raw = json.loads(raw_text)

        # Convert to FounderResult list
        results = []
        for item in results_raw:
            result = FounderResult(
                full_name=item["full_name"],
                company_name=item["company_name"],
                fit_score=item["fit_score"],
                fit_explanation=item["fit_explanation"],
                outreach_message=item["outreach_message"],
            )
            results.append(result)

        # Already sorted by Claude, but sort again to be safe
        results = sorted(results, key=lambda x: x["fit_score"], reverse=True)
        return results

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Claude's JSON response: {e}")
    except (KeyError, anthropic.APIError) as e:
        raise ValueError(f"Claude API error: {e}")
