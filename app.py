import os
import sys
import subprocess
import threading

from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify
)
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK APP CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smart_meeting_recorder_default_secret_key_change_in_production"
)


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")

# Create meetings folder if it does not exist
os.makedirs(MEETINGS_DIR, exist_ok=True)


# ============================================================
# TRANSCRIPTION STATE
# ============================================================

transcription_lock = threading.Lock()

transcription_state = {
    "status": "idle",
    "progress": "",
    "error": None,
    "transcript": ""
}


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for Render/cloud monitoring.
    """

    return jsonify({
        "status": "ok",
        "service": "Smart Meeting Recorder",
        "message": "Service is healthy and running"
    }), 200


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):
    """
    Handle 404 errors.
    """

    if request.path.startswith("/api/"):
        return jsonify({
            "status": "error",
            "message": "API endpoint not found"
        }), 404

    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """
    Handle internal server errors without exposing
    sensitive stack traces.
    """

    if request.path.startswith("/api/"):
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred"
        }), 500

    return jsonify({
        "status": "error",
        "message": "An internal server error occurred"
    }), 500


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


@app.route("/report")
def report_page():
    return render_template("report.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/modules")
def modules_page():
    return render_template("modules.html")


# ============================================================
# API - GET STATUS
# ============================================================

@app.route("/api/status", methods=["GET"])
def get_status():
    """
    Return status of:
    - Audio
    - Transcript
    - Summary
    - PDF
    - Transcription process
    """

    wav_path = os.path.join(
        MEETINGS_DIR,
        "meeting.wav"
    )

    transcript_path = os.path.join(
        MEETINGS_DIR,
        "transcript.txt"
    )

    summary_path = os.path.join(
        MEETINGS_DIR,
        "summary.txt"
    )

    pdf_path = os.path.join(
        MEETINGS_DIR,
        "Meeting_Report.pdf"
    )

    # --------------------------------------------------------
    # Read transcript
    # --------------------------------------------------------

    transcript_text = ""

    if os.path.exists(transcript_path):
        try:
            with open(
                transcript_path,
                "r",
                encoding="utf-8"
            ) as file:
                transcript_text = file.read()

        except Exception:
            transcript_text = ""


    # --------------------------------------------------------
    # Read summary
    # --------------------------------------------------------

    summary_text = ""

    if os.path.exists(summary_path):
        try:
            with open(
                summary_path,
                "r",
                encoding="utf-8"
            ) as file:
                summary_text = file.read()

        except Exception:
            summary_text = ""


    # --------------------------------------------------------
    # Get transcription state safely
    # --------------------------------------------------------

    with transcription_lock:

        stt_status = transcription_state["status"]

        stt_error = transcription_state["error"]

        stt_progress = transcription_state["progress"]

        if (
            stt_status == "completed"
            and transcription_state["transcript"]
        ):
            transcript_text = transcription_state["transcript"]


    # --------------------------------------------------------
    # Return status
    # --------------------------------------------------------

    return jsonify({
        "has_audio": os.path.exists(wav_path),

        "has_transcript": (
            os.path.exists(transcript_path)
            or bool(transcript_text)
        ),

        "has_summary": os.path.exists(summary_path),

        "has_pdf": os.path.exists(pdf_path),

        "transcript": transcript_text,

        "summary": summary_text,

        "transcription_status": stt_status,

        "transcription_error": stt_error,

        "transcription_progress": stt_progress
    })


# ============================================================
# API - SAVE AUDIO
# ============================================================

@app.route("/api/save_audio", methods=["POST"])
def save_audio():
    """
    Save recorded audio from browser microphone
    to meetings/meeting.wav
    """

    if "audio_file" not in request.files:

        return jsonify({
            "status": "error",
            "message": "No audio file provided in request."
        }), 400


    file = request.files["audio_file"]


    if file.filename == "":

        return jsonify({
            "status": "error",
            "message": "Empty file uploaded."
        }), 400


    try:

        audio_path = os.path.join(
            MEETINGS_DIR,
            "meeting.wav"
        )

        file.save(audio_path)


        # Reset transcription state
        with transcription_lock:

            transcription_state["status"] = "idle"

            transcription_state["error"] = None

            transcription_state["progress"] = ""

            transcription_state["transcript"] = ""


        return jsonify({
            "status": "success",
            "message": "Recording Completed Successfully",
            "filename": "meeting.wav"
        })


    except Exception as error:

        return jsonify({
            "status": "error",
            "message": f"Failed to save audio file: {str(error)}"
        }), 500


# ============================================================
# API - SERVER RECORDING
# ============================================================

@app.route("/api/record_server", methods=["POST"])
def record_server():
    """
    Alternative recording method using recorder.py.
    """

    recorder_script = os.path.join(
        BASE_DIR,
        "recorder.py"
    )


    if not os.path.exists(recorder_script):

        return jsonify({
            "status": "error",
            "message": "recorder.py script not found."
        }), 404


    try:

        result = subprocess.run(
            [
                sys.executable,
                recorder_script
            ],
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )


        with transcription_lock:

            transcription_state["status"] = "idle"

            transcription_state["error"] = None

            transcription_state["progress"] = ""

            transcription_state["transcript"] = ""


        return jsonify({
            "status": "success",
            "message": "Recording Completed Successfully",
            "stdout": result.stdout
        })


    except subprocess.CalledProcessError as error:

        return jsonify({
            "status": "error",
            "message": (
                "Hardware recording failed: "
                f"{error.stderr or str(error)}"
            )
        }), 500


# ============================================================
# TRANSCRIPTION WORKER
# ============================================================

def run_transcription_worker():
    """
    Run speech_to_text.py in a background thread.
    """

    script_path = os.path.join(
        BASE_DIR,
        "speech_to_text.py"
    )


    if not os.path.exists(script_path):

        with transcription_lock:

            transcription_state["status"] = "error"

            transcription_state["error"] = (
                "speech_to_text.py not found."
            )

            transcription_state["progress"] = (
                "Transcription failed"
            )

        return


    try:

        result = subprocess.run(
            [
                sys.executable,
                script_path
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )


        if result.stdout:

            print(result.stdout)


        if result.returncode == 0:

            transcript_path = os.path.join(
                MEETINGS_DIR,
                "transcript.txt"
            )

            transcript_text = ""


            if os.path.exists(transcript_path):

                with open(
                    transcript_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    transcript_text = file.read()


            with transcription_lock:

                transcription_state["status"] = "completed"

                transcription_state["progress"] = (
                    "Transcription completed successfully"
                )

                transcription_state["error"] = None

                transcription_state["transcript"] = (
                    transcript_text
                )


        else:

            error_message = (
                result.stderr
                or result.stdout
                or "Unknown transcription error"
            ).strip()


            print(
                f"[ERROR] Transcription process failed: "
                f"{error_message}",
                file=sys.stderr
            )


            with transcription_lock:

                transcription_state["status"] = "error"

                transcription_state["error"] = (
                    f"Transcription failed: {error_message}"
                )

                transcription_state["progress"] = (
                    "Error during transcription"
                )


    except Exception as error:

        print(
            f"[ERROR] Exception running transcription worker: "
            f"{error}",
            file=sys.stderr
        )


        with transcription_lock:

            transcription_state["status"] = "error"

            transcription_state["error"] = str(error)

            transcription_state["progress"] = (
                "Exception during transcription"
            )


# ============================================================
# API - TRANSCRIBE
# ============================================================

@app.route("/api/transcribe", methods=["POST"])
def run_transcribe():
    """
    Start speech-to-text transcription in background.
    """

    wav_path = os.path.join(
        MEETINGS_DIR,
        "meeting.wav"
    )

    script_path = os.path.join(
        BASE_DIR,
        "speech_to_text.py"
    )


    print(
        "\n--------------------------------------------------"
    )

    print("[1] Transcription requested")


    # --------------------------------------------------------
    # Check audio
    # --------------------------------------------------------

    if not os.path.exists(wav_path):

        error_message = (
            "No meeting.wav found! "
            "Please record audio first."
        )

        print(
            f"[ERROR] {error_message}"
        )


        with transcription_lock:

            transcription_state["status"] = "error"

            transcription_state["error"] = error_message

            transcription_state["progress"] = ""


        return jsonify({
            "status": "error",
            "message": error_message
        }), 400


    print(
        f"[2] Audio file found: {wav_path}"
    )


    # --------------------------------------------------------
    # Check transcription script
    # --------------------------------------------------------

    if not os.path.exists(script_path):

        error_message = (
            "speech_to_text.py not found."
        )

        print(
            f"[ERROR] {error_message}"
        )


        with transcription_lock:

            transcription_state["status"] = "error"

            transcription_state["error"] = error_message

            transcription_state["progress"] = ""


        return jsonify({
            "status": "error",
            "message": error_message
        }), 404


    # --------------------------------------------------------
    # Check current state
    # --------------------------------------------------------

    with transcription_lock:

        if transcription_state["status"] == "processing":

            return jsonify({
                "status": "processing",
                "message": (
                    "Transcription is already in progress."
                ),
                "transcription_status": "processing"
            })


        transcription_state["status"] = "processing"

        transcription_state["progress"] = (
            "Starting transcription..."
        )

        transcription_state["error"] = None

        transcription_state["transcript"] = ""


    # --------------------------------------------------------
    # Start background thread
    # --------------------------------------------------------

    worker_thread = threading.Thread(
        target=run_transcription_worker,
        daemon=True
    )

    worker_thread.start()


    return jsonify({
        "status": "success",
        "message": "Transcription process started.",
        "transcription_status": "processing"
    })


# ============================================================
# API - SUMMARIZE
# ============================================================

@app.route("/api/summarize", methods=["POST"])
def run_summarize():
    """
    Generate meeting summary using summarizer.py.
    """

    transcript_path = os.path.join(
        MEETINGS_DIR,
        "transcript.txt"
    )

    script_path = os.path.join(
        BASE_DIR,
        "summarizer.py"
    )


    if not os.path.exists(transcript_path):

        return jsonify({
            "status": "error",
            "message": (
                "No transcript.txt found! "
                "Please convert speech to text first."
            )
        }), 400


    if not os.path.exists(script_path):

        return jsonify({
            "status": "error",
            "message": "summarizer.py not found."
        }), 404


    try:

        result = subprocess.run(
            [
                sys.executable,
                script_path
            ],
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )


        summary_path = os.path.join(
            MEETINGS_DIR,
            "summary.txt"
        )

        summary_text = ""


        if os.path.exists(summary_path):

            with open(
                summary_path,
                "r",
                encoding="utf-8"
            ) as file:

                summary_text = file.read()


        return jsonify({
            "status": "success",
            "message": (
                "Meeting summary generated successfully!"
            ),
            "summary": summary_text,
            "stdout": result.stdout
        })


    except subprocess.CalledProcessError as error:

        return jsonify({
            "status": "error",
            "message": (
                "Summarization failed: "
                f"{error.stderr or str(error)}"
            )
        }), 500


# ============================================================
# API - GENERATE REPORT
# ============================================================

@app.route("/api/generate_report", methods=["POST"])
def run_generate_report():
    """
    Generate Meeting_Report.pdf using report_generator.py.
    """

    transcript_path = os.path.join(
        MEETINGS_DIR,
        "transcript.txt"
    )

    summary_path = os.path.join(
        MEETINGS_DIR,
        "summary.txt"
    )

    script_path = os.path.join(
        BASE_DIR,
        "report_generator.py"
    )


    if (
        not os.path.exists(transcript_path)
        or not os.path.exists(summary_path)
    ):

        return jsonify({
            "status": "error",
            "message": (
                "Missing transcript or summary! "
                "Please complete Modules 2 & 3 first."
            )
        }), 400


    if not os.path.exists(script_path):

        return jsonify({
            "status": "error",
            "message": (
                "report_generator.py not found."
            )
        }), 404


    try:

        result = subprocess.run(
            [
                sys.executable,
                script_path
            ],
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )


        pdf_path = os.path.join(
            MEETINGS_DIR,
            "Meeting_Report.pdf"
        )


        if os.path.exists(pdf_path):

            return jsonify({
                "status": "success",
                "message": (
                    "Report Generated Successfully"
                ),
                "download_url": "/download"
            })


        return jsonify({
            "status": "error",
            "message": (
                "PDF file was not created by "
                "report_generator.py."
            )
        }), 500


    except subprocess.CalledProcessError as error:

        return jsonify({
            "status": "error",
            "message": (
                "Report generation failed: "
                f"{error.stderr or str(error)}"
            )
        }), 500


# ============================================================
# DOWNLOAD PDF
# ============================================================

@app.route("/download")
def download_pdf():
    """
    Download generated Meeting_Report.pdf.
    """

    pdf_path = os.path.join(
        MEETINGS_DIR,
        "Meeting_Report.pdf"
    )


    if os.path.exists(pdf_path):

        return send_file(
            pdf_path,
            as_attachment=True,
            download_name="Meeting_Report.pdf",
            mimetype="application/pdf"
        )


    return (
        "PDF report not found. "
        "Please generate report first.",
        404
    )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )