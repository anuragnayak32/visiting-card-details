import { Image, Mic } from "lucide-react";

export default function UploadControls({ onImageUpload, onAudioUpload, disabled }) {
  return (
    <div className="upload-buttons">
      <label className="upload-btn" title="Upload visiting card">
        <Image size={20} />
        <input
          type="file"
          accept="image/*"
          disabled={disabled}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onImageUpload(file);
            e.target.value = "";
          }}
        />
      </label>
      <label className="upload-btn" title="Upload voice note">
        <Mic size={20} />
        <input
          type="file"
          accept="audio/*"
          disabled={disabled}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onAudioUpload(file);
            e.target.value = "";
          }}
        />
      </label>
    </div>
  );
}
