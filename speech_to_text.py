import os
import sys
from groq import Groq


def transcribe_audio(wav_path):
    """
    Convert audio file to text using Groq Whisper API.
    """

    if not os.path.exists(wav_path):
        print(f"[ERROR] Audio file not found: {wav_path}", file=sys.stderr)
        return None

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print("[ERROR] GROQ_API_KEY is not set", file=sys.stderr)
        return None

    print(f"[1] Audio file found: {wav_path}")

    try:
        client = Groq(api_key=api_key)

        print("[2] Sending audio to Groq Whisper...")

        with open(wav_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                language="en",
                response_format="json",
                temperature=0.0
            )

        transcript_text = transcription.text.strip()

        print("[3] Transcription completed successfully")

        return transcript_text

    except Exception as e:
        print(f"[ERROR] Groq transcription failed: {e}", file=sys.stderr)
        return None


def main():

    print("===== SPEECH TO TEXT STARTED =====")

    wav_path = os.path.join("meetings", "meeting.wav")
    transcript_path = os.path.join("meetings", "transcript.txt")

    transcript_text = transcribe_audio(wav_path)

    if transcript_text is None:
        print("[ERROR] Transcription failed", file=sys.stderr)
        sys.exit(1)

    os.makedirs("meetings", exist_ok=True)

    try:
        with open(transcript_path, "w", encoding="utf-8") as file:
            file.write(transcript_text)

        print(f"[4] Transcript saved: {transcript_path}")

    except Exception as e:
        print(f"[ERROR] Failed to save transcript: {e}", file=sys.stderr)
        sys.exit(1)

    print("===== SPEECH TO TEXT COMPLETED =====")
    print("\n--- TRANSCRIPT ---")
    print(transcript_text)
    print("------------------")


if __name__ == "__main__":
    main()