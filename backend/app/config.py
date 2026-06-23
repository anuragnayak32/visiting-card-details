"""Application configuration loaded from environment variables."""

import json
import os
from functools import lru_cache

from pydantic_settings import BaseSettings


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
    return Settings()
