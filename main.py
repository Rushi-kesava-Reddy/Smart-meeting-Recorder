"""
CLI Orchestration Workflow for Multilingual AI Smart Meeting Recorder.
Executes the full pipeline: Audio Recording -> Multilingual STT -> Translation ->
Summarization & Action Extraction -> Email Drafting -> Unicode PDF Generation.
"""

import os
import sys
import subprocess

# Ensure UTF-8 output
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable

print("================================================================")
print(" MULTILINGUAL AI SMART MEETING RECORDER & ASSISTANT ")
print("================================================================")

# Allow passing language as CLI arg (e.g. 'python main.py te' or 'python main.py auto')
target_lang = sys.argv[1] if len(sys.argv) > 1 else "auto"
print(f"Target Language Mode: {target_lang}\n")

# Step 1: Check or record audio
wav_path = os.path.join(BASE_DIR, "meetings", "meeting.wav")
if not os.path.exists(wav_path):
    print("Step 1: Recording Audio (Hardware Microphone Fallback)...")
    subprocess.run([PYTHON_EXE, "recorder.py"], cwd=BASE_DIR, check=True)
else:
    print(f"Step 1: Using Existing Meeting Audio ({wav_path})")

# Step 2: Speech to Text
print("\nStep 2: Multilingual Speech-to-Text & Language Detection...")
subprocess.run([PYTHON_EXE, "speech_to_text.py", target_lang], cwd=BASE_DIR, check=True)

# Step 3: Translation (if target is not English)
print("\nStep 3: Context-Aware Translation to English...")
subprocess.run([PYTHON_EXE, "translator.py", "en"], cwd=BASE_DIR, check=True)

# Step 4: Meeting Summarization & Action Item Extraction
print("\nStep 4: Multilingual Meeting Summarization & Action Extraction...")
subprocess.run([PYTHON_EXE, "summarizer.py", "same"], cwd=BASE_DIR, check=True)

# Step 5: Follow-up Email Drafting & Priority Assessment
print("\nStep 5: Follow-Up Email Drafting & Prioritization...")
subprocess.run([PYTHON_EXE, "email_drafter.py", "en"], cwd=BASE_DIR, check=True)

# Step 6: Unicode PDF Report Generation
print("\nStep 6: Unicode PDF Report Generation (ReportLab + Google Noto TTF)...")
subprocess.run([PYTHON_EXE, "report_generator.py", "same"], cwd=BASE_DIR, check=True)

print("\n================================================================")
print(" MULTILINGUAL PIPELINE COMPLETED SUCCESSFULLY! ")
print(" Artifacts Created in meetings/:")
print("  - Transcript: meetings/transcript.txt")
print("  - Translation: meetings/translated_transcript.txt")
print("  - Summary: meetings/summary.txt")
print("  - Email Draft: meetings/email_draft.txt")
print("  - Unicode PDF: meetings/Meeting_Report.pdf")
print("================================================================")