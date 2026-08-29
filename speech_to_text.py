import os
import sys
import whisper

# Model cache
model = None


def load_whisper_model():
    global model

    if model is None:
        # Use tiny model for faster transcription
        model_name = os.environ.get("WHISPER_MODEL", "tiny")

        print(f"[1] Loading Whisper model: {model_name}")

        try:
            model = whisper.load_model(model_name)
            print("[2] Whisper model loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load Whisper model: {e}", file=sys.stderr)
            return None

    return model


def transcribe_audio(wav_path):
    """
    Convert audio file to text.
    Returns the transcript text.
    """

    if not os.path.exists(wav_path):
        print(f"[ERROR] Audio file not found: {wav_path}", file=sys.stderr)
        return None

    print(f"[3] Audio file found: {wav_path}")

    whisper_model = load_whisper_model()

    if whisper_model is None:
        return None

    try:
        print("[4] Starting transcription...")

        result = whisper_model.transcribe(
            wav_path,
            language="en",
            fp16=False,
            verbose=False
        )

        transcript_text = result.get("text", "").strip()

        print("[5] Transcription completed successfully")

        return transcript_text

    except Exception as e:
        print(f"[ERROR] Whisper transcription failed: {e}", file=sys.stderr)
        return None


def main():
    print("===== SPEECH TO TEXT STARTED =====")

    wav_path = os.path.join("meetings", "meeting.wav")
    transcript_path = os.path.join("meetings", "transcript.txt")

    # Transcribe audio
    transcript_text = transcribe_audio(wav_path)

    if transcript_text is None:
        print("[ERROR] Transcription failed", file=sys.stderr)
        sys.exit(1)

    # Create meetings folder if needed
    os.makedirs(os.path.dirname(transcript_path), exist_ok=True)

    # Save transcript
    try:
        with open(transcript_path, "w", encoding="utf-8") as file:
            file.write(transcript_text)

        print(f"[6] Transcript saved successfully: {transcript_path}")

    except Exception as e:
        print(f"[ERROR] Failed to save transcript: {e}", file=sys.stderr)
        sys.exit(1)

    print("===== SPEECH TO TEXT COMPLETED =====")
    print("\n--- TRANSCRIPT ---")
    print(transcript_text)
    print("------------------")


if __name__ == "__main__":
    main()