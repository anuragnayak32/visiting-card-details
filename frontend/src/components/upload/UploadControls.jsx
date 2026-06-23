import { useRef, useState } from "react";
import { CreditCard, Mic, Upload } from "lucide-react";

function DropZone({ accept, icon: Icon, title, subtitle, onFile, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handle = (file) => {
    if (file && !disabled) onFile(file);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handle(file);
  };

  return (
    <div
      className={`dropzone ${dragging ? "dragging" : ""} ${disabled ? "dropzone-disabled" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        disabled={disabled}
        onChange={(e) => {
          handle(e.target.files?.[0]);
          e.target.value = "";
        }}
      />
      <div className="dropzone-icon"><Icon size={22} /></div>
      <p className="dropzone-title">{title}</p>
      <p className="dropzone-sub">{subtitle}</p>
      <div className="dropzone-browse">
        <Upload size={13} /> Browse
      </div>
    </div>
  );
}

export default function UploadControls({ onImageUpload, onAudioUpload, disabled, loadingLabel }) {
  return (
    <div className="upload-area">
      {loadingLabel ? (
        <div className="upload-loading">
          <div className="spinner" />
          <span>{loadingLabel}</span>
        </div>
      ) : (
        <div className="upload-grid">
          <DropZone
            accept="image/jpeg,image/png,image/jpg"
            icon={CreditCard}
            title="Visiting Card"
            subtitle="JPG, PNG or JPEG — drag & drop or click"
            onFile={onImageUpload}
            disabled={disabled}
          />
          <DropZone
            accept="audio/mpeg,audio/wav,audio/x-m4a,audio/*"
            icon={Mic}
            title="Voice Note"
            subtitle="MP3, WAV or M4A — drag & drop or click"
            onFile={onAudioUpload}
            disabled={disabled}
          />
        </div>
      )}
    </div>
  );
}
