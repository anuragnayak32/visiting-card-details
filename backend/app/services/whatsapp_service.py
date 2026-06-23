"""Twilio WhatsApp notification service."""

from twilio.rest import Client

from app.config import get_settings


async def send_whatsapp_notification(contact: dict) -> str:
    """Send WhatsApp alert when a new visiting card is logged."""
    settings = get_settings()
    if not all(
        [
            settings.twilio_account_sid,
            settings.twilio_auth_token,
            settings.twilio_whatsapp_number,
            settings.manager_phone_number,
        ]
    ):
        return "WhatsApp notification skipped (Twilio credentials not configured)."

    body = (
        "New Visiting Card Added\n\n"
        f"Name: {contact.get('name', 'N/A')}\n"
        f"Company: {contact.get('company', 'N/A')}\n"
        f"Phone: {contact.get('phone', 'N/A')}\n"
        f"Email: {contact.get('email', 'N/A')}"
    )

    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        message = client.messages.create(
            from_=settings.twilio_whatsapp_number,
            to=settings.manager_phone_number,
            body=body,
        )
        return f"WhatsApp notification sent (SID: {message.sid})."
    except Exception as exc:
        return f"WhatsApp notification failed: {exc}"
