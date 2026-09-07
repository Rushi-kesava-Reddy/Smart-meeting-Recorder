"""
Modular AI Translation Module using Groq LLM.
Translates meeting transcripts between any supported languages (e.g., Telugu -> English,
English -> Telugu, Hindi -> English, Tamil -> English) while preserving meeting context.
"""

import os
import sys
import json
from dotenv import load_dotenv
from groq import Groq
from languages import get_language_name, get_language_info, get_groq_api_key

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
TRANSLATED_PATH = os.path.join(MEETINGS_DIR, "translated_transcript.txt")
STATE_PATH = os.path.join(MEETINGS_DIR, "meeting_state.json")

# LLM model for accurate multilingual translation
MODEL_NAME = "openai/gpt-oss-20b"


def load_meeting_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_meeting_state(state_data):
    current = load_meeting_state()
    current.update(state_data)
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to write state file: {e}", file=sys.stderr)


def translate_text(text, target_language="en", source_language=None):
    """
    Translate text to target language using Groq LLM.
    
    Args:
        text (str): The transcript text to translate.
        target_language (str): Target language code (e.g., 'en', 'te', 'hi', 'ta').
        source_language (str, optional): Source language code if known.
        
    Returns:
        str: Translated text or None on failure.
    """
    if not text or not text.strip():
        print("[WARN] Empty text passed to translator.", file=sys.stderr)
        return ""

    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env or secrets.")

    target_info = get_language_info(target_language)
    target_name = get_language_name(target_language)
    source_name = get_language_name(source_language) if source_language else "the original language"

    print(f"[1] Translating text ({len(text)} chars) from {source_name} to {target_name}...")

    system_prompt = (
        f"You are an expert multilingual conference and meeting translator.\n"
        f"Your task is to translate the provided meeting transcript into natural, fluent {target_name}.\n\n"
        f"Rules:\n"
        f"1. Preserve the exact meaning, technical terms, project names, and speaker nuances.\n"
        f"2. Keep proper nouns, company names, product names, and dates intact.\n"
        f"3. Do not add any commentary, notes, preamble, or explanations.\n"
        f"4. Provide ONLY the translated text in {target_name}.\n"
    )

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please translate the following meeting transcript to {target_name}:\n\n{text}"}
            ],
            temperature=0.2,
            max_tokens=2500
        )

        if not response.choices:
            raise RuntimeError("AI model returned no response choices.")

        translated_text = response.choices[0].message.content
        if translated_text:
            translated_text = translated_text.strip()

        print(f"[2] Translation completed successfully ({len(translated_text)} chars).")
        return translated_text

    except Exception as e:
        print(f"[ERROR] Translation failed: {e}", file=sys.stderr)
        raise e


def main():
    print("===== MEETING TRANSCRIPTION TRANSLATION STARTED =====")
    target_lang = sys.argv[1] if len(sys.argv) > 1 else "en"

    if not os.path.exists(TRANSCRIPT_PATH):
        print(f"[ERROR] Transcript not found at {TRANSCRIPT_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="replace") as f:
        transcript = f.read().strip()

    if not transcript:
        print("[ERROR] Transcript is empty.", file=sys.stderr)
        sys.exit(1)

    state = load_meeting_state()
    source_lang = state.get("detected_language", None)

    translated = translate_text(transcript, target_language=target_lang, source_language=source_lang)

    with open(TRANSLATED_PATH, "w", encoding="utf-8") as f:
        f.write(translated)

    save_meeting_state({
        "translated_transcript": translated,
        "translation_language": target_lang,
        "translation_language_name": get_language_name(target_lang)
    })

    print(f"[3] Translated transcript saved to: {TRANSLATED_PATH}")
    print("===== TRANSLATION COMPLETED =====")


if __name__ == "__main__":
    main()
