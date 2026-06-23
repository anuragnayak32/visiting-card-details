import { useEffect, useRef } from "react";
import { Bot, User, AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";
import ContactPreview from "../contact/ContactPreview.jsx";

const STATUS_ICONS = {
  success: <CheckCircle size={13} />,
  error: <AlertCircle size={13} />,
  warning: <AlertTriangle size={13} />,
};

export default function MessageBubble({
  message,
  cardData,
  awaitingConfirmation,
  onConfirm,
  onReject,
  confirmLoading,
}) {
  const isUser = message.role === "user";
  const ref = useRef(null);

  useEffect(() => {
    ref.current?.classList.add("msg-enter");
  }, []);

  return (
    <div ref={ref} className={`message-row ${isUser ? "message-user" : "message-assistant"}`}>
      {!isUser && (
        <div className="avatar avatar-ai">
          <Bot size={16} />
        </div>
      )}

      <div className={`bubble ${isUser ? "bubble-user" : "bubble-ai"}`}>
        <p className="bubble-text">{message.content}</p>

        {!isUser && awaitingConfirmation && cardData && (
          <ContactPreview
            cardData={cardData}
            onConfirm={onConfirm}
            onReject={onReject}
            loading={confirmLoading}
          />
        )}

        {message.metadata?.status && (
          <div className={`status-pill status-${message.metadata.status}`}>
            {STATUS_ICONS[message.metadata.status]}
            <span>{message.metadata.label}</span>
          </div>
        )}
      </div>

      {isUser && (
        <div className="avatar avatar-user">
          <User size={16} />
        </div>
      )}
    </div>
  );
}
