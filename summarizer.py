"""
Multilingual Meeting Summarization Module using Groq LLM.
Generates structured executive meeting summaries in the meeting's original language
or any user-selected output language (Telugu, Hindi, Tamil, English, etc.).
"""

import os
import sys
import json
from dotenv import load_dotenv
from groq import Groq
from languages import get_language_name, get_language_info, get_groq_api_key
from action_items import extract_action_items

load_dotenv()

# Configure stdout encoding safely
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
SUMMARY_PATH = os.path.join(MEETINGS_DIR, "summary.txt")
STATE_PATH = os.path.join(MEETINGS_DIR, "meeting_state.json")

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


def generate_summary(summary_language="same"):
    """
    Generate structured meeting summary.
    
    Args:
        summary_language (str): 'same' (same as meeting language) or ISO language code.
        
    Returns:
        dict: Summary metadata and formatted text.
    """
    print("===== MULTILINGUAL MEETING SUMMARIZATION STARTED =====")

    if not os.path.exists(TRANSCRIPT_PATH):
        raise FileNotFoundError(f"Transcript file not found at {TRANSCRIPT_PATH}. Please run Speech-to-Text first.")

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8", errors="replace") as file:
        transcript = file.read().strip()

    if not transcript:
        raise ValueError("Transcript file is empty. Please complete Speech-to-Text first.")

    state = load_meeting_state()
    detected_lang = state.get("detected_language", "en")

    # Determine effective target language
    if not summary_language or summary_language.lower() in ("same", "auto", "meeting"):
        effective_lang = detected_lang
    else:
        effective_lang = summary_language.lower().strip()

    lang_name = get_language_name(effective_lang)
    print(f"[1] Transcript loaded ({len(transcript)} chars). Generating summary in {lang_name}...")

    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env or secrets.")

    client = Groq(api_key=api_key)

    system_prompt = (
        f"You are a professional multilingual executive meeting intelligence assistant.\n"
        f"Your task is to analyze the meeting transcript and generate a thorough, clear, and executive-level summary.\n"
        f"CRITICAL REQUIREMENT: You MUST write the ENTIRE summary in {lang_name}.\n\n"
        f"Structure the summary with these exact 7 sections in {lang_name}:\n\n"
        f"1. Executive Summary\n"
        f"   (A concise overview summarizing the main goal and outcome of the meeting)\n\n"
        f"2. Key Discussion Points\n"
        f"   (Bullet points highlighting the major topics and ideas discussed)\n\n"
        f"3. Decisions Made\n"
        f"   (Specific agreements, approvals, and decisions agreed upon)\n\n"
        f"4. Action Items\n"
        f"   (List of specific tasks assigned to people or teams with deadlines)\n\n"
        f"5. Important Deadlines\n"
        f"   (Specific dates, milestones, or target times mentioned)\n\n"
        f"6. Important People / Participants\n"
        f"   (Names of attendees, speakers, or stakeholders mentioned)\n\n"
        f"7. Next Steps\n"
        f"   (Immediate upcoming milestones and subsequent meetings)\n\n"
        f"Rules:\n"
        f"- Only use information actually present or directly implied in the transcript.\n"
        f"- For project presentations, briefings, or proposals where explicit deadlines or formal assignments were not announced, formulate constructive project milestones, deliverables, and logical next steps based on the speaker's stated objectives.\n"
        f"- Do not leave sections as blank or repetitive 'None mentioned'. Ensure every section provides clear, meaningful meeting or project intelligence.\n"
        f"- Format clearly using clean headers and bullet points without markdown tables."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please summarize the following meeting transcript in {lang_name}:\n\n{transcript}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        if not response.choices:
            raise RuntimeError("The AI model returned no response.")

        summary_text = response.choices[0].message.content
        if not summary_text:
            raise RuntimeError("The AI model returned an empty summary.")

        summary_text = summary_text.strip()
        print(f"[2] Summary generated successfully ({len(summary_text)} chars).")

        # Save to summary.txt
        with open(SUMMARY_PATH, "w", encoding="utf-8", errors="replace") as file:
            file.write(summary_text)

        print(f"[3] Summary saved to: {SUMMARY_PATH}")

        # Also extract structured action items and decisions for dashboard tables
        print("[4] Extracting structured action items and decisions...")
        action_data = extract_action_items(transcript, output_language=effective_lang)

        save_meeting_state({
            "summary_text": summary_text,
            "summary_language": effective_lang,
            "summary_language_name": lang_name,
            "action_items": action_data.get("action_items", []),
            "decisions": action_data.get("decisions", [])
        })

        print("===== MEETING SUMMARIZATION COMPLETED =====")
        return {
            "summary": summary_text,
            "language": effective_lang,
            "language_name": lang_name,
            "action_items": action_data.get("action_items", []),
            "decisions": action_data.get("decisions", [])
        }

    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}", file=sys.stderr)
        raise e


def main():
    lang_arg = sys.argv[1] if len(sys.argv) > 1 else "same"
    try:
        result = generate_summary(summary_language=lang_arg)
        print("\n--- SUMMARY ---")
        try:
            print(result["summary"])
        except UnicodeEncodeError:
            print(result["summary"].encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
        print("------------------\n")
    except Exception as e:
        print(f"[ERROR] Summarizer execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()