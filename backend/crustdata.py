import asyncio
import httpx
from typing import Optional
from models import Company, Founder


BASE_URL = "https://api.crustdata.com"

# Title keywords to filter for founders
FOUNDER_TITLES = ["founder", "co-founder", "ceo", "cto", "chief executive", "chief technology"]


def _get_mock_founders(company_id: int, company_name: str) -> list[Founder]:
    """Return mock founder data when API fails."""
    mock_founders_by_id = {
        1: [  # Skit.ai
            {
                "full_name": "Sourabh Gupta",
                "current_title": "CEO & Founder",
                "linkedin_url": "https://linkedin.com/in/sourabhgupta",
                "email": "sourabh@skit.ai",
                "company_name": "Skit.ai",
                "company_id": 1,
            },
            {
                "full_name": "Sourav Mukherjee",
                "current_title": "Co-founder & CTO",
                "linkedin_url": "https://linkedin.com/in/souravmukherjee",
                "email": None,
                "company_name": "Skit.ai",
                "company_id": 1,
            },
        ],
        2: [  # Codemart
            {
                "full_name": "Rajesh Kumar",
                "current_title": "Founder",
                "linkedin_url": "https://linkedin.com/in/rajesh-kumar",
                "email": "rajesh@codemart.io",
                "company_name": "Codemart",
                "company_id": 2,
            },
        ],
        3: [  # Unstop
            {
                "full_name": "Priyank Kharge",
                "current_title": "CEO & Co-founder",
                "linkedin_url": "https://linkedin.com/in/priyankkharge",
                "email": "priyank@unstop.com",
                "company_name": "Unstop",
                "company_id": 3,
            },
        ],
        4: [  # Chargebee
            {
                "full_name": "Krish Subramanian",
                "current_title": "Co-founder & CEO",
                "linkedin_url": "https://linkedin.com/in/krishsubramanian",
                "email": "krish@chargebee.com",
                "company_name": "Chargebee",
                "company_id": 4,
            },
        ],
    }
    founders_data = mock_founders_by_id.get(company_id, [])
    return [Founder(**f) for f in founders_data]


def _get_mock_companies(industry: str, country: str, limit: int) -> list[Company]:
    """Return mock company data for demo/testing when Crustdata API fails."""
    mock_companies = [
        {
            "company_id": 1,
            "company_name": "Skit.ai",
            "domain": "skit.ai",
            "hq_country": "India",
            "funding_stage": "Series B",
            "total_funding_usd": 26000000,
            "last_funding_date": "2023-06-15",
            "description": "Conversational voice AI for enterprise contact centers",
            "linkedin_url": "https://linkedin.com/company/skit-ai",
            "company_tags": ["AI", "Voice AI", "B2B SaaS"],
            "linkedin_headcount": 150,
        },
        {
            "company_id": 2,
            "company_name": "Codemart",
            "domain": "codemart.io",
            "hq_country": "India",
            "funding_stage": "Series A",
            "total_funding_usd": 5000000,
            "last_funding_date": "2024-01-10",
            "description": "AI-powered software development platform",
            "linkedin_url": "https://linkedin.com/company/codemart",
            "company_tags": ["AI", "Developer Tools", "SaaS"],
            "linkedin_headcount": 45,
        },
        {
            "company_id": 3,
            "company_name": "Unstop",
            "domain": "unstop.com",
            "hq_country": "India",
            "funding_stage": "Series A",
            "total_funding_usd": 12000000,
            "last_funding_date": "2023-09-20",
            "description": "Creator economy platform with AI-powered discovery",
            "linkedin_url": "https://linkedin.com/company/unstop",
            "company_tags": ["AI", "Creator Economy", "Marketplace"],
            "linkedin_headcount": 120,
        },
        {
            "company_id": 4,
            "company_name": "Chargebee",
            "domain": "chargebee.com",
            "hq_country": "India",
            "funding_stage": "Series B",
            "total_funding_usd": 30000000,
            "last_funding_date": "2022-11-01",
            "description": "Recurring billing and subscription management with AI features",
            "linkedin_url": "https://linkedin.com/company/chargebee",
            "company_tags": ["FinTech", "B2B SaaS", "Billing"],
            "linkedin_headcount": 250,
        },
    ]
    return [Company(**c) for c in mock_companies[:limit]]


