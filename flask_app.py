"""
Multilingual AI Smart Meeting Recorder & Intelligent Meeting Assistant
Main Flask Web Application & REST API Gateway.
"""

import os
import sys
import json
import threading
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    redirect,
    url_for
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Modular Engine Components
import languages
from speech_to_text import transcribe_audio
from translator import translate_text
from summarizer import generate_summary
from action_items import extract_action_items
from email_drafter import draft_followup_email
from report_generator import generate_pdf_report
from demo_data import get_demo_scenario, get_all_demo_scenarios

# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart_meeting_recorder_secure_production_secret_key_v2"
)

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
os.makedirs(MEETINGS_DIR, exist_ok=True)

WAV_PATH = os.path.join(MEETINGS_DIR, "meeting.wav")
TRANSCRIPT_PATH = os.path.join(MEETINGS_DIR, "transcript.txt")
TRANSLATED_PATH = os.path.join(MEETINGS_DIR, "translated_transcript.txt")
SUMMARY_PATH = os.path.join(MEETINGS_DIR, "summary.txt")
PDF_PATH = os.path.join(MEETINGS_DIR, "Meeting_Report.pdf")
EMAIL_PATH = os.path.join(MEETINGS_DIR, "email_draft.txt")
STATE_PATH = os.path.join(MEETINGS_DIR, "meeting_state.json")

# ============================================================
# THREAD-SAFE STATE MANAGEMENT
# ============================================================

state_lock = threading.Lock()

def get_persisted_state():
    """Read state from JSON file or return clean defaults."""
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "detected_language": "en",
        "detected_language_name": "English",
        "transcription_confidence": 0.95,
        "duration": 0,
        "word_count": 0,
        "original_transcript": "",
        "translated_transcript": "",
        "translation_language": "en",
        "summary_text": "",
        "summary_language": "same",
        "action_items": [],
        "decisions": [],
        "email_draft": {},
        "report_language": "same"
    }

def update_persisted_state(updates):
    """Update state on disk thread-safely."""
    current = get_persisted_state()
    current.update(updates)
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to write meeting_state.json: {e}", file=sys.stderr)
    return current

# In-memory transient background task tracker
async_task_state = {
    "status": "idle",
    "stage": "",
    "progress": "",
    "error": None
}

# ============================================================
# HEALTH & ERROR HANDLERS
# ============================================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "Multilingual Smart Meeting Recorder",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def page_not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "API endpoint not found"}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    return jsonify({"status": "error", "message": "An internal server error occurred"}), 500


# ============================================================
# PAGE ROUTES
# ============================================================

@app.route("/")
@app.route("/record")
def index():
    return render_template("index.html")


@app.route("/transcript")
def transcript_page():
    return render_template("transcript.html")


@app.route("/summary")
def summary_page():
    return render_template("summary.html")


@app.route("/email")
def email_page():
    return render_template("email.html")


@app.route("/report")
def report_page():
    return render_template("report.html")


