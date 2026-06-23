"""LangGraph agent state definition."""

from typing import Any, Literal, Optional, TypedDict


class AgentState(TypedDict, total=False):
    session_id: str
    flow_type: Literal["card", "voice"]
    card_image_path: str
    card_data: dict[str, Any]
    contact_id: str
    audio_path: str
    audio_url: str
    transcript: str
    duplicate: bool
    duplicate_source: str
    awaiting_confirmation: bool
    user_confirmed: bool
    message: str
    messages: list[dict[str, str]]
    enrichment: dict[str, str]
