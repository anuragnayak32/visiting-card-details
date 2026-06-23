"""FastAPI application entry point."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_settings
from app.models.database import close_db, connect_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)

settings = get_settings()

key = settings.gemini_api_key
key_prefix = key[:6] + "..." if len(key) >= 6 else "(empty)"
print("CORS_ORIGINS =", settings.cors_origins)
print("CORS_LIST =", settings.cors_origin_list)
print(f"GEMINI_API_KEY prefix: {key_prefix}  (length: {len(key)})")
if not key:
    print("WARNING: GEMINI_API_KEY is empty — card extraction will return demo data!")
if key and not key.startswith("AIzaSy"):
    print(
        "WARNING: GEMINI_API_KEY does not start with 'AIzaSy' — "
        "this may not be a valid Google API key. Check your .env file."
    )

app = FastAPI(
    title="Visiting Card Digitization & Voice Notes Orchestrator",
    description="AI-powered visiting card processing with LangGraph orchestration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "cards"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "audio"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "visiting-card-orchestrator"}
