import asyncio
import httpx
import logging
from typing import Optional
from models import Company, Founder

logger = logging.getLogger(__name__)

BASE_URL = "https://api.crustdata.com"

# Title keywords to filter for founders
FOUNDER_TITLES = ["founder", "co-founder", "ceo", "cto", "chief executive", "chief technology"]


def get_client(api_key: str) -> httpx.AsyncClient:
    """Return a configured httpx AsyncClient with auth headers."""
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
        "x-api-version": "2025-11-01",
    }
    return httpx.AsyncClient(headers=headers, timeout=30.0)


async def fetch_companies(
    client: httpx.AsyncClient,
    industry: str,
    country: str,
    stage: str,
    limit: int = 20,
) -> list[Company]:
    """
    Fetch companies matching the search criteria using Crustdata company search.
    Returns a list of Company TypedDicts.
    """
    stage_map = {
        "Pre-seed": "Pre-Seed",
        "Seed": "Seed",
        "Series A": "Series A",
        "Series B": "Series B",
    }
    crustdata_stage = stage_map.get(stage, stage)

    payload = {
        "filters": {
            "op": "and",
            "conditions": [
                {
                    "field": "taxonomy.professional_network_industry",
                    "type": "(.)",
                    "value": industry.lower(),
                },
                {
                    "field": "locations.headquarters",
                    "type": "=",
                    "value": country,
                },
                {
                    "field": "funding.last_round_type",
                    "type": "in",
                    "value": [crustdata_stage.lower().replace(" ", "_")],
                },
            ],
        },
        "limit": limit,
        "fields": [
            "crustdata_company_id",
            "basic_info.name",
            "basic_info.primary_domain",
            "basic_info.professional_network_url",
            "basic_info.professional_network_id",
            "basic_info.year_founded",
            "basic_info.employee_count_range",
            "basic_info.industries",
            "headcount.total",
            "locations.headquarters",
            "funding.total_investment_usd",
            "funding.last_fundraise_date",
            "funding.last_round_type",
        ],
    }

    try:
        response = await client.post(f"{BASE_URL}/company/search", json=payload)
        if response.status_code != 200:
            logger.error(f"Company search error {response.status_code}: {response.text}")
            raise ValueError(f"Crustdata API returned {response.status_code}: {response.text}")
        data = response.json()

        companies = []
        results = data.get("companies", [])

        for company_data in results:
            company = Company(
                company_id=company_data.get("crustdata_company_id"),
                company_name=company_data.get("basic_info", {}).get("name", ""),
                domain=company_data.get("basic_info", {}).get("primary_domain", ""),
                hq_country=company_data.get("locations", {}).get("headquarters", country),
                funding_stage=company_data.get("funding", {}).get("last_round_type", stage),
                total_funding_usd=company_data.get("funding", {}).get("total_investment_usd"),
                last_funding_date=company_data.get("funding", {}).get("last_fundraise_date"),
                description=company_data.get("basic_info", {}).get("description", "")[:200],
                linkedin_url=company_data.get("basic_info", {}).get("professional_network_url"),
                company_tags=company_data.get("basic_info", {}).get("industries", [industry]),
                linkedin_headcount=company_data.get("headcount", {}).get("total"),
            )
            companies.append(company)

        logger.info(f"[PIPELINE] companies_fetched={len(companies)}")
        return companies
    except httpx.HTTPError as e:
        raise ValueError(f"Crustdata company search error: {e}")


async def fetch_founders_for_company(
    client: httpx.AsyncClient,
    company_id: int,
    company_name: str,
) -> list[Founder]:
    """
    Fetch founders for a specific company using Crustdata person search.
    Returns a list of Founder TypedDicts, or empty list if none found.
    """
    payload = {
        "filters": {
            "field": "experience.employment_details.current.company_name",
            "type": "=",
            "value": company_name,
        },
        "limit": 25,
    }

    try:
        response = await client.post(f"{BASE_URL}/person/search", json=payload)
        if response.status_code != 200:
            logger.error(f"Person search error {response.status_code}: {response.text}")
            raise ValueError(f"Crustdata API returned {response.status_code}: {response.text}")
        data = response.json()

        founders = []
        results = data.get("profiles", [])

        for person_data in results:
            basic_profile = person_data.get("basic_profile", {})
            title = (basic_profile.get("current_title") or "").lower()
            is_founder = any(keyword in title for keyword in FOUNDER_TITLES)

            if is_founder:
                social_handles = person_data.get("social_handles", {})
                linkedin_url = social_handles.get("professional_network_identifier", {}).get("profile_url")

                founder = Founder(
                    full_name=basic_profile.get("name", ""),
                    current_title=basic_profile.get("current_title", ""),
                    linkedin_url=linkedin_url,
                    email=None,  # Not available in Crustdata person/search response
                    company_name=company_name,
                    company_id=company_id,
                )
                founders.append(founder)

        return founders
    except httpx.HTTPError as e:
        raise ValueError(f"Crustdata person search error for {company_name}: {e}")


async def fetch_all_founders(
    client: httpx.AsyncClient,
    companies: list[Company],
) -> tuple[list[tuple[Company, list[Founder]]], int]:
    """
    Fetch founders for all companies using parallel requests with a semaphore.
    Returns pairs of (Company, Founders) and count of skipped companies.
    """
    semaphore = asyncio.Semaphore(5)

    async def bounded_fetch(company: Company) -> tuple[Company, list[Founder]]:
        async with semaphore:
            founders = await fetch_founders_for_company(
                client,
                company["company_id"],
                company["company_name"],
            )
            return (company, founders)

    results = await asyncio.gather(
        *[bounded_fetch(company) for company in companies],
        return_exceptions=True,
    )

    pairs = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Skipped company due to fetch error: {result}")
        else:
            company, founders = result
            if founders:
                pairs.append((company, founders))
    skipped = len(results) - len(pairs)

    total = sum(len(f) for _, f in pairs)
    logger.info(f"[PIPELINE] companies_with_founders={len(pairs)}")
    logger.info(f"[PIPELINE] total_founders={total}")

    return pairs, skipped
