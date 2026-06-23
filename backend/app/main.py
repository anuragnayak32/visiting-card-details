"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_settings
from app.models.database import close_db, connect_db

settings = get_settings()

print("CORS_ORIGINS =", settings.cors_origins)
print("CORS_LIST =", settings.cors_origin_list)

app = FastAPI(
    title="Visiting Card Digitization & Voice Notes Orchestrator",
    description="AI-powered visiting card processing with LangGraph orchestration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
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
