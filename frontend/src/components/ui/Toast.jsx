import { useEffect, useState } from "react";
import { CheckCircle, XCircle, AlertTriangle, Info, X } from "lucide-react";

const ICONS = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

function Toast({ id, type = "info", message, onRemove }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    requestAnimationFrame(() => setVisible(true));
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => onRemove(id), 300);
    }, 4000);
    return () => clearTimeout(timer);
  }, [id, onRemove]);

  const Icon = ICONS[type];

  const colors = {
    success: "toast-success",
    error: "toast-error",
    warning: "toast-warning",
    info: "toast-info",
  };

  return (
    <div className={`toast ${colors[type]} ${visible ? "toast-visible" : ""}`}>
      <Icon size={16} />
      <span>{message}</span>
      <button
        className="toast-close"
        onClick={() => {
          setVisible(false);
          setTimeout(() => onRemove(id), 300);
        }}
      >
        <X size={14} />
      </button>
    </div>
  );
}

let _addToast = null;

export function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  _addToast = (type, message) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, type, message }]);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <Toast key={t.id} {...t} onRemove={removeToast} />
      ))}
    </div>
  );
}

export const toast = {
  success: (msg) => _addToast?.("success", msg),
  error: (msg) => _addToast?.("error", msg),
  warning: (msg) => _addToast?.("warning", msg),
  info: (msg) => _addToast?.("info", msg),
};
