import { useState } from "react";
import {
  User, Briefcase, Building2, Phone, Mail, Globe,
  Linkedin, MapPin, Check, X, Pencil, Save,
} from "lucide-react";

const FIELDS = [
  { key: "name", label: "Name", icon: User },
  { key: "designation", label: "Designation", icon: Briefcase },
  { key: "company", label: "Company", icon: Building2 },
  { key: "phone", label: "Phone", icon: Phone },
  { key: "email", label: "Email", icon: Mail },
  { key: "website", label: "Website", icon: Globe },
  { key: "linkedin", label: "LinkedIn", icon: Linkedin },
  { key: "address", label: "Address", icon: MapPin },
];

export default function ContactPreview({ cardData, onConfirm, onReject, loading }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({ ...cardData });

  if (!cardData) return null;

  const data = editing ? draft : cardData;

  return (
    <div className="contact-card">
      <div className="contact-card-header">
        <div className="contact-avatar">
          {(data.name || "?")[0].toUpperCase()}
        </div>
        <div>
          <p className="contact-name">{data.name || "—"}</p>
          <p className="contact-role">{data.designation || ""}{data.company ? ` · ${data.company}` : ""}</p>
        </div>
        <button
          className="edit-btn"
          onClick={() => { setEditing((e) => !e); setDraft({ ...cardData }); }}
        >
          <Pencil size={14} /> {editing ? "Cancel" : "Edit"}
        </button>
      </div>

      <div className="contact-fields">
        {FIELDS.map(({ key, label, icon: Icon }) => {
          const val = data[key];
          if (!val && !editing) return null;
          return (
            <div className="contact-field" key={key}>
              <span className="field-icon"><Icon size={13} /></span>
              <span className="field-label">{label}</span>
              {editing ? (
                <input
                  className="field-input"
                  value={draft[key] || ""}
                  onChange={(e) => setDraft((d) => ({ ...d, [key]: e.target.value }))}
                  placeholder={label}
                />
              ) : (
                <span className="field-value">{val}</span>
              )}
            </div>
          );
        })}
      </div>

      <div className="contact-actions">
        {editing ? (
          <button
            className="btn-confirm"
            onClick={() => { onConfirm(draft); setEditing(false); }}
            disabled={loading}
          >
            <Save size={15} /> {loading ? "Saving…" : "Save & Confirm"}
          </button>
        ) : (
          <button className="btn-confirm" onClick={() => onConfirm(null)} disabled={loading}>
            <Check size={15} /> {loading ? "Saving…" : "Confirm & Save"}
          </button>
        )}
        <button className="btn-reject" onClick={onReject} disabled={loading}>
          <X size={15} /> Reject
        </button>
      </div>
    </div>
  );
}
