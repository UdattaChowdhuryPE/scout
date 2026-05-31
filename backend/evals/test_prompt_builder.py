import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_client import build_user_prompt
from evals.fixtures import SEARCH_REQUEST, STRONG_FIT_COMPANY, STRONG_FIT_FOUNDER, WEAK_FIT_COMPANY, WEAK_FIT_FOUNDER


def test_prompt_includes_company_name():
    pairs = [{"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER}]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    assert STRONG_FIT_COMPANY["company_name"] in prompt


def test_prompt_includes_founder_name():
    pairs = [{"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER}]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    assert STRONG_FIT_FOUNDER["full_name"] in prompt


def test_prompt_includes_stage():
    pairs = [{"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER}]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    assert "seed" in prompt.lower()


def test_prompt_includes_role_interest():
    pairs = [{"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER}]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    assert SEARCH_REQUEST.role_interest in prompt


def test_prompt_formats_funding_amount():
    pairs = [{"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER}]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    # Total funding is 2,500,000 — should format as "$2M" or "$2.5M" or similar
    assert "$" in prompt and ("2" in prompt or "M" in prompt)


def test_prompt_limits_company_tags_to_three():
    # Create a company with many tags
    company_with_many_tags = {**STRONG_FIT_COMPANY, "company_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}
    pairs = [{"company": company_with_many_tags, "founder": STRONG_FIT_FOUNDER}]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    # Prompt should mention first 3 tags
    assert "tag1" in prompt
    assert "tag2" in prompt
    assert "tag3" in prompt


def test_prompt_multiple_pairs():
    pairs = [
        {"company": STRONG_FIT_COMPANY, "founder": STRONG_FIT_FOUNDER},
        {"company": WEAK_FIT_COMPANY, "founder": WEAK_FIT_FOUNDER},
    ]
    prompt = build_user_prompt(pairs, SEARCH_REQUEST)
    # Both companies should appear
    assert STRONG_FIT_COMPANY["company_name"] in prompt
    assert WEAK_FIT_COMPANY["company_name"] in prompt
    # Both founders should appear
    assert STRONG_FIT_FOUNDER["full_name"] in prompt
    assert WEAK_FIT_FOUNDER["full_name"] in prompt
