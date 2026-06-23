"""Google Sheets integration for contact storage and deduplication."""

print("LOADED SHEETS_SERVICE.PY")

from typing import Any, Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.config import get_settings
from app.utils.helpers import normalize_email, normalize_phone

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = [
    "Contact ID",
    "Name",
    "Phone",
    "Email",
    "Company",
    "Designation",
    "Audio URL",
    "Voice Transcript",
    "Created At",
]


class GoogleSheetsService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._service = None
        self._memory_rows: list[list[str]] = []

    def _get_service(self):
        print("GOOGLE_SHEET_ID =", self.settings.google_sheet_id)

        if self._service is not None:
            print("Using existing service")
            return self._service

        credentials_data = self.settings.google_credentials

        print("Credentials loaded:", bool(credentials_data))

        if not credentials_data or not self.settings.google_sheet_id:
            print("SERVICE IS NONE")
            return None

        print("CREATING GOOGLE SHEETS SERVICE")    

        credentials = Credentials.from_service_account_info(credentials_data, scopes=SCOPES)
        self._service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        return self._service

    async def ensure_headers(self) -> None:
        service = self._get_service()
        print("Spreadsheet ID:", self.settings.google_sheet_id)
        if not service:
            if not self._memory_rows:
                self._memory_rows = [HEADERS.copy()]
            return

        sheet_id = self.settings.google_sheet_id
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range="A1:I1")
            .execute()
        )
        values = result.get("values", [])
        if not values:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range="A1:I1",
                valueInputOption="RAW",
                body={"values": [HEADERS]},
            ).execute()

    async def get_all_contacts(self) -> list[dict[str, str]]:
        await self.ensure_headers()
        service = self._get_service()
        if not service:
            rows = self._memory_rows[1:] if len(self._memory_rows) > 1 else []
        else:
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=self.settings.google_sheet_id, range="A2:I1000")
                .execute()
            )
            rows = result.get("values", [])

        contacts = []
        for row in rows:
            padded = row + [""] * (len(HEADERS) - len(row))
            contacts.append(
                {
                    "contact_id": padded[0],
                    "name": padded[1],
                    "phone": padded[2],
                    "email": padded[3],
                    "company": padded[4],
                    "designation": padded[5],
                    "audio_url": padded[6],
                    "transcript": padded[7],
                    "created_at": padded[8],
                }
            )
        return contacts

    async def find_duplicate(self, card_data: dict[str, Any]) -> Optional[dict[str, str]]:
        phone = normalize_phone(card_data.get("phone"))
        email = normalize_email(card_data.get("email"))
        name = (card_data.get("name") or "").strip().lower()
        company = (card_data.get("company") or "").strip().lower()

        for contact in await self.get_all_contacts():
            if phone and normalize_phone(contact.get("phone")) == phone:
                return contact
            if email and normalize_email(contact.get("email")) == email:
                return contact
            if name and company:
                if (
                    contact.get("name", "").strip().lower() == name
                    and contact.get("company", "").strip().lower() == company
                ):
                    return contact
        return None

    async def insert_contact(self, contact: dict[str, Any]) -> None:
        await self.ensure_headers()
        row = [
            contact.get("contact_id", ""),
            contact.get("name", ""),
            contact.get("phone", ""),
            contact.get("email", ""),
            contact.get("company", ""),
            contact.get("designation", ""),
            contact.get("audio_url", ""),
            contact.get("transcript", ""),
            contact.get("created_at", ""),
        ]

        service = self._get_service()
        if not service:
            self._memory_rows.append(row)
            return
        
        print("Writing row:", row)

        result = service.spreadsheets().values().append(
            spreadsheetId=self.settings.google_sheet_id,
            range="A:I",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute()
        print("Google API Result:", result)

    async def update_contact(self, contact_id: str, updates: dict[str, Any]) -> bool:
        contacts = await self.get_all_contacts()
        row_index = None
        for idx, contact in enumerate(contacts):
            if contact.get("contact_id") == contact_id:
                row_index = idx + 2
                break

        if row_index is None:
            return False

        merged = {**contacts[row_index - 2], **updates}
        row = [
            merged.get("contact_id", ""),
            merged.get("name", ""),
            merged.get("phone", ""),
            merged.get("email", ""),
            merged.get("company", ""),
            merged.get("designation", ""),
            merged.get("audio_url", ""),
            merged.get("transcript", ""),
            merged.get("created_at", ""),
        ]

        service = self._get_service()
        if not service:
            self._memory_rows[row_index - 1] = row
            return True

        service.spreadsheets().values().update(
            spreadsheetId=self.settings.google_sheet_id,
            range=f"A{row_index}:I{row_index}",
            valueInputOption="RAW",
            body={"values": [row]},
        ).execute()
        return True


sheets_service = GoogleSheetsService()