@app.route("/modules")
def modules_page():
    return render_template("modules.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


# ============================================================
# API - SYSTEM STATUS & METADATA
# ============================================================

@app.route("/api/status", methods=["GET"])
def get_status():
    """
    Consolidated system state endpoint returning file availability,
    transcription progress, and language intelligence metadata.
    """
    state = get_persisted_state()

    # Read transcript from file if not in state
    transcript_text = state.get("original_transcript", "")
    if not transcript_text and os.path.exists(TRANSCRIPT_PATH):
        try:
            with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
                transcript_text = f.read()
        except Exception:
            pass

    # Read translated transcript
    translated_text = state.get("translated_transcript", "")
    if not translated_text and os.path.exists(TRANSLATED_PATH):
        try:
            with open(TRANSLATED_PATH, "r", encoding="utf-8") as f:
                translated_text = f.read()
        except Exception:
            pass

    # Read summary
    summary_text = state.get("summary_text", "")
    if not summary_text and os.path.exists(SUMMARY_PATH):
        try:
            with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
                summary_text = f.read()
        except Exception:
            pass

    with state_lock:
        task_status = async_task_state["status"]
        task_stage = async_task_state["stage"]
        task_progress = async_task_state["progress"]
        task_error = async_task_state["error"]

    return jsonify({
        "has_audio": os.path.exists(WAV_PATH),
        "has_transcript": bool(transcript_text),
        "has_translation": bool(translated_text),
        "has_summary": bool(summary_text),
        "has_email": bool(state.get("email_draft", {}).get("body")),
        "has_pdf": os.path.exists(PDF_PATH),

        "transcript": transcript_text,
        "translated_transcript": translated_text,
        "summary": summary_text,
        "action_items": state.get("action_items", []),
        "decisions": state.get("decisions", []),
        "email_draft": state.get("email_draft", {}),

        "detected_language": state.get("detected_language", "en"),
        "detected_language_name": state.get("detected_language_name", "English"),
        "transcription_confidence": state.get("transcription_confidence", 0.95),
        "duration": state.get("duration", 0),
        "word_count": state.get("word_count", len(transcript_text.split()) if transcript_text else 0),
        "summary_language": state.get("summary_language", "same"),
        "translation_language": state.get("translation_language", "en"),
        "report_language": state.get("report_language", "same"),

        "transcription_status": task_status,
        "task_stage": task_stage,
        "transcription_progress": task_progress,
        "transcription_error": task_error
    })


@app.route("/api/languages", methods=["GET"])
def get_languages():
    """Return all supported languages with native names."""
    return jsonify({
        "status": "success",
        "languages": languages.get_supported_languages()
    })


@app.route("/api/demo_scenarios", methods=["GET"])
def get_demo_scenarios():
    """Return list of pre-configured college demo scenarios."""
    return jsonify({
        "status": "success",
        "scenarios": get_all_demo_scenarios()
    })


# ============================================================
# API - AUDIO CAPTURE & UPLOAD
# ============================================================

@app.route("/api/save_audio", methods=["POST"])
def save_audio():
    """Save audio recording from browser microphone or upload form."""
    if "audio_file" not in request.files:
        return jsonify({"status": "error", "message": "No audio file provided in request."}), 400

    file = request.files["audio_file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty file uploaded."}), 400

    try:
        file.save(WAV_PATH)

        # Reset async state
        with state_lock:
            async_task_state["status"] = "idle"
            async_task_state["stage"] = ""
            async_task_state["progress"] = ""
            async_task_state["error"] = None

        return jsonify({
            "status": "success",
            "message": "Audio recording saved successfully",
            "filename": "meeting.wav"
        })

    except Exception as error:
        return jsonify({"status": "error", "message": f"Failed to save audio: {str(error)}"}), 500


@app.route("/api/record_server", methods=["POST"])
def record_server():
    """Alternative hardware recorder fallback for local testing."""
    recorder_script = os.path.join(BASE_DIR, "recorder.py")
    if not os.path.exists(recorder_script):
        return jsonify({"status": "error", "message": "recorder.py not found."}), 404

    import subprocess
    try:
        result = subprocess.run([sys.executable, recorder_script], cwd=BASE_DIR, capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "message": "Hardware recording finished", "stdout": result.stdout})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Hardware recording failed: {str(e)}"}), 500


# ============================================================
# API - MULTILINGUAL SPEECH TO TEXT
# ============================================================

def run_transcription_background(language="auto"):
    """Background worker executing Groq Whisper speech recognition."""
    with state_lock:
        async_task_state["status"] = "processing"
        async_task_state["stage"] = "transcribing"
        async_task_state["progress"] = "Connecting to Groq Whisper and analyzing audio..."
        async_task_state["error"] = None

    try:
        result = transcribe_audio(WAV_PATH, language=language)

        if not result or not result.get("text"):
            with state_lock:
                async_task_state["status"] = "error"
                async_task_state["error"] = "Speech recognition produced an empty transcript. Please check audio clarity."
                async_task_state["progress"] = "Transcription failed"
            return

        transcript_text = result["text"]

        # Write transcript.txt
        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Update persisted state
        update_persisted_state({
            "original_transcript": transcript_text,
            "detected_language": result["language_code"],
            "detected_language_name": result["language_name"],
            "transcription_confidence": result["confidence"],
            "duration": result["duration"],
            "word_count": result["word_count"]
        })

        with state_lock:
            async_task_state["status"] = "completed"
            async_task_state["stage"] = "done"
            async_task_state["progress"] = f"Transcribed successfully in {result['language_name']} ({int(result['confidence']*100)}% confidence)."
            async_task_state["error"] = None

    except Exception as e:
        with state_lock:
            async_task_state["status"] = "error"
            async_task_state["error"] = f"Speech recognition failed: {str(e)}"
            async_task_state["progress"] = "Error during transcription"


