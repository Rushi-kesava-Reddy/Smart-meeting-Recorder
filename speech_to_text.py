"""
Multilingual Speech to Text Module using Groq Whisper.
Supports auto-detection of spoken languages (Telugu, Hindi, Tamil, English, etc.)
or manual language selection while preserving original language text.
"""

import os
import sys
import json
import math
from dotenv import load_dotenv
from groq import Groq
from languages import get_language_info, get_language_name, get_groq_api_key
from language_detector import detect_script_from_text

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
STATE_PATH = os.path.join(MEETINGS_DIR, "meeting_state.json")

os.makedirs(MEETINGS_DIR, exist_ok=True)


def load_meeting_state():
    """Load existing meeting state JSON if available."""
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_meeting_state(state_data):
    """Save or merge meeting state JSON."""
    current = load_meeting_state()
    current.update(state_data)
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to write state file: {e}", file=sys.stderr)


def detect_audio_container(file_path):
    """Detect real container format from audio header bytes to ensure optimal API processing."""
    with open(file_path, "rb") as f:
        header = f.read(64)
    if header.startswith(b"RIFF"):
        return "meeting.wav", "audio/wav"
    elif b"ftyp" in header:
        return "meeting.m4a", "audio/mp4"
    elif header.startswith(b"\x1aE\xdf\xa3"):
        return "meeting.webm", "audio/webm"
    elif header.startswith(b"OggS"):
        return "meeting.ogg", "audio/ogg"
    elif header.startswith(b"ID3") or header[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "meeting.mp3", "audio/mpeg"
    return "meeting.wav", "audio/wav"


def transcribe_audio(wav_path, language="auto"):
    """
    Convert audio file to text using Groq Whisper API.
    
    Args:
        wav_path (str): Path to WAV/audio file.
        language (str): 'auto' or specific ISO code (e.g., 'te', 'hi', 'en').
        
    Returns:
        dict: Transcription results with text, detected language, confidence, etc.
              or None on failure.
    """
    if not os.path.exists(wav_path):
        print(f"[ERROR] Audio file not found: {wav_path}", file=sys.stderr)
        return None

    api_key = get_groq_api_key()
    if not api_key:
        print("[ERROR] GROQ_API_KEY is not configured in environment or secrets.", file=sys.stderr)
        return None

    file_size_mb = os.path.getsize(wav_path) / (1024 * 1024)
    print(f"[1] Audio file found: {wav_path} ({file_size_mb:.2f} MB)")

    if file_size_mb > 25:
        print("[ERROR] Audio file exceeds 25MB Groq Whisper limit.", file=sys.stderr)
        return None

    try:
        client = Groq(api_key=api_key)
        print(f"[2] Connecting to Groq Whisper (Language setting: {language})...")

        upload_name, mime_type = detect_audio_container(wav_path)
        with open(wav_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        file_tuple = (upload_name, audio_bytes, mime_type)

        whisper_params = {
            "model": "whisper-large-v3-turbo",
            "file": file_tuple,
            "response_format": "verbose_json",
            "temperature": 0.0
        }

        # If user explicitly requested a specific language (not auto)
        if language and language.lower() not in ("auto", "none", ""):
            whisper_params["language"] = language.lower()

        try:
            transcription = client.audio.transcriptions.create(**whisper_params)
        except Exception as e_turbo:
            print(f"[WARN] whisper-large-v3-turbo attempt: {e_turbo}, falling back to whisper-large-v3", file=sys.stderr)
            whisper_params["model"] = "whisper-large-v3"
            transcription = client.audio.transcriptions.create(**whisper_params)

        transcript_text = getattr(transcription, "text", "") or ""
        transcript_text = transcript_text.strip()

        if not transcript_text:
            print("[WARN] Whisper returned empty transcription text.", file=sys.stderr)

        # Detect spoken language from Whisper verbose_json
        detected_lang = getattr(transcription, "language", None)
        if not detected_lang:
            # Fallback to Unicode script detection on the transcript text
            detected_lang, _ = detect_script_from_text(transcript_text)
        else:
            detected_lang = detected_lang.lower().strip()

        duration = getattr(transcription, "duration", 0.0) or 0.0

        # Calculate average confidence if segment data exists
        confidence = 0.95
        segments = getattr(transcription, "segments", None)
        if segments and isinstance(segments, list) and len(segments) > 0:
            avg_logprobs = []
            for seg in segments:
                if isinstance(seg, dict) and "avg_logprob" in seg:
                    avg_logprobs.append(seg["avg_logprob"])
                elif hasattr(seg, "avg_logprob"):
                    avg_logprobs.append(seg.avg_logprob)
            if avg_logprobs:
                mean_logprob = sum(avg_logprobs) / len(avg_logprobs)
                confidence = round(min(1.0, max(0.0, math.exp(mean_logprob))), 2)

        word_count = len(transcript_text.split()) if transcript_text else 0

        result = {
            "text": transcript_text,
            "language_code": detected_lang,
            "language_name": get_language_name(detected_lang),
            "duration": round(duration, 1),
            "confidence": confidence,
            "word_count": word_count
        }

        print(f"[3] Transcription completed: Detected Language = {result['language_name']} ({result['language_code']}), Confidence = {int(confidence*100)}%")
        return result

    except Exception as e:
        print(f"[ERROR] Groq Whisper transcription failed: {e}", file=sys.stderr)
        return None


def main():
    print("===== MULTILINGUAL SPEECH TO TEXT STARTED =====")
    wav_path = os.path.join(MEETINGS_DIR, "meeting.wav")

    # Check if a custom language code was passed as command-line arg
    lang_arg = sys.argv[1] if len(sys.argv) > 1 else "auto"

    result = transcribe_audio(wav_path, language=lang_arg)

    if result is None:
        print("[ERROR] Transcription failed", file=sys.stderr)
        sys.exit(1)

    transcript_text = result["text"]

    # Save original transcript to meetings/transcript.txt
    try:
        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        print(f"[4] Original transcript saved to: {TRANSCRIPT_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to save transcript: {e}", file=sys.stderr)
        sys.exit(1)

    # Save state
    save_meeting_state({
        "original_transcript": transcript_text,
        "detected_language": result["language_code"],
        "detected_language_name": result["language_name"],
        "transcription_confidence": result["confidence"],
        "duration": result["duration"],
        "word_count": result["word_count"]
    })

    print("===== SPEECH TO TEXT COMPLETED =====")
    print(f"Language: {result['language_name']}")
    print(f"Words: {result['word_count']}, Duration: {result['duration']}s")
    print("\n--- ORIGINAL TRANSCRIPT ---")
    try:
        print(transcript_text)
    except UnicodeEncodeError:
        print(transcript_text.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
    print("---------------------------\n")


if __name__ == "__main__":
    main()