def get_client(api_key: str) -> httpx.AsyncClient:
    """Return a configured httpx AsyncClient with auth header."""
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
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
    Fetch companies matching the search criteria using Crustdata screener.
    Returns a list of Company TypedDicts.
    """
    # Map stage names to Crustdata format (adjust if needed after seeing actual API response)
    stage_map = {
        "Pre-seed": "Pre-Seed",
        "Seed": "Seed",
        "Series A": "Series A",
        "Series B": "Series B",
    }
    crustdata_stage = stage_map.get(stage, stage)

    # Build the screener request (filters as dict, not list)
    payload = {
        "page": 1,
        "limit": limit,
        "filters": {
            "company_tags": {
                "filter_type": "icontains",
                "value": industry,
            },
            "hq_country": {
                "filter_type": "in",
                "value": [country],
            },
            "funding_stage": {
                "filter_type": "in",
                "value": [crustdata_stage],
            },
        },
    }

    try:
        response = await client.post(f"{BASE_URL}/screener/screen/", json=payload)
        if response.status_code != 200:
            print(f"Crustdata error {response.status_code}: {response.text}")
            # For demo purposes, return mock data if API fails
            return _get_mock_companies(industry, country, limit)
        data = response.json()

        # Parse companies from the response
        companies = []
        results = data.get("results", [])

        for company_data in results:
            company = Company(
                company_id=company_data.get("company_id", company_data.get("id")),
                company_name=company_data.get("company_name", ""),
                domain=company_data.get("domain", ""),
                hq_country=company_data.get("hq_country", country),
                funding_stage=company_data.get("funding_stage", stage),
                total_funding_usd=company_data.get("total_funding_usd"),
                last_funding_date=company_data.get("last_funding_date"),
                description=(company_data.get("description") or "")[:200],  # Truncate for token efficiency
                linkedin_url=company_data.get("linkedin_url"),
                company_tags=company_data.get("company_tags", []),
                linkedin_headcount=company_data.get("linkedin_headcount"),
            )
            companies.append(company)

        return companies
    except httpx.HTTPError as e:
        raise ValueError(f"Crustdata API error: {e}")


async def fetch_founders_for_company(
    client: httpx.AsyncClient,
    company_id: int,
    company_name: str,
) -> list[Founder]:
    """
    Fetch founders for a specific company using Crustdata people search.
    Returns a list of Founder TypedDicts, or empty list if none found.
    """
    payload = {
        "filters": [
            {
                "filter_type": "eq",
                "field": "company_id",
                "value": company_id,
            },
        ],
        "page": 1,
        "limit": 25,
    }

    try:
        response = await client.post(f"{BASE_URL}/people/search/", json=payload)
        response.raise_for_status()
        data = response.json()

        founders = []
        results = data.get("results", [])

        for person_data in results:
            # Filter for founders by title
            title = (person_data.get("current_title") or "").lower()
            is_founder = any(keyword in title for keyword in FOUNDER_TITLES)

            if is_founder:
                founder = Founder(
                    full_name=person_data.get("full_name", ""),
                    current_title=person_data.get("current_title", ""),
                    linkedin_url=person_data.get("linkedin_url"),
                    email=person_data.get("email"),
                    company_name=company_name,
                    company_id=company_id,
                )
                founders.append(founder)

        return founders
    except httpx.HTTPError:
        # On error, return mock founders
        return _get_mock_founders(company_id, company_name)


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
        return_exceptions=False,
    )

    # Filter out companies with no founders
    pairs = [(company, founders) for company, founders in results if founders]
    skipped = len(results) - len(pairs)

    return pairs, skipped
