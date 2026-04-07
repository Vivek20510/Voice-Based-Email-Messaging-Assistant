import os
import tempfile
from unittest.mock import patch, MagicMock
from src.services.voice import transcribe_audio, speak_text


def test_transcribe_audio_detects_language():
    # Mock audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(b"dummy audio data")
        temp_path = temp_file.name

    # Mock whisper
    with patch("src.services.voice.whisper") as mock_whisper:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hello world", "language": "en"}
        mock_whisper.load_model.return_value = mock_model

        # Mock file save
        with patch("werkzeug.datastructures.FileStorage.save"):
            from werkzeug.datastructures import FileStorage
            mock_file = MagicMock(spec=FileStorage)
            result = transcribe_audio(mock_file)

        assert result == {"text": "Hello world", "language": "en"}

    os.unlink(temp_path)


def test_speak_text_creates_mp3():
    text = "Hello world"
    lang = "en"

    audio_path = speak_text(text, lang)

    assert os.path.exists(audio_path)
    assert audio_path.endswith(".mp3")

    # Clean up
    os.unlink(audio_path)


def test_speak_text_spanish():
    text = "Hola mundo"
    lang = "es"

    audio_path = speak_text(text, lang)

    assert os.path.exists(audio_path)
    assert audio_path.endswith(".mp3")

    # Clean up
    os.unlink(audio_path)