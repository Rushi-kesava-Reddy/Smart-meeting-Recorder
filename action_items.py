"""
Action Items & Decision Extraction Module using Groq LLM.
Extracts structured action items (Task, Assignee, Deadline, Priority, Status)
and key decisions in the selected output language.
"""

import os
import sys
import json
import re
from dotenv import load_dotenv
from groq import Groq
from languages import get_language_name, get_language_info, get_groq_api_key

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
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


def extract_action_items(transcript, output_language="en"):
    """
    Extract structured action items and decisions from transcript.
    Returns:
        dict: {"action_items": [...], "decisions": [...]}
    """
    if not transcript or not transcript.strip():
        return {"action_items": [], "decisions": []}

    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env or secrets.")

    lang_name = get_language_name(output_language)

    system_prompt = (
        f"You are an executive project management intelligence assistant.\n"
        f"Extract all action items, deliverables, milestones, and decisions made or implied in the meeting transcript.\n"
        f"CRITICAL INSTRUCTION: If the meeting is a project presentation, briefing, or proposal without formally assigned task tickets, formulate 3-5 core project deliverables, architectural milestones, and next steps implied by the speaker's stated goals.\n"
        f"Output MUST be in valid JSON format with keys 'action_items' and 'decisions' in {lang_name}.\n\n"
        f"Format schema:\n"
        f"{{\n"
        f'  "action_items": [\n'
        f'    {{\n'
        f'      "task": "Deliverable or task description in {lang_name}",\n'
        f'      "assigned_to": "Person, team, or department (e.g. Speaker name / Project Team / Unassigned)",\n'
        f'      "deadline": "Phase, timeline, or milestone (e.g. Phase 1 / Milestone 2 / TBD)",\n'
        f'      "priority": "High" | "Medium" | "Low",\n'
        f'      "status": "Pending" | "In Progress" | "Completed"\n'
        f'    }}\n'
        f'  ],\n'
        f'  "decisions": [\n'
        f'    "Key architectural choice, approved scope, or decision 1 in {lang_name}",\n'
        f'    "Key architectural choice, approved scope, or decision 2 in {lang_name}"\n'
        f'  ]\n'
        f"}}\n\n"
        f"Respond with valid JSON only."
    )

    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract action items and decisions from this transcript:\n\n{transcript}"}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        data = json.loads(content)

        action_items = data.get("action_items", [])
        decisions = data.get("decisions", [])

        # Validate action item fields
        cleaned_items = []
        for item in action_items:
            if isinstance(item, dict) and item.get("task"):
                cleaned_items.append({
                    "task": str(item.get("task", "")),
                    "assigned_to": str(item.get("assigned_to", "Unassigned")),
                    "deadline": str(item.get("deadline", "Not specified")),
                    "priority": str(item.get("priority", "Medium")).capitalize(),
                    "status": str(item.get("status", "Pending")).capitalize()
                })

        return {
            "action_items": cleaned_items,
            "decisions": [str(d) for d in decisions if d]
        }

    except Exception as e:
        print(f"[ERROR] Action items extraction failed: {e}", file=sys.stderr)
        return {"action_items": [], "decisions": []}


def main():
    if not os.path.exists(TRANSCRIPT_PATH):
        print("[ERROR] Transcript file not found.", file=sys.stderr)
        sys.exit(1)

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        transcript = f.read()

    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    result = extract_action_items(transcript, output_language=lang)

    save_meeting_state(result)
    print(f"Extracted {len(result['action_items'])} action items and {len(result['decisions'])} decisions.")


if __name__ == "__main__":
    main()
