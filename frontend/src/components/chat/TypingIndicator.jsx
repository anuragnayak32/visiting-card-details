import { Bot } from "lucide-react";

export default function TypingIndicator({ label }) {
  return (
    <div className="message-row message-assistant">
      <div className="avatar avatar-ai">
        <Bot size={16} />
      </div>
      <div className="bubble bubble-ai typing-bubble">
        <div className="typing-dots">
          <span /><span /><span />
        </div>
        {label && <span className="typing-label">{label}</span>}
      </div>
    </div>
  );
}
