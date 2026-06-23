import { useEffect, useRef } from "react";
import MessageBubble from "../chat/MessageBubble.jsx";
import TypingIndicator from "../chat/TypingIndicator.jsx";
import EmptyState from "../chat/EmptyState.jsx";
import UploadControls from "../upload/UploadControls.jsx";
import Header from "../layout/Header.jsx";

const LOADING_LABELS = {
  card: "🔄 Extracting card details…",
  audio: "🎤 Transcribing audio…",
  saving: "💾 Saving contact…",
};

export default function ChatWindow({
  title,
  messages,
  cardData,
  awaitingConfirmation,
  loading,
  loadingType,
  onImageUpload,
  onAudioUpload,
  onConfirm,
  onReject,
  confirmLoading,
  onMenuToggle,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="main-content">
      <Header title={title} onMenuToggle={onMenuToggle} />

      <div className="messages-container">
        {messages.length === 0 && !loading ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((msg, i) => (
              <MessageBubble
                key={`${msg.timestamp}-${i}`}
                message={msg}
                cardData={i === messages.length - 1 && msg.role === "assistant" ? cardData : null}
                awaitingConfirmation={
                  i === messages.length - 1 && msg.role === "assistant" && awaitingConfirmation
                }
                onConfirm={onConfirm}
                onReject={onReject}
                confirmLoading={confirmLoading}
              />
            ))}
            {loading && <TypingIndicator label={LOADING_LABELS[loadingType]} />}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <UploadControls
          onImageUpload={onImageUpload}
          onAudioUpload={onAudioUpload}
          disabled={loading || confirmLoading}
          loadingLabel={loading ? LOADING_LABELS[loadingType] : null}
        />
      </div>
    </div>
  );
}
