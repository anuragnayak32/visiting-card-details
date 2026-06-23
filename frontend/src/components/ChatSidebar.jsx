import { Plus } from "lucide-react";

export default function ChatSidebar({ sessions, activeSessionId, onSelectSession, onNewChat }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewChat}>
          <Plus size={18} />
          New Chat
        </button>
      </div>
      <div className="sessions-list">
        {sessions.map((session) => (
          <button
            key={session.session_id}
            className={`session-item ${session.session_id === activeSessionId ? "active" : ""}`}
            onClick={() => onSelectSession(session.session_id)}
          >
            {session.title || "New Chat"}
          </button>
        ))}
      </div>
    </aside>
  );
}
