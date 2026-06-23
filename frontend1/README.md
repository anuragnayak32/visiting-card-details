# Visiting Card AI — Frontend

Modern SaaS-style React frontend for the Visiting Card Digitisation system.

---

## Setup

```bash
# 1. Install dependencies (no extra libraries needed beyond lucide-react)
npm install

# 2. Create environment file
cp .env.example .env
# Edit .env → set VITE_API_URL to your FastAPI backend URL

# 3. Start development server
npm run dev

# 4. Build for production
npm run build
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

---

## Folder Structure

```
src/
├── components/
│   ├── chat/
│   │   ├── EmptyState.jsx        — Empty chat placeholder with hints
│   │   ├── MessageBubble.jsx     — Individual message (left/right aligned)
│   │   └── TypingIndicator.jsx   — Animated dots while AI is processing
│   │
│   ├── contact/
│   │   └── ContactPreview.jsx    — Extracted card details with Edit/Confirm/Reject
│   │
│   ├── layout/
│   │   ├── ChatSidebar.jsx       — Left sidebar with search, rename, delete
│   │   ├── ChatWindow.jsx        — Main chat area with header + messages + input
│   │   └── Header.jsx            — Top bar with title + dark/light toggle
│   │
│   ├── ui/
│   │   ├── Modal.jsx             — Reusable confirmation modal
│   │   └── Toast.jsx             — Toast notification system (no extra library)
│   │
│   └── upload/
│       └── UploadControls.jsx    — Drag-and-drop upload zones (card + voice)
│
├── context/
│   └── ThemeContext.jsx          — Dark/light theme with localStorage persistence
│
├── pages/
│   └── ChatPage.jsx              — Re-export of App (routing compatibility)
│
├── services/
│   └── api.js                    — All API calls (unchanged from original)
│
├── App.jsx                       — Root component with all state management
├── main.jsx                      — React DOM entry point
└── index.css                     — Complete design system (CSS variables + components)
```

---

## Features

| Feature | Status |
|---|---|
| Dark / Light mode with localStorage | ✅ |
| ChatGPT-style left sidebar | ✅ |
| Search chats | ✅ |
| Rename chat (inline) | ✅ |
| Delete chat (confirmation modal) | ✅ |
| User messages on RIGHT | ✅ |
| AI messages on LEFT | ✅ |
| Animated message appearance | ✅ |
| Typing indicator with contextual label | ✅ |
| Drag-and-drop upload zones | ✅ |
| Professional contact preview card | ✅ |
| Inline field editing before confirm | ✅ |
| Toast notifications (built-in, no library) | ✅ |
| Loading states with descriptive labels | ✅ |
| Mobile responsive + hamburger drawer | ✅ |
| All original API integrations preserved | ✅ |

---

## API Notes

`api.js` adds two optional endpoints that improve UX:

- `DELETE /api/session/:id` — delete a chat session
- `PATCH /api/session/:id` — rename a chat session `{ title: "..." }`

If your backend doesn't implement these yet, the frontend **degrades gracefully** — deletions are reflected locally and renames update local state without crashing.

---

## Theme

The design uses **CSS custom properties** only — no Tailwind, no extra CSS-in-JS. Both themes live in `index.css` under `[data-theme="dark"]` and `[data-theme="light"]` selectors. The `ThemeContext` sets the attribute on `<html>` and persists the choice to `localStorage`.
