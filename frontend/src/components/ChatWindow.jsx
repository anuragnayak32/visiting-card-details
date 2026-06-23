import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import UploadControls from "./UploadControls";

export default function ChatWindow({
  title,
  messages,
  cardData,
  awaitingConfirmation,
  loading,
  onImageUpload,
  onAudioUpload,
  onConfirm,
  onReject,
  confirmLoading,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="main-content">
      <header className="chat-header">{title || "Visiting Card Orchestrator"}</header>

      <div className="messages-container">
        {messages.length === 0 && !loading ? (
          <div className="empty-state">
            <h2>Visiting Card Digitization</h2>
            <p>
              Upload a visiting card image to extract contact details. After saving,
              upload a voice note to attach a transcript to the same contact.
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble
              key={`${msg.timestamp}-${index}`}
              message={msg}
              cardData={
                index === messages.length - 1 && msg.role === "assistant"
                  ? cardData
                  : null
              }
              awaitingConfirmation={
                index === messages.length - 1 &&
                msg.role === "assistant" &&
                awaitingConfirmation
              }
              onConfirm={onConfirm}
              onReject={onReject}
              confirmLoading={confirmLoading}
            />
          ))
        )}

        {loading && (
          <div className="message assistant">
            <div className="message-avatar">AI</div>
            <div className="message-content">
              <div className="loading-dots">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <div className="input-wrapper">
          <UploadControls
            onImageUpload={onImageUpload}
            onAudioUpload={onAudioUpload}
            disabled={loading || confirmLoading}
          />
          <span style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Upload a visiting card image or voice note to get started
          </span>
        </div>
      </div>
    </div>
  );
}
