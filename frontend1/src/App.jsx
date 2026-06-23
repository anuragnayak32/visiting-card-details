import { useCallback, useEffect, useState } from "react";
import ChatSidebar from "./components/layout/ChatSidebar";
import ChatWindow from "./components/layout/ChatWindow";
import { ToastContainer, toast } from "./components/ui/Toast";
import { ThemeProvider } from "./context/ThemeContext";
import { api } from "./services/api";

function AppInner() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [title, setTitle] = useState("New Chat");
  const [cardData, setCardData] = useState(null);
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingType, setLoadingType] = useState(null);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const loadSessions = useCallback(async () => {
    try {
      const data = await api.listSessions();
      setSessions(data);
    } catch {
      toast.error("Failed to load sessions");
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
    } catch {
      toast.error("Failed to load chat");
    }
  }, []);

  const handleNewChat = async () => {
    try {
      const session = await api.createSession();
      await loadSessions();
      await loadSession(session.session_id);
    } catch {
      toast.error("Failed to create new chat");
    }
  };

  useEffect(() => {
    loadSessions();
    handleNewChat();
  }, []);

  const handleImageUpload = async (file) => {
    if (!activeSessionId) return;
    setLoading(true);
    setLoadingType("card");
    try {
      const result = await api.uploadCard(activeSessionId, file);
      await loadSession(activeSessionId);
      setCardData(result.card_data);
      setAwaitingConfirmation(result.awaiting_confirmation);
      if (result.duplicate) {
        setAwaitingConfirmation(false);
        toast.warning("Duplicate card detected");
      } else {
        toast.success("Card extracted successfully");
      }
    } catch (err) {
      toast.error(`Upload failed: ${err.message}`);
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
      setLoadingType(null);
    }
  };

  const handleAudioUpload = async (file) => {
    if (!activeSessionId) return;
    setLoading(true);
    setLoadingType("audio");
    try {
      await api.uploadAudio(activeSessionId, file);
      await loadSession(activeSessionId);
      setAwaitingConfirmation(false);
      toast.success("Voice note transcribed");
    } catch (err) {
      toast.error(`Audio upload failed: ${err.message}`);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.message}`,
          timestamp: new Date().toISOString(),
          metadata: { status: "error", label: "Audio Upload Failed" },
        },
      ]);
    } finally {
      setLoading(false);
      setLoadingType(null);
    }
  };

  const handleConfirm = async (editedData) => {
    if (!activeSessionId) return;
    setConfirmLoading(true);
    try {
      await api.confirmContact(activeSessionId, true, editedData || cardData);
      await loadSession(activeSessionId);
      setAwaitingConfirmation(false);
      await loadSessions();
      toast.success("Contact saved successfully");
    } catch (err) {
      toast.error(`Failed to save contact: ${err.message}`);
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
      toast.info("Contact rejected");
    } catch (err) {
      toast.error(`Error: ${err.message}`);
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleRenameSession = async (sessionId, newTitle) => {
    try {
      await api.renameSession(sessionId, newTitle);
      await loadSessions();
      if (sessionId === activeSessionId) setTitle(newTitle);
      toast.success("Chat renamed");
    } catch {
      // Gracefully update local state even if backend doesn't support rename
      setSessions((prev) =>
        prev.map((s) => (s.session_id === sessionId ? { ...s, title: newTitle } : s))
      );
      if (sessionId === activeSessionId) setTitle(newTitle);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await api.deleteSession(sessionId);
      await loadSessions();
      if (sessionId === activeSessionId) {
        const remaining = sessions.filter((s) => s.session_id !== sessionId);
        if (remaining.length > 0) {
          await loadSession(remaining[0].session_id);
        } else {
          await handleNewChat();
        }
      }
      toast.success("Chat deleted");
    } catch {
      // Remove locally if backend doesn't support delete
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      toast.warning("Deleted locally");
    }
  };

  return (
    <div className="app">
      <ToastContainer />
      <ChatSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={loadSession}
        onNewChat={handleNewChat}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        mobileOpen={sidebarOpen}
        onCloseMobile={() => setSidebarOpen(false)}
      />
      <ChatWindow
        title={title}
        messages={messages}
        cardData={cardData}
        awaitingConfirmation={awaitingConfirmation}
        loading={loading}
        loadingType={loadingType}
        onImageUpload={handleImageUpload}
        onAudioUpload={handleAudioUpload}
        onConfirm={handleConfirm}
        onReject={handleReject}
        confirmLoading={confirmLoading}
        onMenuToggle={() => setSidebarOpen((o) => !o)}
      />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppInner />
    </ThemeProvider>
  );
}
