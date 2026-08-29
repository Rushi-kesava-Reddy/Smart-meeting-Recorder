import os
import sys
import whisper

def main():
    print("[1] Transcription requested")
    
    wav_path = os.path.join("meetings", "meeting.wav")
    transcript_path = os.path.join("meetings", "transcript.txt")
    
    if not os.path.exists(wav_path):
        print("[ERROR] Audio file not found: meetings/meeting.wav", file=sys.stderr)
        sys.exit(1)
        
    print(f"[2] Audio file found: {wav_path}")
    
    # Use 'tiny' by default for fast local CPU inference; can be overridden via WHISPER_MODEL env var
    model_name = os.environ.get("WHISPER_MODEL", "tiny")
    print(f"[3] Loading Whisper model ('{model_name}')")
    
    try:
        model = whisper.load_model(model_name)
        print(f"[4] Whisper model '{model_name}' loaded successfully")
    except Exception as e:
        print(f"[ERROR] Failed to load Whisper model: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("[5] Starting transcription...")
    try:
        # fp16=False avoids CPU FP16 warnings and optimizes CPU execution speed
        result = model.transcribe(wav_path, language="en", fp16=False)
        transcript_text = result.get("text", "").strip()
        print("[6] Transcription completed")
    except Exception as e:
        print(f"[ERROR] Whisper transcription failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"\n--- Transcript Output ---\n{transcript_text}\n-------------------------\n")
    
    os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(transcript_text)
        
    print(f"[7] Transcript saved to {transcript_path}")

if __name__ == "__main__":
    main()