@app.route("/api/transcribe", methods=["POST"])
def run_transcribe():
    """Trigger fast speech-to-text with optional language parameter."""
    if not os.path.exists(WAV_PATH):
        return jsonify({"status": "error", "message": "No audio found at meetings/meeting.wav. Please record or upload audio first."}), 400

    data = request.get_json(silent=True) or {}
    req_lang = data.get("language", "auto")

    with state_lock:
        async_task_state["status"] = "processing"
        async_task_state["stage"] = "transcribing"
        async_task_state["progress"] = f"Connecting to Groq Whisper (Language: {req_lang})..."
        async_task_state["error"] = None

    try:
        result = transcribe_audio(WAV_PATH, language=req_lang)

        if not result or not result.get("text"):
            with state_lock:
                async_task_state["status"] = "error"
                async_task_state["error"] = "Speech recognition produced an empty transcript. Please check audio clarity."
                async_task_state["progress"] = "Transcription failed"
            return jsonify({
                "status": "error",
                "message": "Speech recognition produced an empty transcript. Please check audio clarity."
            }), 400

        transcript_text = result["text"]

        # Write transcript.txt
        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Update persisted state
        update_persisted_state({
            "original_transcript": transcript_text,
            "detected_language": result["language_code"],
            "detected_language_name": result["language_name"],
            "transcription_confidence": result["confidence"],
            "duration": result["duration"],
            "word_count": result["word_count"]
        })

        with state_lock:
            async_task_state["status"] = "completed"
            async_task_state["stage"] = "done"
            async_task_state["progress"] = f"Transcribed successfully in {result['language_name']} ({int(result['confidence']*100)}% confidence)."
            async_task_state["error"] = None

        return jsonify({
            "status": "success",
            "message": f"Speech recognized successfully as {result['language_name']}!",
            "transcript": transcript_text,
            "detected_language": result["language_code"],
            "detected_language_name": result["language_name"],
            "transcription_confidence": result["confidence"],
            "duration": result["duration"],
            "word_count": result["word_count"],
            "transcription_status": "completed"
        })

    except Exception as e:
        with state_lock:
            async_task_state["status"] = "error"
            async_task_state["error"] = f"Speech recognition failed: {str(e)}"
            async_task_state["progress"] = "Error during transcription"
        return jsonify({
            "status": "error",
            "message": f"Speech recognition failed: {str(e)}"
        }), 500


@app.route("/hybridaction/<path:subpath>", methods=["GET", "POST"])
def swallow_tracker(subpath):
    """Handle client tracker requests quietly without 404 logs."""
    return ("", 204)


# ============================================================
# API - TRANSLATION
# ============================================================

