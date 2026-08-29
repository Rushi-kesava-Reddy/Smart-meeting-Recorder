import os
import sys
import subprocess
import threading
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smart_meeting_recorder_default_secret_key_change_in_production")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")

# Ensure meetings directory exists
os.makedirs(MEETINGS_DIR, exist_ok=True)

# Global thread-safe state for speech-to-text transcription
transcription_lock = threading.Lock()
transcription_state = {
    "status": "idle",       # "idle", "processing", "completed", "error"
    "progress": "",
    "error": None,
    "transcript": ""
}


# ==============================================================================
# HEALTH CHECK & ERROR HANDLERS
# ==============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for cloud load balancers and automated monitoring."""
    return jsonify({
        "status": "ok",
        "service": "Smart Meeting Recorder",
        "message": "Service is healthy and running"
    }), 200


@app.errorhandler(404)
def page_not_found(e):
    """Secure 404 error handler."""
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "API endpoint not found"}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Secure 500 error handler avoiding exposing stack traces."""
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "An internal server error occurred"}), 500
    return jsonify({"status": "error", "message": "An internal server error occurred"}), 500


# ==============================================================================
# PAGE ROUTES
# ==============================================================================

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


@app.route("/report")
def report_page():
    return render_template("report.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/modules")
def modules_page():
    return render_template("modules.html")


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/status", methods=["GET"])
def get_status():
    """Return status of all meeting artifacts (audio, transcript, summary, PDF) and background job states."""
    wav_path = os.path.join(MEETINGS_DIR, "meeting.wav")
    transcript_path = os.path.join(MEETINGS_DIR, "transcript.txt")
    summary_path = os.path.join(MEETINGS_DIR, "summary.txt")
    pdf_path = os.path.join(MEETINGS_DIR, "Meeting_Report.pdf")

    transcript_text = ""
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_text = f.read()
        except Exception:
            pass

    summary_text = ""
    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()
        except Exception:
            pass

    with transcription_lock:
        stt_status = transcription_state["status"]
        stt_error = transcription_state["error"]
        stt_progress = transcription_state["progress"]
        if stt_status == "completed" and transcription_state["transcript"]:
            transcript_text = transcription_state["transcript"]

    return jsonify({
        "has_audio": os.path.exists(wav_path),
        "has_transcript": os.path.exists(transcript_path) or bool(transcript_text),
        "has_summary": os.path.exists(summary_path),
        "has_pdf": os.path.exists(pdf_path),
        "transcript": transcript_text,
        "summary": summary_text,
        "transcription_status": stt_status,
        "transcription_error": stt_error,
        "transcription_progress": stt_progress
    })


@app.route("/api/save_audio", methods=["POST"])
def save_audio():
    """Save recorded audio blob from browser microphone to meetings/meeting.wav."""
    if "audio_file" not in request.files:
        return jsonify({"status": "error", "message": "No audio file provided in request."}), 400

    file = request.files["audio_file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Empty file uploaded."}), 400

    try:
        audio_path = os.path.join(MEETINGS_DIR, "meeting.wav")
        file.save(audio_path)
        
        # Reset STT state for fresh recording
        with transcription_lock:
            transcription_state["status"] = "idle"
            transcription_state["error"] = None
            transcription_state["progress"] = ""

        return jsonify({
            "status": "success",
            "message": "Recording Completed Successfully",
            "filename": "meeting.wav"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save audio file: {str(e)}"}), 500


@app.route("/api/record_server", methods=["POST"])
def record_server():
    """Module 1 Alternative: Trigger backend hardware microphone recording via recorder.py."""
    recorder_script = os.path.join(BASE_DIR, "recorder.py")
    if not os.path.exists(recorder_script):
        return jsonify({"status": "error", "message": "recorder.py script not found."}), 404

    try:
        result = subprocess.run(
            [sys.executable, recorder_script],
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        with transcription_lock:
            transcription_state["status"] = "idle"
            transcription_state["error"] = None

        return jsonify({
            "status": "success",
            "message": "Recording Completed Successfully",
            "stdout": result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"Hardware recording failed: {e.stderr or str(e)}"}), 500


def run_transcription_worker():
    """Background worker function executing speech_to_text.py with thread safety."""
    script_path = os.path.join(BASE_DIR, "speech_to_text.py")
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            transcript_path = os.path.join(MEETINGS_DIR, "transcript.txt")
            transcript_text = ""
            if os.path.exists(transcript_path):
                with open(transcript_path, "r", encoding="utf-8") as f:
                    transcript_text = f.read()

            with transcription_lock:
                transcription_state["status"] = "completed"
                transcription_state["progress"] = "Transcription completed successfully"
                transcription_state["error"] = None
                transcription_state["transcript"] = transcript_text
        else:
            err_msg = (result.stderr or result.stdout or "Unknown transcription error").strip()
            print(f"[ERROR] Transcription process failed: {err_msg}", file=sys.stderr)
            with transcription_lock:
                transcription_state["status"] = "error"
                transcription_state["error"] = f"Transcription failed: {err_msg}"
                transcription_state["progress"] = "Error during transcription"

    except Exception as e:
        print(f"[ERROR] Exception running transcription worker: {e}", file=sys.stderr)
        with transcription_lock:
            transcription_state["status"] = "error"
            transcription_state["error"] = str(e)
            transcription_state["progress"] = "Exception during transcription"


@app.route("/api/transcribe", methods=["POST"])
def run_transcribe():
    """Module 2: Start background transcription via speech_to_text.py with status tracking."""
    wav_path = os.path.join(MEETINGS_DIR, "meeting.wav")
    script_path = os.path.join(BASE_DIR, "speech_to_text.py")

    print("\n--------------------------------------------------")
    print("[1] Transcription requested")

    if not os.path.exists(wav_path):
        err_msg = "No meeting.wav found! Please record audio first."
        print(f"[ERROR] {err_msg}")
        with transcription_lock:
            transcription_state["status"] = "error"
            transcription_state["error"] = err_msg
        return jsonify({"status": "error", "message": err_msg}), 400

    print(f"[2] Audio file found: {wav_path}")

    if not os.path.exists(script_path):
        err_msg = "speech_to_text.py not found."
        print(f"[ERROR] {err_msg}")
        with transcription_lock:
            transcription_state["status"] = "error"
            transcription_state["error"] = err_msg
        return jsonify({"status": "error", "message": err_msg}), 404

    with transcription_lock:
        if transcription_state["status"] == "processing":
            return jsonify({
                "status": "processing",
                "message": "Transcription is already in progress.",
                "transcription_status": "processing"
            })

        transcription_state["status"] = "processing"
        transcription_state["progress"] = "Starting transcription..."
        transcription_state["error"] = None

    # Spawn background thread to prevent blocking Flask HTTP response
    worker_thread = threading.Thread(target=run_transcription_worker, daemon=True)
    worker_thread.start()

    return jsonify({
        "status": "success",
        "message": "Transcription process started.",
        "transcription_status": "processing"
    })



@app.route("/api/summarize", methods=["POST"])
def run_summarize():
    """Module 3: Call summarizer.py to generate meeting summary into meetings/summary.txt."""
    transcript_path = os.path.join(MEETINGS_DIR, "transcript.txt")
    script_path = os.path.join(BASE_DIR, "summarizer.py")

    if not os.path.exists(transcript_path):
        return jsonify({
            "status": "error",
            "message": "No transcript.txt found! Please convert speech to text first."
        }), 400

    if not os.path.exists(script_path):
        return jsonify({"status": "error", "message": "summarizer.py not found."}), 404

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        summary_path = os.path.join(MEETINGS_DIR, "summary.txt")
        summary_text = ""
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()

        return jsonify({
            "status": "success",
            "message": "Meeting summary generated successfully!",
            "summary": summary_text,
            "stdout": result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": f"Summarization failed: {e.stderr or str(e)}"
        }), 500


@app.route("/api/generate_report", methods=["POST"])
def run_generate_report():
    """Module 4: Call report_generator.py to create meetings/Meeting_Report.pdf."""
    transcript_path = os.path.join(MEETINGS_DIR, "transcript.txt")
    summary_path = os.path.join(MEETINGS_DIR, "summary.txt")
    script_path = os.path.join(BASE_DIR, "report_generator.py")

    if not os.path.exists(transcript_path) or not os.path.exists(summary_path):
        return jsonify({
            "status": "error",
            "message": "Missing transcript or summary! Please complete Modules 2 & 3 first."
        }), 400

    if not os.path.exists(script_path):
        return jsonify({"status": "error", "message": "report_generator.py not found."}), 404

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        pdf_path = os.path.join(MEETINGS_DIR, "Meeting_Report.pdf")
        pdf_exists = os.path.exists(pdf_path)

        if pdf_exists:
            return jsonify({
                "status": "success",
                "message": "Report Generated Successfully",
                "download_url": "/download"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "PDF file was not created by report_generator.py."
            }), 500

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": f"Report generation failed: {e.stderr or str(e)}"
        }), 500


@app.route("/download")
def download_pdf():
    """Serve Meeting_Report.pdf for direct browser download."""
    pdf_path = os.path.join(MEETINGS_DIR, "Meeting_Report.pdf")
    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name="Meeting_Report.pdf",
            mimetype="application/pdf"
        )
    else:
        return "PDF report not found. Please generate report first.", 404


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug_mode, host=host, port=port)

