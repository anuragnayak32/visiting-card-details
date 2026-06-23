const FIELDS = [
  { key: "name", label: "Name" },
  { key: "phone", label: "Phone" },
  { key: "email", label: "Email" },
  { key: "company", label: "Company" },
  { key: "designation", label: "Designation" },
  { key: "website", label: "Website" },
  { key: "address", label: "Address" },
];

export default function ContactPreview({ cardData, onConfirm, onReject, loading }) {
  if (!cardData) return null;

  return (
    <div className="contact-preview">
      <h4>Extracted Contact Details</h4>
      <div className="contact-grid">
        {FIELDS.map(({ key, label }) =>
          cardData[key] ? (
            <div key={key}>
              <span>{label}: </span>
              {cardData[key]}
            </div>
          ) : null
        )}
      </div>
      <div className="confirm-actions">
        <button className="btn-primary" onClick={onConfirm} disabled={loading}>
          {loading ? "Saving..." : "Confirm & Save"}
        </button>
        <button className="btn-secondary" onClick={onReject} disabled={loading}>
          Reject
        </button>
      </div>
    </div>
  );
}
