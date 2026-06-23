# Visiting Card Digitization & Voice Notes Orchestrator

A full-stack AI application that digitizes visiting cards through a chat interface, orchestrates extraction, deduplication, storage, and notifications via a **single LangGraph agent**, and supports voice note transcription linked to contacts.

## Architecture

```mermaid
flowchart TD
    UI[React Chat UI] --> API[FastAPI Backend]
    API --> Agent[LangGraph Agent]
    Agent --> Gemini[Gemini 2.5 Flash Vision/LLM]
    Agent --> Whisper[Whisper STT]
    Agent --> Sheets[Google Sheets]
    Agent --> Mongo[(MongoDB Atlas)]
    Agent --> WhatsApp[Twilio WhatsApp]
```

### LangGraph Agent Flow

**Card Flow:**
```
START → Upload Card → Extract (Gemini) → Duplicate Check
  ├─ Duplicate → END
  └─ Unique → Human Confirmation (interrupt) → Google Sheets → MongoDB → WhatsApp → END
```

**Voice Flow:**
```
START → Upload Audio → Find Contact by Session → Transcribe (Whisper)
  → Update Google Sheet → Update MongoDB → END
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite |
| Backend | FastAPI, Python 3.11 |
| Orchestration | LangGraph |
| Database | MongoDB Atlas |
| Storage | Google Sheets API |
| Vision/LLM | Gemini 2.5 Flash |
| Speech-to-Text | faster-whisper (Whisper tiny model) |
| Notifications | Twilio WhatsApp Sandbox |
| Deployment | Docker, Docker Compose, Render |

## Project Structure

```
Krid.AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── config.py                   # Environment & application settings
│   │   │
│   │   ├── api/
│   │   │   └── routes.py               # REST API endpoints
│   │   │
│   │   ├── agent/
│   │   │   ├── graph.py                # LangGraph workflow definition
│   │   │   ├── nodes.py                # Agent workflow nodes
│   │   │   └── state.py                # Shared workflow state
│   │   │
│   │   ├── services/                   # External integrations
│   │   │   ├── gemini_service.py
│   │   │   ├── whisper_service.py
│   │   │   ├── sheets_service.py
│   │   │   └── whatsapp_service.py
│   │   │
│   │   ├── models/                     # MongoDB models & database layer
│   │   ├── schemas/                    # Pydantic request/response schemas
│   │   └── utils/                      # Helper utilities
│   │
│   ├── uploads/
│   │   ├── cards/                      # Uploaded visiting cards
│   │   └── audio/                      # Uploaded voice notes
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── README.md
│   │
│   └── src/
│       ├── App.jsx                     # Root component
│       ├── main.jsx                    # React entry point
│       ├── index.css                   # Global styles
│       │
│       ├── context/
│       │   └── ThemeContext.jsx        # Light/Dark mode management
│       │
│       ├── services/
│       │   └── api.js                  # Backend API client
│       │
│       ├── pages/
│       │   └── ChatPage.jsx            # Main application page
│       │
│       └── components/
│           │
│           ├── layout/
│           │   ├── ChatSidebar.jsx     # Chat history sidebar
│           │   ├── ChatWindow.jsx      # Main chat container
│           │   └── Header.jsx          # Application header
│           │
│           ├── chat/
│           │   ├── EmptyState.jsx      # Welcome screen
│           │   ├── MessageBubble.jsx   # User/AI messages
│           │   └── TypingIndicator.jsx # Loading animation
│           │
│           ├── contact/
│           │   └── ContactPreview.jsx  # Extracted contact preview
│           │
│           ├── upload/
│           │   └── UploadControls.jsx  # Card & audio upload controls
│           │
│           └── ui/
│               ├── Modal.jsx           # Reusable modal component
│               └── Toast.jsx           # Notifications
│
├── docker-compose.yml
├── render.yaml
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (M0 free tier)
- Google Cloud service account with Sheets API enabled
- Google Sheet with columns: Contact ID, Name, Phone, Email, Company, Designation, Audio URL, Voice Transcript, Created At
- Gemini API key
- Twilio account with WhatsApp Sandbox (optional for notifications)
- ffmpeg (for Whisper audio processing)

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in values:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google AI Studio API key |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB_NAME` | Database name (default: `visiting_cards`) |
| `GOOGLE_SHEET_ID` | Spreadsheet ID from Google Sheets URL |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON string OR path to service account file |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | e.g. `whatsapp:+14155238886` |
| `MANAGER_PHONE_NUMBER` | e.g. `whatsapp:+91XXXXXXXXXX` |
| `BACKEND_URL` | Public backend URL (for audio file links) |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |

For frontend, copy `frontend/.env.example` to `frontend/.env`:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (e.g. `http://localhost:8000`) |