@app.route("/api/translate", methods=["POST"])
def run_translate():
    """Translate meeting transcript into target language."""
    data = request.get_json(silent=True) or {}
    target_lang = data.get("target_language", "en")

    state = get_persisted_state()
    transcript = state.get("original_transcript", "")

    if not transcript and os.path.exists(TRANSCRIPT_PATH):
        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            transcript = f.read()

    if not transcript:
        return jsonify({"status": "error", "message": "No transcript available to translate. Run Speech-to-Text first."}), 400

    source_lang = state.get("detected_language", None)

    try:
        translated = translate_text(transcript, target_language=target_lang, source_language=source_lang)

        with open(TRANSLATED_PATH, "w", encoding="utf-8") as f:
            f.write(translated)

        target_name = languages.get_language_name(target_lang)
        update_persisted_state({
            "translated_transcript": translated,
            "translation_language": target_lang,
            "translation_language_name": target_name
        })

        return jsonify({
            "status": "success",
            "message": f"Transcript translated successfully to {target_name}.",
            "translated_transcript": translated,
            "target_language": target_lang,
            "target_language_name": target_name
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Translation failed: {str(e)}"}), 500


# ============================================================
# API - SUMMARIZATION & ACTION ITEMS
# ============================================================

@app.route("/api/summarize", methods=["POST"])
def run_summarize():
    """Generate structured multilingual meeting summary."""
    data = request.get_json(silent=True) or {}
    summary_lang = data.get("summary_language", "same")

    if not os.path.exists(TRANSCRIPT_PATH):
        return jsonify({"status": "error", "message": "No transcript.txt found. Please run Speech-to-Text first."}), 400

    try:
        result = generate_summary(summary_language=summary_lang)
        return jsonify({
            "status": "success",
            "message": f"Meeting summary generated successfully in {result['language_name']}!",
            "summary": result["summary"],
            "language": result["language"],
            "language_name": result["language_name"],
            "action_items": result.get("action_items", []),
            "decisions": result.get("decisions", [])
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Summarization failed: {str(e)}"}), 500


@app.route("/api/action_items", methods=["POST"])
def run_action_items():
    """Extract action items and decisions on demand."""
    data = request.get_json(silent=True) or {}
    target_lang = data.get("language", "en")

    state = get_persisted_state()
    transcript = state.get("original_transcript", "")

    if not transcript and os.path.exists(TRANSCRIPT_PATH):
        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            transcript = f.read()

    if not transcript:
        return jsonify({"status": "error", "message": "No transcript available."}), 400

    try:
        result = extract_action_items(transcript, output_language=target_lang)
        update_persisted_state(result)
        return jsonify({
            "status": "success",
            "action_items": result["action_items"],
            "decisions": result["decisions"]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Action items extraction failed: {str(e)}"}), 500


# ============================================================
# API - EMAIL DRAFTING & PRIORITIZATION
# ============================================================

@app.route("/api/generate_email", methods=["POST"])
def run_generate_email():
    """Generate professional follow-up email draft with priority classification."""
    data = request.get_json(silent=True) or {}
    email_lang = data.get("email_language", "en")

    state = get_persisted_state()
    transcript = state.get("original_transcript", "")
    summary = state.get("summary_text", "")
    action_items = state.get("action_items", [])

    if not transcript and os.path.exists(TRANSCRIPT_PATH):
        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            transcript = f.read()

    if not transcript:
        return jsonify({"status": "error", "message": "No transcript available to draft email."}), 400

    try:
        draft = draft_followup_email(transcript, summary, action_items, email_language=email_lang)
        return jsonify({
            "status": "success",
            "message": "Follow-up email drafted successfully!",
            "email_draft": draft
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Email drafting failed: {str(e)}"}), 500


# ============================================================
# API - PDF REPORT GENERATION
# ============================================================

@app.route("/api/generate_report", methods=["POST"])
def run_generate_report():
    """Compile meeting intelligence into a print-ready Unicode PDF."""
    data = request.get_json(silent=True) or {}
    report_lang = data.get("report_language", "en")

    state = get_persisted_state()
    transcript = state.get("original_transcript", "")
    summary = state.get("summary_text", "")

    if not transcript and os.path.exists(TRANSCRIPT_PATH):
        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            transcript = f.read()

    if not summary and os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary = f.read()

    if not transcript:
        return jsonify({"status": "error", "message": "Meeting transcript missing. Please complete Speech-to-Text first."}), 400

    try:
        pdf_file = generate_pdf_report(report_language=report_lang)
        update_persisted_state({"report_language": report_lang})

        return jsonify({
            "status": "success",
            "message": "Unicode PDF Meeting Report generated successfully!",
            "download_url": "/download"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"PDF generation failed: {str(e)}"}), 500


# ============================================================
# API - COLLEGE DEMO MODE
# ============================================================

@app.route("/api/load_demo", methods=["POST"])
def run_load_demo():
    """
    Load a pre-configured multilingual meeting dataset for instant college viva demonstration.
    Populates transcript, summary, action items, email draft, and triggers PDF generation.
    """
    data = request.get_json(silent=True) or {}
    scenario_id = data.get("scenario_id", "telugu_project")

    scenario = get_demo_scenario(scenario_id)

    try:
        # Write files
        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(scenario["transcript"])

        with open(TRANSLATED_PATH, "w", encoding="utf-8") as f:
            f.write(scenario.get("translation_en", ""))

        with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
            f.write(scenario["summary"])

        with open(EMAIL_PATH, "w", encoding="utf-8") as f:
            draft = scenario["email_draft"]
            f.write(f"Subject: {draft['subject']}\nPriority: {draft['priority']}\nRecipients: {draft['recipients']}\n\n{draft['body']}")

        # Save to state JSON
        update_persisted_state({
            "original_transcript": scenario["transcript"],
            "detected_language": scenario["language_code"],
            "detected_language_name": scenario["language_name"],
            "transcription_confidence": 0.98,
            "duration": scenario["duration"],
            "word_count": len(scenario["transcript"].split()),
            "translated_transcript": scenario.get("translation_en", ""),
            "translation_language": "en",
            "translation_language_name": "English",
            "summary_text": scenario["summary"],
            "summary_language": scenario["language_code"],
            "summary_language_name": scenario["language_name"],
            "action_items": scenario["action_items"],
            "decisions": scenario["decisions"],
            "email_draft": scenario["email_draft"],
            "report_language": scenario["language_code"]
        })

        # Generate Unicode PDF in meeting language
        generate_pdf_report(report_language=scenario["language_code"])

        return jsonify({
            "status": "success",
            "message": f"Demo scenario '{scenario['title']}' loaded successfully!",
            "scenario": scenario
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to load demo scenario: {str(e)}"}), 500


@app.route("/api/reset", methods=["POST"])
def run_reset():
    """Reset meeting session for a new recording."""
    try:
        for fpath in [WAV_PATH, TRANSCRIPT_PATH, TRANSLATED_PATH, SUMMARY_PATH, PDF_PATH, EMAIL_PATH, STATE_PATH]:
            if os.path.exists(fpath):
                os.remove(fpath)

        with state_lock:
            async_task_state["status"] = "idle"
            async_task_state["stage"] = ""
            async_task_state["progress"] = ""
            async_task_state["error"] = None

        return jsonify({"status": "success", "message": "Session reset successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Reset failed: {str(e)}"}), 500


# ============================================================
# DOWNLOAD & VIEW ROUTES
# ============================================================

@app.route("/download")
@app.route("/download/pdf")
@app.route("/download/Meeting_Report.pdf")
def download_pdf():
    """Download Meeting_Report.pdf with strict Content-Disposition and MIME headers."""
    if not os.path.exists(PDF_PATH):
        try:
            generate_pdf_report(report_language="en")
        except Exception as e:
            return f"PDF report could not be generated: {e}", 500

    if os.path.exists(PDF_PATH):
        response = send_file(
            PDF_PATH,
            as_attachment=True,
            download_name="Meeting_Report.pdf",
            mimetype="application/pdf"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="Meeting_Report.pdf"'
        response.headers["Content-Type"] = "application/pdf"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return "PDF report not found.", 404


@app.route("/view/pdf")
@app.route("/view/Meeting_Report.pdf")
def view_pdf():
    """View Meeting_Report.pdf inline inside the browser."""
    if os.path.exists(PDF_PATH):
        response = send_file(
            PDF_PATH,
            as_attachment=False,
            download_name="Meeting_Report.pdf",
            mimetype="application/pdf"
        )
        response.headers["Content-Disposition"] = 'inline; filename="Meeting_Report.pdf"'
        response.headers["Content-Type"] = "application/pdf"
        return response
    return "PDF report not found. Please generate report first.", 404


@app.route("/download/transcript")
@app.route("/download/transcript/meeting_transcript.txt")
def download_transcript():
    if os.path.exists(TRANSCRIPT_PATH):
        response = send_file(
            TRANSCRIPT_PATH,
            as_attachment=True,
            download_name="meeting_transcript.txt",
            mimetype="text/plain; charset=utf-8"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="meeting_transcript.txt"'
        return response
    return "Transcript not found.", 404


@app.route("/download/translated")
@app.route("/download/translated/translated_transcript.txt")
def download_translated():
    if os.path.exists(TRANSLATED_PATH):
        response = send_file(
            TRANSLATED_PATH,
            as_attachment=True,
            download_name="translated_transcript.txt",
            mimetype="text/plain; charset=utf-8"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="translated_transcript.txt"'
        return response
    return "Translated transcript not found.", 404


@app.route("/download/summary")
@app.route("/download/summary/meeting_summary.txt")
def download_summary():
    if os.path.exists(SUMMARY_PATH):
        response = send_file(
            SUMMARY_PATH,
            as_attachment=True,
            download_name="meeting_summary.txt",
            mimetype="text/plain; charset=utf-8"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="meeting_summary.txt"'
        return response
    return "Summary not found.", 404


@app.route("/download/email")
@app.route("/download/email/followup_email.txt")
def download_email():
    if os.path.exists(EMAIL_PATH):
        response = send_file(
            EMAIL_PATH,
            as_attachment=True,
            download_name="followup_email.txt",
            mimetype="text/plain; charset=utf-8"
        )
        response.headers["Content-Disposition"] = 'attachment; filename="followup_email.txt"'
        return response
    return "Email draft not found.", 404



# ============================================================
# PRODUCTION SERVER ENTRY
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=False)