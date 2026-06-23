"""Whisper-based speech-to-text transcription using faster-whisper."""

import asyncio
from functools import lru_cache

from faster_whisper import WhisperModel


@lru_cache(maxsize=1)
def _load_model():
    """Load faster-whisper model once (tiny for faster local inference)."""
    return WhisperModel("tiny", device="cpu", compute_type="int8")


async def transcribe_audio(audio_path: str) -> str:
    """Transcribe an audio file using Whisper."""
    if not audio_path:
        return ""

    def _transcribe() -> str:
        model = _load_model()
        segments, _ = model.transcribe(audio_path)
        return " ".join(segment.text.strip() for segment in segments).strip()

    try:
        return await asyncio.to_thread(_transcribe)
    except Exception as exc:
        return f"[Transcription unavailable: {exc}]"
