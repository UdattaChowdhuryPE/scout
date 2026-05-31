import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Company, Founder, SearchRequest

# Strong fit: AI infra startup, seed stage, CTO with AI experience
STRONG_FIT_COMPANY: Company = {
    "company_id": 1001,
    "company_name": "LLMCore",
    "domain": "llmcore.io",
    "hq_country": "United States",
    "funding_stage": "seed",
    "total_funding_usd": 2500000,
    "last_funding_date": "2025-12-01",
    "description": "Building open-source infrastructure for LLM fine-tuning and deployment with focus on distributed training at scale.",
    "linkedin_url": "https://www.linkedin.com/company/llmcore/",
    "company_tags": ["artificial intelligence", "machine learning", "infrastructure"],
    "linkedin_headcount": 8,
}

STRONG_FIT_FOUNDER: Founder = {
    "full_name": "Sarah Chen",
    "current_title": "CTO & Co-Founder",
    "linkedin_url": "https://www.linkedin.com/in/sarahchen/",
    "email": "sarah@llmcore.io",
    "company_name": "LLMCore",
    "company_id": 1001,
}

# Weak fit: Retail company, large stage, merchandising head with no engineering signal
WEAK_FIT_COMPANY: Company = {
    "company_id": 2001,
    "company_name": "StyleHub",
    "domain": "stylehub.co.uk",
    "hq_country": "United Kingdom",
    "funding_stage": "series_d",
    "total_funding_usd": 45000000,
    "last_funding_date": "2023-03-15",
    "description": "Online fashion and lifestyle marketplace connecting independent designers with consumers across Europe.",
    "linkedin_url": "https://www.linkedin.com/company/stylehub/",
    "company_tags": ["ecommerce", "fashion", "retail"],
    "linkedin_headcount": 280,
}

WEAK_FIT_FOUNDER: Founder = {
    "full_name": "Michael Roberts",
    "current_title": "Head of Merchandising",
    "linkedin_url": "https://www.linkedin.com/in/michael-roberts-merch/",
    "email": "michael@stylehub.co.uk",
    "company_name": "StyleHub",
    "company_id": 2001,
}

# Search context for evaluation
SEARCH_REQUEST = SearchRequest(
    industry="artificial intelligence",
    country="United States",
    stage="seed",
    role_interest="AI engineering role at an early-stage AI infrastructure company",
)
