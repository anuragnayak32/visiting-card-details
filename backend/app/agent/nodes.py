"""LangGraph node implementations for visiting card orchestration."""

from typing import Any

from app.config import get_settings
from app.services.contact_service import contact_service
from app.services.gemini_service import enrich_company_data, extract_card_data
from app.services.sheets_service import sheets_service
from app.services.whatsapp_service import send_whatsapp_notification
from app.services.whisper_service import transcribe_audio
from app.utils.helpers import generate_contact_id, utc_now_iso


def _append_message(state: dict[str, Any], role: str, content: str) -> list[dict[str, str]]:
    messages = list(state.get("messages") or [])
    messages.append({"role": role, "content": content})
    return messages


async def upload_card_node(state: dict[str, Any]) -> dict[str, Any]:
    """Receive and validate visiting card image path."""
    image_path = state.get("card_image_path", "")
    message = "Visiting card image received. Starting extraction..."
    return {
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def extract_card_data_node(state: dict[str, Any]) -> dict[str, Any]:
    """Use Gemini Vision to extract structured JSON from the card."""
    card_data = await extract_card_data(state["card_image_path"])

    # Bonus: company website and LinkedIn enrichment
    enrichment = await enrich_company_data(card_data.get("company", ""), card_data.get("name", ""))
    if enrichment.get("website") and not card_data.get("website"):
        card_data["website"] = enrichment["website"]
    if enrichment.get("linkedin"):
        card_data["linkedin"] = enrichment["linkedin"]

    preview = (
        f"Extracted contact details:\n"
        f"• Name: {card_data.get('name') or 'N/A'}\n"
        f"• Phone: {card_data.get('phone') or 'N/A'}\n"
        f"• Email: {card_data.get('email') or 'N/A'}\n"
        f"• Company: {card_data.get('company') or 'N/A'}\n"
        f"• Designation: {card_data.get('designation') or 'N/A'}\n"
        f"• Website: {card_data.get('website') or 'N/A'}\n"
        f"• Address: {card_data.get('address') or 'N/A'}"
    )
    return {
        "card_data": card_data,
        "enrichment": enrichment,
        "message": preview,
        "messages": _append_message(state, "assistant", preview),
    }


async def duplicate_check_node(state: dict[str, Any]) -> dict[str, Any]:
    """Check Google Sheets and MongoDB for duplicate contacts."""
    card_data = state.get("card_data") or {}
    sheet_duplicate = await sheets_service.find_duplicate(card_data)
    mongo_duplicate = await contact_service.find_duplicate(card_data)

    if sheet_duplicate or mongo_duplicate:
        existing = sheet_duplicate or mongo_duplicate
        message = (
            "Duplicate contact detected. This visiting card matches an existing entry.\n"
            f"Existing: {existing.get('name')} at {existing.get('company')} "
            f"({existing.get('email') or existing.get('phone')})"
        )
        return {
            "duplicate": True,
            "duplicate_source": "sheets" if sheet_duplicate else "mongodb",
            "contact_id": existing.get("contact_id"),
            "message": message,
            "messages": _append_message(state, "assistant", message),
        }

    message = "No duplicates found. Proceeding to confirmation."
    return {
        "duplicate": False,
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def human_confirmation_node(state: dict[str, Any]) -> dict[str, Any]:
    """Ask user to confirm extracted details before saving."""
    card_data = state.get("card_data") or {}
    if state.get("user_confirmed"):
        message = "Details confirmed. Saving contact..."
        return {
            "awaiting_confirmation": False,
            "message": message,
            "messages": _append_message(state, "assistant", message),
        }

    message = (
        "Are these extracted details correct?\n\n"
        f"Name: {card_data.get('name')}\n"
        f"Phone: {card_data.get('phone')}\n"
        f"Email: {card_data.get('email')}\n"
        f"Company: {card_data.get('company')}\n\n"
        "Please confirm to save this contact."
    )
    return {
        "awaiting_confirmation": True,
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def save_google_sheet_node(state: dict[str, Any]) -> dict[str, Any]:
    """Insert new contact row into Google Sheets."""
    card_data = state.get("card_data") or {}
    contact_id = state.get("contact_id") or generate_contact_id()
    contact = {
        "contact_id": contact_id,
        "session_id": state.get("session_id", ""),
        "name": card_data.get("name", ""),
        "phone": card_data.get("phone", ""),
        "email": card_data.get("email", ""),
        "company": card_data.get("company", ""),
        "designation": card_data.get("designation", ""),
        "website": card_data.get("website", ""),
        "address": card_data.get("address", ""),
        "linkedin": card_data.get("linkedin", ""),
        "audio_url": "",
        "transcript": "",
        "created_at": utc_now_iso(),
    }
    await sheets_service.insert_contact(contact)
    message = "Contact saved to Google Sheets."
    return {
        "contact_id": contact_id,
        "card_data": card_data,
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def save_mongodb_node(state: dict[str, Any]) -> dict[str, Any]:
    """Persist contact document in MongoDB."""
    card_data = state.get("card_data") or {}
    contact = {
        "contact_id": state.get("contact_id"),
        "session_id": state.get("session_id", ""),
        "name": card_data.get("name", ""),
        "phone": card_data.get("phone", ""),
        "email": card_data.get("email", ""),
        "company": card_data.get("company", ""),
        "designation": card_data.get("designation", ""),
        "website": card_data.get("website", ""),
        "address": card_data.get("address", ""),
        "linkedin": card_data.get("linkedin", ""),
        "audio_url": "",
        "transcript": "",
        "created_at": utc_now_iso(),
    }
    await contact_service.create_contact(contact)
    message = "Contact saved to MongoDB."
    return {
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def whatsapp_notification_node(state: dict[str, Any]) -> dict[str, Any]:
    """Send WhatsApp notification to manager."""
    card_data = state.get("card_data") or {}
    result = await send_whatsapp_notification(card_data)
    message = f"Workflow complete. {result}"
    return {
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def upload_audio_node(state: dict[str, Any]) -> dict[str, Any]:
    """Receive voice note audio file."""
    settings = get_settings()
    audio_path = state.get("audio_path", "")
    filename = audio_path.split("/")[-1].split("\\")[-1]
    audio_url = f"{settings.backend_url.rstrip('/')}/uploads/audio/{filename}"
    message = "Voice note received. Looking up associated contact..."
    return {
        "audio_url": audio_url,
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def find_contact_by_session_node(state: dict[str, Any]) -> dict[str, Any]:
    """Find contact linked to the current chat session."""
    session_id = state.get("session_id", "")
    contact = await contact_service.get_by_session_id(session_id)
    if not contact:
        message = (
            "No contact found for this session. "
            "Please upload a visiting card first before sending a voice note."
        )
        return {
            "message": message,
            "messages": _append_message(state, "assistant", message),
        }

    message = f"Found contact: {contact.get('name')} ({contact.get('company')}). Transcribing audio..."
    return {
        "contact_id": contact.get("contact_id"),
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def transcribe_audio_node(state: dict[str, Any]) -> dict[str, Any]:
    """Transcribe voice note using Whisper."""
    if not state.get("contact_id"):
        return {"transcript": "", "message": state.get("message", "")}

    transcript = await transcribe_audio(state.get("audio_path", ""))
    message = f"Transcription complete:\n\n{transcript}"
    return {
        "transcript": transcript,
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def update_google_sheet_node(state: dict[str, Any]) -> dict[str, Any]:
    """Update existing Google Sheets row with audio URL and transcript."""
    contact_id = state.get("contact_id")
    if not contact_id:
        return {"message": state.get("message", "")}

    updated = await sheets_service.update_contact(
        contact_id,
        {
            "audio_url": state.get("audio_url", ""),
            "transcript": state.get("transcript", ""),
        },
    )
    message = "Google Sheet updated with voice note." if updated else "Failed to update Google Sheet."
    return {
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }


async def update_mongodb_node(state: dict[str, Any]) -> dict[str, Any]:
    """Save transcription and audio URL in MongoDB."""
    contact_id = state.get("contact_id")
    if not contact_id:
        return {"message": state.get("message", "")}

    await contact_service.update_contact(
        contact_id,
        {
            "audio_url": state.get("audio_url", ""),
            "transcript": state.get("transcript", ""),
        },
    )
    message = "MongoDB updated with voice note and transcript. Voice workflow complete."
    return {
        "message": message,
        "messages": _append_message(state, "assistant", message),
    }
