from typing import TypedDict, Optional
from pydantic import BaseModel


class Company(TypedDict):
    company_id: int
    company_name: str
    domain: str
    hq_country: str
    funding_stage: str
    total_funding_usd: Optional[int]
    last_funding_date: Optional[str]
    description: Optional[str]
    linkedin_url: Optional[str]
    company_tags: list[str]
    linkedin_headcount: Optional[int]


class Founder(TypedDict):
    full_name: str
    current_title: str
    linkedin_url: Optional[str]
    email: Optional[str]
    company_name: str
    company_id: int


class FounderResult(TypedDict):
    full_name: str
    company_name: str
    fit_score: int
    fit_explanation: str
    outreach_message: str
    linkedin_url: Optional[str]


class SearchRequest(BaseModel):
    industry: str
    country: str
    stage: str
    role_interest: str