---

## MongoDB Atlas Setup Guide

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free M0 cluster.
2. Create a database user with read/write permissions.
3. Add your IP address to **Network Access** (or `0.0.0.0/0` for development).
4. Click **Connect** → **Drivers** → copy the connection string.
5. Replace `<password>` with your user password and set the database name:

```
mongodb+srv://user:password@cluster.mongodb.net/visiting_cards?retryWrites=true&w=majority
```

6. Set `MONGODB_URI` in `backend/.env`.

Collections are created automatically:
- `contacts` — stored contact records
- `sessions` — chat sessions and message history

---

## Google Sheets Integration Guide

1. Create a new Google Sheet with header row:

   | Contact ID | Name | Phone | Email | Company | Designation | Audio URL | Voice Transcript | Created At |

2. Enable **Google Sheets API** in [Google Cloud Console](https://console.cloud.google.com/).
3. Create a **Service Account** and download the JSON key file.
4. Share the Google Sheet with the service account email (Editor access).
5. Copy the Spreadsheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
6. Set in `.env`:
   - `GOOGLE_SHEET_ID=SPREADSHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT_JSON=` paste full JSON or file path

**Deduplication logic:** Matches on phone, email, or name+company combination across both Google Sheets and MongoDB.

---

## Twilio WhatsApp Integration Guide

1. Sign up at [Twilio](https://www.twilio.com/).
2. Go to **Messaging** → **Try it out** → **Send a WhatsApp message**.
3. Join the WhatsApp Sandbox by sending the join code to the sandbox number.
4. Set environment variables:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   MANAGER_PHONE_NUMBER=whatsapp:+91XXXXXXXXXX
   ```
5. The manager number must also join the sandbox during testing.

**Message format sent on new contact:**
```
New Visiting Card Added

Name: John Doe
Company: Acme Corp
Phone: +1 555-0100
Email: john@acme.com
```

---

## Local Development

### Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env

npm run dev
```

Open http://localhost:5173

---

## Docker

```bash
# From project root
cp backend/.env.example backend/.env
# Edit backend/.env

docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Health check: http://localhost:8000/health

---

## Render Deployment Guide

1. Push the repository to GitHub.
2. Create a [Render](https://render.com) account.
3. Click **New** → **Blueprint** and connect your repo (uses `render.yaml`).
4. Or deploy services manually:
   - **Backend**: Web Service → Docker → `backend/Dockerfile`
   - **Frontend**: Web Service → Docker → `frontend/Dockerfile`
5. Set all environment variables in the Render dashboard for the backend service.
6. Set `VITE_API_URL` on frontend build to your backend Render URL.
7. Set `BACKEND_URL` on backend to its public Render URL.
8. Update `CORS_ORIGINS` to include your frontend Render URL.

**Note:** Render free tier has ephemeral filesystem — uploaded files may not persist across restarts. For production, use cloud storage (S3/GCS).

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create new chat session |
| GET | `/api/sessions` | List all sessions |
| GET | `/api/session/{session_id}` | Get session with messages |
| POST | `/api/card/upload` | Upload visiting card image |
| POST | `/api/confirm` | Confirm/reject extracted details |
| POST | `/api/audio/upload` | Upload voice note |
| GET | `/api/contact/{id}` | Get contact by ID |
| GET | `/health` | Health check |

---

## Usage Flow

1. **Start a chat** — Click "New Chat" in the sidebar.
2. **Upload visiting card** — Click the image icon and select a card photo.
3. **Review extraction** — Agent extracts name, phone, email, company, etc.
4. **Confirm details** — Click "Confirm & Save" (human-in-the-loop).
5. **Automatic actions** — Contact saved to Google Sheets + MongoDB, WhatsApp sent.
6. **Add voice note** — Click the mic icon and upload an audio file.
7. **Transcription** — Whisper transcribes audio and updates the contact record.

---

## Bonus Features Implemented

- **Human-in-the-loop confirmation** — LangGraph interrupt after extraction
- **Company enrichment** — Gemini suggests website and LinkedIn profile
- **Conversation memory** — Session messages persisted in MongoDB

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MongoDB connection failed | Check URI, IP whitelist, credentials |
| Google Sheets permission denied | Share sheet with service account email |
| WhatsApp not sending | Verify sandbox join, phone number format |
| Whisper slow on first run | Downloads model on first transcription |
| CORS errors | Add frontend URL to `CORS_ORIGINS` |
| Gemini model not found | Fallback to `gemini-2.0-flash` if 2.5 unavailable |

---

