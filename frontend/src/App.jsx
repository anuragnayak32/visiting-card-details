import { useCallback, useEffect, useState } from "react";
import ChatSidebar from "./components/ChatSidebar";
import ChatWindow from "./components/ChatWindow";
import { api } from "./services/api";

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [title, setTitle] = useState("New Chat");
  const [cardData, setCardData] = useState(null);
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);

  const loadSessions = useCallback(async () => {
    try {
      const data = await api.listSessions();
      setSessions(data);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  }, []);

  const loadSession = useCallback(async (sessionId) => {
    try {
      const session = await api.getSession(sessionId);
      setActiveSessionId(sessionId);
      setMessages(session.messages || []);
      setTitle(session.title || "New Chat");
      setCardData(session.card_data || null);
      setAwaitingConfirmation(session.awaiting_confirmation || false);
    } catch (err) {
      console.error("Failed to load session:", err);
    }
  }, []);

  const handleNewChat = async () => {
    try {
      const session = await api.createSession();
      await loadSessions();
      await loadSession(session.session_id);
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  };

  useEffect(() => {
    loadSessions();
    handleNewChat();
  }, []);

  const handleImageUpload = async (file) => {
    if (!activeSessionId) return;
    setLoading(true);
    try {
      const result = await api.uploadCard(activeSessionId, file);
      await loadSession(activeSessionId);
      setCardData(result.card_data);
      setAwaitingConfirmation(result.awaiting_confirmation);

      if (result.duplicate) {
        setAwaitingConfirmation(false);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.message}`,
          timestamp: new Date().toISOString(),
          metadata: { status: "error", label: "Upload Failed" },
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (file) => {
    if (!activeSessionId) return;
    setLoading(true);
    try {
      await api.uploadAudio(activeSessionId, file);
      await loadSession(activeSessionId);
      setAwaitingConfirmation(false);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.message}`,
          timestamp: new Date().toISOString(),
          metadata: { status: "error", label: "Upload Failed" },
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!activeSessionId) return;
    setConfirmLoading(true);
    try {
      await api.confirmContact(activeSessionId, true, cardData);
      await loadSession(activeSessionId);
      setAwaitingConfirmation(false);
      await loadSessions();
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error saving contact: ${err.message}`,
          timestamp: new Date().toISOString(),
          metadata: { status: "error", label: "Save Failed" },
        },
      ]);
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleReject = async () => {
    if (!activeSessionId) return;
    setConfirmLoading(true);
    try {
      await api.confirmContact(activeSessionId, false);
      await loadSession(activeSessionId);
      setCardData(null);
      setAwaitingConfirmation(false);
    } catch (err) {
      console.error("Failed to reject:", err);
    } finally {
      setConfirmLoading(false);
    }
  };

  return (
    <div className="app">
      <ChatSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={loadSession}
        onNewChat={handleNewChat}
      />
      <ChatWindow
        title={title}
        messages={messages}
        cardData={cardData}
        awaitingConfirmation={awaitingConfirmation}
        loading={loading}
        onImageUpload={handleImageUpload}
        onAudioUpload={handleAudioUpload}
        onConfirm={handleConfirm}
        onReject={handleReject}
        confirmLoading={confirmLoading}
      />
    </div>
  );
}
