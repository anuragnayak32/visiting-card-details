"""Pydantic request/response schemas."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class CardData(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    designation: str = ""
    website: str = ""
    address: str = ""
    linkedin: str = ""


class CardUploadResponse(BaseModel):
    session_id: str
    message: str
    card_data: Optional[CardData] = None
    duplicate: bool = False
    awaiting_confirmation: bool = False
    contact_id: Optional[str] = None


class AudioUploadResponse(BaseModel):
    session_id: str
    message: str
    contact_id: Optional[str] = None
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


class ConfirmRequest(BaseModel):
    session_id: str
    confirmed: bool = True
    card_data: Optional[CardData] = None


class ConfirmResponse(BaseModel):
    session_id: str
    message: str
    contact_id: Optional[str] = None
    success: bool = True


class ContactResponse(BaseModel):
    contact_id: str
    session_id: str
    name: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    designation: str = ""
    website: str = ""
    address: str = ""
    linkedin: str = ""
    audio_url: str = ""
    transcript: str = ""
    created_at: str = ""


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionCreateResponse(BaseModel):
    session_id: str
    title: str = "New Chat"


class SessionSummary(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
    contact_id: Optional[str] = None


class SessionDetail(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
    contact_id: Optional[str] = None
    messages: list[ChatMessage] = Field(default_factory=list)
    card_data: Optional[CardData] = None
    awaiting_confirmation: bool = False
