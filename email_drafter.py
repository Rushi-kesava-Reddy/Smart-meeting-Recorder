"""
Email Drafting & Prioritization Assistant Module using Groq LLM.
Analyzes meeting context to assess email priority (Urgent/High/Medium/Low),
suggest recipients, craft an executive subject line, and draft a structured
follow-up email in the requested language.
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
SUMMARY_PATH = os.path.join(MEETINGS_DIR, "summary.txt")
EMAIL_PATH = os.path.join(MEETINGS_DIR, "email_draft.txt")
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


def draft_followup_email(transcript, summary="", action_items=None, email_language="en"):
    """
    Generate professional follow-up email draft with priority classification.
    
    Returns:
        dict: {
            "subject": str,
            "priority": "Urgent" | "High" | "Medium" | "Low",
            "priority_reason": str,
            "recipients": str,
            "body": str,
            "language": str
        }
    """
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env or secrets.")

    lang_name = get_language_name(email_language)

    action_text = ""
    if action_items and isinstance(action_items, list):
        action_text = "\nAction Items:\n" + "\n".join(
            [f"- {item.get('task')} (Assigned to: {item.get('assigned_to', 'Team')}, Deadline: {item.get('deadline', 'TBD')})"
             for item in action_items if isinstance(item, dict)]
        )

    system_prompt = (
        f"You are an executive communication assistant.\n"
        f"Your role is to draft a comprehensive, highly professional post-meeting follow-up email in {lang_name}.\n"
        f"You must analyze the urgency of deadlines and impact of tasks to assign an Email Priority Level.\n\n"
        f"Priority classification criteria:\n"
        f"- 'Urgent': Critical blockers, immediate deadlines (<24-48 hours), high financial/operational risk.\n"
        f"- 'High': Major milestones due within a week, senior management decisions, project dependencies.\n"
        f"- 'Medium': Standard project tasks, normal sprint deliverables, routine updates.\n"
        f"- 'Low': Informational sharing, minor documentation, long-range future ideas.\n\n"
        f"Output must be a valid JSON object with the following keys:\n"
        f"{{\n"
        f'  "subject": "Clear, professional subject line in {lang_name}",\n'
        f'  "priority": "Urgent" | "High" | "Medium" | "Low",\n'
        f'  "priority_reason": "Concise 1-2 sentence justification for the assigned priority in {lang_name}",\n'
        f'  "recipients": "Suggested attendees or stakeholders mentioned in the meeting",\n'
        f'  "body": "Complete email body in {lang_name} including greeting, meeting recap, deliverables, action item assignments with owners and dates, next steps, and sign-off"\n'
        f"}}\n"
        f"Respond with valid JSON only."
    )

    user_content = f"Meeting Context:\n\nTranscript:\n{transcript}\n\nSummary:\n{summary}\n{action_text}"

    client = Groq(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.25,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        result = json.loads(content)

        draft = {
            "subject": result.get("subject", "Meeting Summary & Next Steps"),
            "priority": result.get("priority", "Medium").capitalize(),
            "priority_reason": result.get("priority_reason", "Routine post-meeting follow-up."),
            "recipients": result.get("recipients", "Team Members"),
            "body": result.get("body", ""),
            "language": email_language,
            "language_name": lang_name
        }

        # Save email draft text file
        try:
            with open(EMAIL_PATH, "w", encoding="utf-8") as f:
                f.write(f"Subject: {draft['subject']}\n")
                f.write(f"Priority: {draft['priority']} ({draft['priority_reason']})\n")
                f.write(f"Recipients: {draft['recipients']}\n\n")
                f.write(draft['body'])
        except Exception as e:
            print(f"[WARN] Failed to write email draft file: {e}", file=sys.stderr)

        save_meeting_state({"email_draft": draft})
        return draft

    except Exception as e:
        print(f"[ERROR] Email drafting failed: {e}", file=sys.stderr)
        raise e


def main():
    if not os.path.exists(TRANSCRIPT_PATH):
        print("[ERROR] Transcript not found.", file=sys.stderr)
        sys.exit(1)

    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        transcript = f.read()

    summary = ""
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary = f.read()

    state = load_meeting_state()
    action_items = state.get("action_items", [])
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"

    draft = draft_followup_email(transcript, summary, action_items, email_language=lang)
    print("===== EMAIL DRAFT CREATED =====")
    print(f"Subject: {draft['subject']}")
    print(f"Priority: {draft['priority']}")
    print(f"Saved to: {EMAIL_PATH}")


if __name__ == "__main__":
    main()
