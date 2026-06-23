"""FastAPI route handlers."""

import logging
import os
import uuid
from typing import Optional

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agent.graph import resume_card_flow, run_card_flow, run_voice_flow
from app.config import get_settings
from app.schemas.schemas import (
    AudioUploadResponse,
    CardData,
    CardUploadResponse,
    ConfirmRequest,
    ConfirmResponse,
    ContactResponse,
    SessionCreateResponse,
    SessionDetail,
    SessionSummary,
)
from app.services.session_service import session_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


async def _save_upload(file: UploadFile, subdir: str) -> str:
    settings = get_settings()
    upload_dir = os.path.join(settings.upload_dir, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    async with aiofiles.open(filepath, "wb") as handle:
        content = await file.read()
        await handle.write(content)
    return filepath


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session():
    session = await session_service.create_session()
    return SessionCreateResponse(session_id=session["session_id"], title=session["title"])


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions():
    sessions = await session_service.list_sessions()
    return [SessionSummary(**session) for session in sessions]


@router.get("/session/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetail(**session)


@router.post("/card/upload", response_model=CardUploadResponse)
async def upload_card(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    filepath = await _save_upload(file, "cards")
    await session_service.add_message(
        session_id,
        "user",
        f"Uploaded visiting card: {file.filename}",
        {"type": "image", "filename": file.filename},
    )

    try:
        result = await run_card_flow(session_id, filepath)
    except ValueError as exc:
        logger.error("Image processing error in card upload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Gemini API error in card upload: %s", exc)
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error in card upload for session %s", session_id)
        raise HTTPException(status_code=500, detail="Internal server error during card processing") from exc

    card_data = result.get("card_data") or {}

    if result.get("message"):
        await session_service.add_message(session_id, "assistant", result["message"])

    awaiting = result.get("awaiting_confirmation", False) or bool(
        result.get("duplicate") is False and not result.get("user_confirmed")
    )

    await session_service.update_session(
        session_id,
        {
            "card_data": card_data,
            "awaiting_confirmation": awaiting and not result.get("duplicate"),
            "contact_id": result.get("contact_id"),
            "title": card_data.get("name") or session.get("title") or "New Chat",
        },
    )

    return CardUploadResponse(
        session_id=session_id,
        message=result.get("message", ""),
        card_data=CardData(**card_data) if card_data else None,
        duplicate=bool(result.get("duplicate")),
        awaiting_confirmation=awaiting and not result.get("duplicate"),
        contact_id=result.get("contact_id"),
    )


@router.post("/confirm", response_model=ConfirmResponse)
async def confirm_details(payload: ConfirmRequest):
    session = await session_service.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not payload.confirmed:
        await session_service.update_session(
            payload.session_id,
            {"awaiting_confirmation": False, "card_data": None},
        )
        await session_service.add_message(
            payload.session_id,
            "assistant",
            "Contact save cancelled. You can upload a new card anytime.",
        )
        return ConfirmResponse(
            session_id=payload.session_id,
            message="Contact save cancelled.",
            success=False,
        )

    card_data = payload.card_data.model_dump() if payload.card_data else session.get("card_data") or {}
    result = await resume_card_flow(payload.session_id, True, card_data)

    if result.get("message"):
        await session_service.add_message(payload.session_id, "assistant", result["message"])

    await session_service.update_session(
        payload.session_id,
        {
            "awaiting_confirmation": False,
            "contact_id": result.get("contact_id"),
            "card_data": card_data,
        },
    )

    return ConfirmResponse(
        session_id=payload.session_id,
        message=result.get("message", "Contact saved successfully."),
        contact_id=result.get("contact_id"),
        success=True,
    )


@router.post("/audio/upload", response_model=AudioUploadResponse)
async def upload_audio(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    filepath = await _save_upload(file, "audio")
    await session_service.add_message(
        session_id,
        "user",
        f"Uploaded voice note: {file.filename}",
        {"type": "audio", "filename": file.filename},
    )

    try:
        result = await run_voice_flow(session_id, filepath)
    except ValueError as exc:
        logger.error("Audio processing error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("AI service error in audio upload: %s", exc)
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error in audio upload for session %s", session_id)
        raise HTTPException(status_code=500, detail="Internal server error during audio processing") from exc

    if result.get("message"):
        await session_service.add_message(session_id, "assistant", result["message"])

    return AudioUploadResponse(
        session_id=session_id,
        message=result.get("message", ""),
        contact_id=result.get("contact_id"),
        transcript=result.get("transcript"),
        audio_url=result.get("audio_url"),
    )


@router.get("/contact/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str):
    from app.services.contact_service import contact_service

    contact = await contact_service.get_by_contact_id(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactResponse(**contact)
