import os
import sys

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FIX WINDOWS TERMINAL UTF-8 ENCODING
# ============================================================

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
except Exception:
    pass


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MEETINGS_DIR = os.path.join(
    BASE_DIR,
    "meetings"
)

TRANSCRIPT_PATH = os.path.join(
    MEETINGS_DIR,
    "transcript.txt"
)

SUMMARY_PATH = os.path.join(
    MEETINGS_DIR,
    "summary.txt"
)


# ============================================================
# CREATE MEETINGS DIRECTORY
# ============================================================

os.makedirs(
    MEETINGS_DIR,
    exist_ok=True
)


# ============================================================
# GROQ API CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

if not GROQ_API_KEY:

    raise RuntimeError(
        "GROQ_API_KEY is not configured. "
        "Please add GROQ_API_KEY to your .env file."
    )


# ============================================================
# CREATE GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# AI MODEL
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# GENERATE SUMMARY
# ============================================================

def generate_summary():

    print(
        "===== MEETING SUMMARIZATION STARTED ====="
    )


    # --------------------------------------------------------
    # CHECK TRANSCRIPT FILE
    # --------------------------------------------------------

    if not os.path.exists(
        TRANSCRIPT_PATH
    ):

        raise FileNotFoundError(
            "Transcript file not found: "
            + TRANSCRIPT_PATH
            + "\nPlease complete Speech-to-Text first."
        )


    # --------------------------------------------------------
    # READ TRANSCRIPT
    # --------------------------------------------------------

    with open(
        TRANSCRIPT_PATH,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        transcript = file.read().strip()


    # --------------------------------------------------------
    # CHECK EMPTY TRANSCRIPT
    # --------------------------------------------------------

    if not transcript:

        raise ValueError(
            "Transcript file is empty. "
            "Please complete Speech-to-Text first."
        )


    print(
        f"[1] Transcript loaded successfully "
        f"({len(transcript)} characters)"
    )


    # --------------------------------------------------------
    # SHOW SHORT PREVIEW
    # --------------------------------------------------------

    preview = transcript[:150]

    if len(transcript) > 150:

        preview += "..."


    print(
        "[1.1] Transcript preview:"
    )

    print(
        preview.encode(
            "utf-8",
            errors="replace"
        ).decode(
            "utf-8",
            errors="replace"
        )
    )


    # --------------------------------------------------------
    # SEND TRANSCRIPT TO GROQ
    # --------------------------------------------------------

    print(
        f"[2] Sending transcript to AI model: "
        f"{MODEL_NAME}"
    )


    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[

            {
                "role": "system",

                "content": (
                    "You are a professional meeting "
                    "summarization assistant.\n\n"

                    "Create a clear, concise and "
                    "professional summary of the meeting.\n\n"

                    "Use the following sections when "
                    "information is available:\n\n"

                    "1. Meeting Summary\n"
                    "2. Key Discussion Points\n"
                    "3. Completed Work\n"
                    "4. Important Decisions\n"
                    "5. Action Items\n"
                    "6. Next Steps\n\n"

                    "Only use information that is actually "
                    "present in the transcript.\n"

                    "Do not invent names, dates, decisions, "
                    "tasks, or other information.\n"

                    "If a section has no relevant information, "
                    "write 'None mentioned.'"
                )
            },

            {
                "role": "user",

                "content": (
                    "Please summarize the following "
                    "meeting transcript:\n\n"
                    + transcript
                )
            }

        ],

        temperature=0.3,

        max_tokens=1200
    )


    # --------------------------------------------------------
    # CHECK AI RESPONSE
    # --------------------------------------------------------

    if not response.choices:

        raise RuntimeError(
            "The AI model returned no response."
        )


    # --------------------------------------------------------
    # EXTRACT SUMMARY
    # --------------------------------------------------------

    summary = response.choices[0].message.content


    if summary is None:

        raise RuntimeError(
            "The AI model returned an empty summary."
        )


    summary = summary.strip()


    if not summary:

        raise RuntimeError(
            "The AI model returned an empty summary."
        )


    print(
        "[3] AI summary generated successfully"
    )


    # --------------------------------------------------------
    # SAVE SUMMARY TO FILE
    # --------------------------------------------------------

    with open(
        SUMMARY_PATH,
        "w",
        encoding="utf-8",
        errors="replace"
    ) as file:

        file.write(summary)


    print(
        "[4] Summary saved successfully: "
        + SUMMARY_PATH
    )


    # --------------------------------------------------------
    # DISPLAY SUMMARY SAFELY
    # --------------------------------------------------------

    print()
    print("--- SUMMARY ---")

    try:

        print(summary)

    except UnicodeEncodeError:

        safe_summary = summary.encode(
            "ascii",
            errors="replace"
        ).decode(
            "ascii"
        )

        print(
            safe_summary
        )

    print(
        "------------------"
    )


    print(
        "===== MEETING SUMMARIZATION COMPLETED ====="
    )


    return summary


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    try:

        generate_summary()


    except Exception as error:

        print()

        print(
            "[ERROR] Summarization failed: "
            + str(error)
        )

        sys.exit(1)