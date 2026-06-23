const API_BASE = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  createSession: () => request("/api/sessions", { method: "POST" }),
  listSessions: () => request("/api/sessions"),
  getSession: (sessionId) => request(`/api/session/${sessionId}`),
  uploadCard: (sessionId, file) => {
    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("file", file);
    return request("/api/card/upload", { method: "POST", body: formData });
  },
  uploadAudio: (sessionId, file) => {
    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("file", file);
    return request("/api/audio/upload", { method: "POST", body: formData });
  },
  confirmContact: (sessionId, confirmed, cardData = null) =>
    request("/api/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        confirmed,
        card_data: cardData,
      }),
    }),
  getContact: (contactId) => request(`/api/contact/${contactId}`),
};
