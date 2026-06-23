"""Gemini vision and LLM service for card extraction and enrichment."""

import json
import re
from typing import Any

import google.generativeai as genai

from app.config import get_settings


def _configure() -> None:
    settings = get_settings()
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)


def _parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


async def extract_card_data(image_path: str) -> dict[str, Any]:
    """Extract structured contact fields from a visiting card image."""
    _configure()
    settings = get_settings()
    if not settings.gemini_api_key:
        return {
            "name": "Demo User",
            "phone": "+1 555-0100",
            "email": "demo@example.com",
            "company": "Demo Corp",
            "designation": "Sales Manager",
            "website": "https://example.com",
            "address": "123 Demo Street",
        }

    model = genai.GenerativeModel("gemini-2.5-flash")
    uploaded = genai.upload_file(image_path)

    prompt = """Extract contact information from this visiting card image.
Return ONLY valid JSON with these keys:
name, phone, email, company, designation, website, address.
Use empty strings for missing fields."""

    response = model.generate_content([prompt, uploaded])
    data = _parse_json_response(response.text or "{}")
    return {
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "company": data.get("company", ""),
        "designation": data.get("designation", ""),
        "website": data.get("website", ""),
        "address": data.get("address", ""),
        "linkedin": data.get("linkedin", ""),
    }


async def enrich_company_data(company: str, name: str = "") -> dict[str, str]:
    """Bonus: enrich company website and LinkedIn profile using Gemini."""
    _configure()
    settings = get_settings()
    if not settings.gemini_api_key or not company:
        return {"website": "", "linkedin": ""}

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""For company "{company}" and contact "{name}", suggest the most likely:
1. Official company website URL
2. LinkedIn company or person profile URL

Return ONLY JSON: {{"website": "...", "linkedin": "..."}}
Use empty strings if unknown. Do not invent fake URLs."""

    response = model.generate_content(prompt)
    data = _parse_json_response(response.text or "{}")
    return {
        "website": data.get("website", ""),
        "linkedin": data.get("linkedin", ""),
    }
