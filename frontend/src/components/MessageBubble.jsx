import ContactPreview from "./ContactPreview";

export default function MessageBubble({
  message,
  cardData,
  awaitingConfirmation,
  onConfirm,
  onReject,
  confirmLoading,
}) {
  const isUser = message.role === "user";

  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      <div className="message-avatar">{isUser ? "U" : "AI"}</div>
      <div className="message-content">
        {message.content}
        {!isUser && awaitingConfirmation && cardData && (
          <ContactPreview
            cardData={cardData}
            onConfirm={onConfirm}
            onReject={onReject}
            loading={confirmLoading}
          />
        )}
        {message.metadata?.status && (
          <span className={`status-badge ${message.metadata.status}`}>
            {message.metadata.label}
          </span>
        )}
      </div>
    </div>
  );
}
