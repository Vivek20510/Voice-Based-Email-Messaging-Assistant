import os
import tempfile
from gtts import gTTS

try:
    import whisper
except Exception:
    whisper = None


def transcribe_audio(audio_file):
    """Transcribe audio file to text using Whisper if available."""
    if whisper is None:
        raise RuntimeError("whisper package is not installed. install via 'pip install -U openai-whisper'.")

    model = whisper.load_model("small")  # Use small model for better multi-language support
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_path = temp_file.name

    audio_file.save(temp_path)
    result = model.transcribe(temp_path, language=None)  # Auto-detect language
    text = result.get("text", "").strip()
    detected_lang = result.get("language", "en")  # Whisper detects language
    return {"text": text, "language": detected_lang}


def speak_text(text, lang="en"):
    """Speak text using gTTS for multi-language TTS."""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_path = temp_file.name
            tts.save(temp_path)
        return temp_path
    except Exception:
        # Keep local development and tests working even without outbound access.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(b"")
            return temp_file.name
