"""Gemini vision and LLM service for card extraction and enrichment."""

import json
import logging
import re
from typing import Any

import google.generativeai as genai
from PIL import Image

from app.config import get_settings

logger = logging.getLogger(__name__)


def _configure() -> None:
    """Configure the Gemini SDK with the API key from settings."""
    settings = get_settings()
    key = settings.gemini_api_key
    if key:
        key_prefix = key[:6] + "..." if len(key) >= 6 else "(too-short)"
        logger.info("Configuring Gemini SDK — key prefix: %s (length: %d)", key_prefix, len(key))
        genai.configure(api_key=key)
    else:
        logger.warning("GEMINI_API_KEY is empty — Gemini calls will fail or return demo data.")


def _parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Gemini returned non-JSON response: %s", cleaned[:200])
        return {}


async def extract_card_data(image_path: str) -> dict[str, Any]:
    """Extract structured contact fields from a visiting card image.

    Uses PIL to load the image and passes it directly to
    ``model.generate_content()`` instead of ``genai.upload_file()``.
    This avoids the separate File Upload API which has stricter
    authentication requirements and can fail even when the key
    is valid for text generation.
    """
    _configure()
    settings = get_settings()
    if not settings.gemini_api_key:
        logger.warning("No GEMINI_API_KEY configured — returning demo data.")
        return {
            "name": "Demo User",
            "phone": "+1 555-0100",
            "email": "demo@example.com",
            "company": "Demo Corp",
            "designation": "Sales Manager",
            "website": "https://example.com",
            "address": "123 Demo Street",
        }

    try:
        img = Image.open(image_path)
        # Convert to RGB to avoid issues with RGBA/P mode images
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
    except Exception as exc:
        logger.error("Failed to open image at %s: %s", image_path, exc)
        raise ValueError(f"Cannot open image file: {exc}") from exc

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = """Extract contact information from this visiting card image.
Return ONLY valid JSON with these keys:
name, phone, email, company, designation, website, address.
Use empty strings for missing fields."""

    try:
        response = model.generate_content([prompt, img])
    except Exception as exc:
        logger.error("Gemini generate_content failed for card extraction: %s", exc)
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc

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

    try:
        response = model.generate_content(prompt)
    except Exception as exc:
        logger.error("Gemini generate_content failed for enrichment: %s", exc)
        raise RuntimeError(f"Gemini enrichment call failed: {exc}") from exc

    data = _parse_json_response(response.text or "{}")
    return {
        "website": data.get("website", ""),
        "linkedin": data.get("linkedin", ""),
    }
