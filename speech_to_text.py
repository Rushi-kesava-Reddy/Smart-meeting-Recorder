"""
Multilingual Speech-to-Text using Groq Whisper.
Supports automatic language detection and manual language hints.
"""

import os
import sys
import json
import math
from dotenv import load_dotenv
from groq import Groq
from languages import get_language_name
from language_detector import detect_script_from_text

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
STATE_PATH = os.path.join(MEETINGS_DIR, "meeting_state.json")

os.makedirs(MEETINGS_DIR, exist_ok=True)


def load_meeting_state():
    """Load existing meeting state JSON if available."""
    if not os.path.exists(STATE_PATH):
        return {}

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"[WARN] Could not load meeting state: {e}", file=sys.stderr)
        return {}


def save_meeting_state(state_data):
    """Save or merge meeting state JSON."""
    current = load_meeting_state()
    current.update(state_data or {})

    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to write state file: {e}", file=sys.stderr)


def detect_audio_container(file_path):
    """Return a filename and MIME type based on the actual audio header."""
    with open(file_path, "rb") as f:
        header = f.read(64)

    if header.startswith(b"RIFF"):
        return "meeting.wav", "audio/wav"
    if b"ftyp" in header:
        return "meeting.m4a", "audio/mp4"
    if header.startswith(b"\x1aE\xdf\xa3"):
        return "meeting.webm", "audio/webm"
    if header.startswith(b"OggS"):
        return "meeting.ogg", "audio/ogg"
    if header.startswith(b"ID3") or header[:2] in (
        b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"
    ):
        return "meeting.mp3", "audio/mpeg"

    return "meeting.wav", "audio/wav"


def transcribe_audio(audio_path, language="auto"):
    """
    Transcribe an audio file with Groq Whisper.

    Parameters
    ----------
    audio_path : str
        Path to the audio file.
    language : str
        'auto' or an ISO-639-1 language code such as 'te', 'hi', 'ta', 'en'.

    Returns
    -------
    dict
        text, language_code, language_name, duration, confidence, word_count.

    Raises
    ------
    RuntimeError
        If configuration or the Groq request fails. Raising the exception is
        intentional so Streamlit can display the real error instead of showing
        a misleading empty-transcript message.
    """

    if not audio_path or not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    file_size = os.path.getsize(audio_path)
    file_size_mb = file_size / (1024 * 1024)

    if file_size < 1000:
        raise RuntimeError("The audio file is empty or too small to transcribe.")

    if file_size_mb > 25:
        raise RuntimeError(
            f"Audio file is {file_size_mb:.2f} MB. "
            "Please use an audio file within Groq's 25 MB limit."
        )

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Add GROQ_API_KEY to Render Environment Variables."
        )

    upload_name, mime_type = detect_audio_container(audio_path)

    print(f"[1] Audio file: {audio_path} ({file_size_mb:.2f} MB)")
    print(f"[2] Detected container: {upload_name} ({mime_type})")
    print(f"[2] Language hint: {language}")

    try:
        client = Groq(api_key=api_key, timeout=45.0, max_retries=1)

        # Read bytes and send them with an explicit filename/MIME type.
        # This works reliably for WAV, M4A, MP3, WebM and OGG uploads.
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        whisper_params = {
            "model": "whisper-large-v3-turbo",
            "file": (upload_name, audio_bytes, mime_type),
            "response_format": "verbose_json",
            "temperature": 0.0,
        }

        if language and language.lower() not in ("auto", "none", ""):
            whisper_params["language"] = language.lower()

        print("[3] Sending audio to Groq Whisper...")

        try:
            transcription = client.audio.transcriptions.create(**whisper_params)
        except Exception as first_error:
            # Keep the fallback because it helps if the Turbo model is
            # temporarily unavailable for an account/region.
            print(
                f"[WARN] whisper-large-v3-turbo failed: {first_error}",
                file=sys.stderr,
            )
            whisper_params["model"] = "whisper-large-v3"
            print("[3] Retrying once with whisper-large-v3...", file=sys.stderr)
            transcription = client.audio.transcriptions.create(**whisper_params)

        transcript_text = (getattr(transcription, "text", "") or "").strip()

        if not transcript_text:
            raise RuntimeError(
                "Groq Whisper returned an empty transcript. "
                "Please record clear speech and try again."
            )

        detected_lang = getattr(transcription, "language", None)

        if detected_lang:
            detected_lang = str(detected_lang).lower().strip()
        else:
            detected_lang, _ = detect_script_from_text(transcript_text)
            detected_lang = str(detected_lang or "en").lower().strip()

        duration = float(getattr(transcription, "duration", 0.0) or 0.0)

        confidence = 0.95
        segments = getattr(transcription, "segments", None)

        if segments:
            avg_logprobs = []

            for segment in segments:
                if isinstance(segment, dict):
                    value = segment.get("avg_logprob")
                else:
                    value = getattr(segment, "avg_logprob", None)

                if value is not None:
                    try:
                        avg_logprobs.append(float(value))
                    except (TypeError, ValueError):
                        pass

            if avg_logprobs:
                mean_logprob = sum(avg_logprobs) / len(avg_logprobs)
                confidence = round(
                    min(1.0, max(0.0, math.exp(mean_logprob))), 2
                )

        word_count = len(transcript_text.split())

        result = {
            "text": transcript_text,
            "language_code": detected_lang,
            "language_name": get_language_name(detected_lang),
            "duration": round(duration, 1),
            "confidence": confidence,
            "word_count": word_count,
        }

        print(
            f"[4] Completed: {result['language_name']} "
            f"({result['language_code']}), "
            f"{word_count} words, {result['duration']} seconds"
        )

        return result

    except Exception as e:
        message = f"Groq Whisper transcription failed: {type(e).__name__}: {e}"
        print(f"[ERROR] {message}", file=sys.stderr)
        raise RuntimeError(message) from e


def main():
    print("===== MULTILINGUAL SPEECH TO TEXT STARTED =====")

    audio_path = os.path.join(MEETINGS_DIR, "meeting.wav")
    language = sys.argv[1] if len(sys.argv) > 1 else "auto"

    result = transcribe_audio(audio_path, language=language)

    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(result["text"])

    save_meeting_state(
        {
            "original_transcript": result["text"],
            "detected_language": result["language_code"],
            "detected_language_name": result["language_name"],
            "transcription_confidence": result["confidence"],
            "duration": result["duration"],
            "word_count": result["word_count"],
        }
    )

    print("===== SPEECH TO TEXT COMPLETED =====")
    print(f"Language: {result['language_name']}")
    print(f"Words: {result['word_count']}, Duration: {result['duration']}s")
    print("\n--- ORIGINAL TRANSCRIPT ---")
    print(result["text"])
    print("---------------------------")


if __name__ == "__main__":
    main()
