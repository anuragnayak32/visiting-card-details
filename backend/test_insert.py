from app.services.sheets_service import sheets_service
import asyncio

async def main():
    await sheets_service.insert_contact({
        "contact_id": "TEST123",
        "name": "Anurag Test",
        "phone": "9999999999",
        "email": "test@test.com",
        "company": "KridAI",
        "designation": "Developer",
        "audio_url": "",
        "transcript": "",
        "created_at": "2026-06-22"
    })

    print("Inserted!")

asyncio.run(main())