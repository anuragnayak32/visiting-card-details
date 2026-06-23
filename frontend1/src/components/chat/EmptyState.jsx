import { CreditCard, Mic } from "lucide-react";

export default function EmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-icon-wrap">
        <CreditCard size={40} className="empty-icon" />
      </div>
      <h2>Visiting Card AI</h2>
      <p>Upload a business card to extract contact details, then attach a voice note to add context.</p>
      <div className="empty-hints">
        <div className="hint-card">
          <CreditCard size={20} />
          <div>
            <strong>Upload a Card</strong>
            <span>JPG, PNG or JPEG business cards</span>
          </div>
        </div>
        <div className="hint-card">
          <Mic size={20} />
          <div>
            <strong>Voice Note</strong>
            <span>MP3, WAV or M4A voice memos</span>
          </div>
        </div>
      </div>
    </div>
  );
}
