"""MongoDB contact persistence service."""

from typing import Any, Optional

from app.models.database import get_database
from app.utils.helpers import generate_contact_id, normalize_email, normalize_phone, utc_now_iso


class ContactService:
    async def find_duplicate(self, card_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        db = get_database()
        phone = normalize_phone(card_data.get("phone"))
        email = normalize_email(card_data.get("email"))
        name = (card_data.get("name") or "").strip().lower()
        company = (card_data.get("company") or "").strip().lower()

        query_conditions = []
        if phone:
            query_conditions.append({"phone_normalized": phone})
        if email:
            query_conditions.append({"email_normalized": email})
        if name and company:
            query_conditions.append({"name_lower": name, "company_lower": company})

        if not query_conditions:
            return None

        return await db.contacts.find_one({"$or": query_conditions})

    async def create_contact(self, contact: dict[str, Any]) -> dict[str, Any]:
        db = get_database()
        contact_id = contact.get("contact_id") or generate_contact_id()
        document = {
            "contact_id": contact_id,
            "session_id": contact.get("session_id", ""),
            "name": contact.get("name", ""),
            "phone": contact.get("phone", ""),
            "email": contact.get("email", ""),
            "company": contact.get("company", ""),
            "designation": contact.get("designation", ""),
            "website": contact.get("website", ""),
            "address": contact.get("address", ""),
            "linkedin": contact.get("linkedin", ""),
            "phone_normalized": normalize_phone(contact.get("phone")),
            "email_normalized": normalize_email(contact.get("email")),
            "name_lower": (contact.get("name") or "").strip().lower(),
            "company_lower": (contact.get("company") or "").strip().lower(),
            "audio_url": contact.get("audio_url", ""),
            "transcript": contact.get("transcript", ""),
            "created_at": contact.get("created_at") or utc_now_iso(),
        }
        await db.contacts.insert_one(document)
        return document

    async def get_by_contact_id(self, contact_id: str) -> Optional[dict[str, Any]]:
        db = get_database()
        return await db.contacts.find_one({"contact_id": contact_id}, {"_id": 0})

    async def get_by_session_id(self, session_id: str) -> Optional[dict[str, Any]]:
        db = get_database()
        return await db.contacts.find_one({"session_id": session_id}, {"_id": 0})

    async def update_contact(self, contact_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        db = get_database()
        if "phone" in updates:
            updates["phone_normalized"] = normalize_phone(updates["phone"])
        if "email" in updates:
            updates["email_normalized"] = normalize_email(updates["email"])
        if "name" in updates:
            updates["name_lower"] = (updates["name"] or "").strip().lower()
        if "company" in updates:
            updates["company_lower"] = (updates["company"] or "").strip().lower()

        await db.contacts.update_one({"contact_id": contact_id}, {"$set": updates})
        return await self.get_by_contact_id(contact_id)


contact_service = ContactService()
