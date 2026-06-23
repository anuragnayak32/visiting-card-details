import { useState, useRef, useEffect } from "react";
import {
  Plus,
  Search,
  MessageSquare,
  MoreHorizontal,
  Pencil,
  Trash2,
  Check,
  X,
  Menu,
} from "lucide-react";
import Modal from "../ui/Modal.jsx";

function SessionItem({ session, isActive, onSelect, onRename, onDelete }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [renameVal, setRenameVal] = useState(session.title || "New Chat");
  const menuRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (renaming) inputRef.current?.focus();
  }, [renaming]);

  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const submitRename = () => {
    if (renameVal.trim()) onRename(session.session_id, renameVal.trim());
    setRenaming(false);
    setMenuOpen(false);
  };

  const fmt = (iso) => {
    if (!iso) return "";
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000) return "just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  };

  return (
    <div className={`session-item ${isActive ? "active" : ""}`}>
      <button className="session-main" onClick={() => onSelect(session.session_id)}>
        <MessageSquare size={14} className="session-icon" />
        <div className="session-info">
          {renaming ? (
            <input
              ref={inputRef}
              className="rename-input"
              value={renameVal}
              onChange={(e) => setRenameVal(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submitRename();
                if (e.key === "Escape") setRenaming(false);
              }}
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <span className="session-title">{session.title || "New Chat"}</span>
          )}
          <span className="session-time">{fmt(session.updated_at || session.created_at)}</span>
        </div>
      </button>

      {renaming ? (
        <div className="rename-actions">
          <button className="icon-btn accent" onClick={submitRename}><Check size={13} /></button>
          <button className="icon-btn" onClick={() => setRenaming(false)}><X size={13} /></button>
        </div>
      ) : (
        <div className="session-menu-wrap" ref={menuRef}>
          <button
            className="session-menu-btn"
            onClick={(e) => { e.stopPropagation(); setMenuOpen((o) => !o); }}
          >
            <MoreHorizontal size={15} />
          </button>
          {menuOpen && (
            <div className="dropdown-menu">
              <button
                className="dropdown-item"
                onClick={(e) => {
                  e.stopPropagation();
                  setRenaming(true);
                  setMenuOpen(false);
                }}
              >
                <Pencil size={13} /> Rename
              </button>
              <button
                className="dropdown-item danger"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(session.session_id, session.title || "New Chat");
                  setMenuOpen(false);
                }}
              >
                <Trash2 size={13} /> Delete
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ChatSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onRenameSession,
  onDeleteSession,
  mobileOpen,
  onCloseMobile,
}) {
  const [search, setSearch] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);

  const filtered = sessions.filter((s) =>
    (s.title || "New Chat").toLowerCase().includes(search.toLowerCase())
  );

  const handleDeleteRequest = (id, title) => setDeleteTarget({ id, title });

  const confirmDelete = () => {
    if (deleteTarget) {
      onDeleteSession(deleteTarget.id);
      setDeleteTarget(null);
    }
  };

  return (
    <>
      {mobileOpen && <div className="sidebar-overlay" onClick={onCloseMobile} />}
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="brand-icon">VC</div>
            <span className="brand-name">Card AI</span>
          </div>
          <button className="new-chat-btn" onClick={onNewChat}>
            <Plus size={16} />
            New Chat
          </button>
        </div>

        <div className="sidebar-search">
          <Search size={14} />
          <input
            placeholder="Search chats..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="sessions-list">
          {filtered.length === 0 ? (
            <p className="sessions-empty">No chats found</p>
          ) : (
            filtered.map((s) => (
              <SessionItem
                key={s.session_id}
                session={s}
                isActive={s.session_id === activeSessionId}
                onSelect={(id) => { onSelectSession(id); onCloseMobile?.(); }}
                onRename={onRenameSession}
                onDelete={handleDeleteRequest}
              />
            ))
          )}
        </div>
      </aside>

      <Modal
        open={!!deleteTarget}
        title="Delete Chat"
        onClose={() => setDeleteTarget(null)}
      >
        <div className="modal-body">
          <p>Delete <strong>"{deleteTarget?.title}"</strong>? This cannot be undone.</p>
          <div className="modal-actions">
            <button className="btn-ghost" onClick={() => setDeleteTarget(null)}>Cancel</button>
            <button className="btn-danger" onClick={confirmDelete}>Delete</button>
          </div>
        </div>
      </Modal>
    </>
  );
}
