"""Chat session and message persistence for conversation memory."""

from typing import Any, Optional

from app.models.database import get_database
from app.utils.helpers import generate_session_id, utc_now_iso


class SessionService:
    async def create_session(self, title: str = "New Chat") -> dict[str, Any]:
        db = get_database()
        session_id = generate_session_id()
        now = utc_now_iso()
        document = {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "contact_id": None,
            "card_data": None,
            "awaiting_confirmation": False,
            "messages": [],
            "graph_state": {},
        }
        await db.sessions.insert_one(document)
        return document

    async def list_sessions(self) -> list[dict[str, Any]]:
        db = get_database()
        cursor = db.sessions.find({}, {"_id": 0, "messages": 0, "graph_state": 0}).sort(
            "updated_at", -1
        )
        return await cursor.to_list(length=100)

    async def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        db = get_database()
        return await db.sessions.find_one({"session_id": session_id}, {"_id": 0})

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        db = get_database()
        message = {
            "role": role,
            "content": content,
            "timestamp": utc_now_iso(),
            "metadata": metadata or {},
        }
        await db.sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": utc_now_iso()},
            },
        )

    async def update_session(self, session_id: str, updates: dict[str, Any]) -> None:
        db = get_database()
        updates["updated_at"] = utc_now_iso()
        await db.sessions.update_one({"session_id": session_id}, {"$set": updates})

    async def save_graph_state(self, session_id: str, state: dict[str, Any]) -> None:
        await self.update_session(session_id, {"graph_state": state})


session_service = SessionService()
