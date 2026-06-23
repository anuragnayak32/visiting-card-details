"""Application configuration loaded from environment variables."""

import json
import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    gemini_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "visiting_cards"
    google_sheet_id: str = ""
    google_service_account_json: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    manager_phone_number: str = ""
    upload_dir: str = "./uploads"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def google_credentials(self) -> dict:
        if not self.google_service_account_json:
            return {}
        try:
            return json.loads(self.google_service_account_json)
        except json.JSONDecodeError:
            path = self.google_service_account_json
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as handle:
                    return json.load(handle)
            return {}


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    key = settings.gemini_api_key
    key_prefix = key[:6] + "..." if len(key) >= 6 else "(empty or too-short)"
    logger.info(
        "Settings loaded — GEMINI_API_KEY prefix: %s (length: %d)",
        key_prefix,
        len(key),
    )
    if not key:
        logger.warning("GEMINI_API_KEY is NOT set. Card extraction will return demo data.")
    elif not key.startswith("AIzaSy"):
        logger.warning(
            "GEMINI_API_KEY does not start with 'AIzaSy' — this may not be a valid Google API key. "
            "Please verify the key in your .env file.",
        )
    return settings
