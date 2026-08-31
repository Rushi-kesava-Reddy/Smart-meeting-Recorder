import os
import re
import html

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm


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

PDF_PATH = os.path.join(
    MEETINGS_DIR,
    "Meeting_Report.pdf"
)


# ============================================================
# CREATE MEETINGS FOLDER
# ============================================================

os.makedirs(
    MEETINGS_DIR,
    exist_ok=True
)


# ============================================================
# PDF DOCUMENT
# ============================================================

doc = SimpleDocTemplate(
    PDF_PATH,
    pagesize=A4,
    rightMargin=20 * mm,
    leftMargin=20 * mm,
    topMargin=20 * mm,
    bottomMargin=20 * mm
)


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()


title_style = ParagraphStyle(
    "ReportTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    alignment=TA_CENTER,
    spaceAfter=18
)


section_style = ParagraphStyle(
    "SectionHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    spaceBefore=10,
    spaceAfter=8
)


subheading_style = ParagraphStyle(
    "SubHeading",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    spaceBefore=7,
    spaceAfter=5
)


body_style = ParagraphStyle(
    "ReportBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=15,
    spaceAfter=7
)


bullet_style = ParagraphStyle(
    "ReportBullet",
    parent=body_style,
    leftIndent=15,
    firstLineIndent=-8,
    spaceAfter=5
)


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    """
    Convert problematic Unicode characters into
    PDF-safe characters.
    """

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u2022": "-",
        "\u00a0": " ",
        "\u2026": "...",
        "\u2192": "->",
        "\u2190": "<-",
        "\u2010": "-",
        "\u200b": "",
        "\ufeff": ""
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# ESCAPE PDF HTML
# ============================================================

def safe_text(text):
    """
    Escape characters that have special meaning
    inside ReportLab Paragraph.
    """

    text = clean_text(text)

    return html.escape(
        text,
        quote=False
    )


# ============================================================
# ADD TRANSCRIPT
# ============================================================

def add_transcript(story, transcript):

    story.append(
        Paragraph(
            "Transcript",
            section_style
        )
    )

    transcript = clean_text(
        transcript
    ).strip()

    # Split transcript into paragraphs
    paragraphs = re.split(
        r"\n\s*\n",
        transcript
    )

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # Keep normal line breaks readable
        paragraph = paragraph.replace(
            "\n",
            "<br/>"
        )

        story.append(
            Paragraph(
                safe_text(paragraph).replace(
                    "\n",
                    "<br/>"
                ),
                body_style
            )
        )


# ============================================================
# ADD SUMMARY
# ============================================================

def add_summary(story, summary):

    story.append(
        Paragraph(
            "Summary",
            section_style
        )
    )

    # Clean Unicode first
    summary = clean_text(
        summary
    ).strip()

    # Split summary line by line
    lines = summary.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            story.append(
                Spacer(1, 4)
            )
            continue

        # ----------------------------------------------------
        # Remove Markdown bold markers
        # ----------------------------------------------------

        line = line.replace(
            "**",
            ""
        )

        # ----------------------------------------------------
        # Markdown headings
        # ----------------------------------------------------

        if line.startswith("#"):

            heading = line.lstrip(
                "#"
            ).strip()

            if heading:

                story.append(
                    Paragraph(
                        safe_text(heading),
                        subheading_style
                    )
                )

            continue

        # ----------------------------------------------------
        # Bullet points
        # ----------------------------------------------------

        if re.match(
            r"^[-*]\s+",
            line
        ):

            bullet_text = re.sub(
                r"^[-*]\s+",
                "",
                line
            ).strip()

            story.append(
                Paragraph(
                    "&#8226; "
                    + safe_text(bullet_text),
                    bullet_style
                )
            )

            continue

        # ----------------------------------------------------
        # Numbered points
        # ----------------------------------------------------

        numbered_match = re.match(
            r"^(\d+)[.)]\s+(.*)",
            line
        )

        if numbered_match:

            number = numbered_match.group(1)

            text = numbered_match.group(2)

            story.append(
                Paragraph(
                    f"<b>{number}.</b> "
                    + safe_text(text),
                    body_style
                )
            )

            continue

        # ----------------------------------------------------
        # Normal line
        # ----------------------------------------------------

        story.append(
            Paragraph(
                safe_text(line),
                body_style
            )
        )


# ============================================================
# BUILD PDF
# ============================================================

def generate_report():

    print(
        "===== PDF REPORT GENERATION STARTED ====="
    )


    # --------------------------------------------------------
    # Check transcript
    # --------------------------------------------------------

    if not os.path.exists(
        TRANSCRIPT_PATH
    ):

        raise FileNotFoundError(
            "Transcript file not found: "
            + TRANSCRIPT_PATH
        )


    # --------------------------------------------------------
    # Check summary
    # --------------------------------------------------------

    if not os.path.exists(
        SUMMARY_PATH
    ):

        raise FileNotFoundError(
            "Summary file not found: "
            + SUMMARY_PATH
        )


    # --------------------------------------------------------
    # Read transcript
    # --------------------------------------------------------

    with open(
        TRANSCRIPT_PATH,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        transcript = file.read().strip()


    # --------------------------------------------------------
    # Read summary
    # --------------------------------------------------------

    with open(
        SUMMARY_PATH,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        summary = file.read().strip()


    # --------------------------------------------------------
    # Validate files
    # --------------------------------------------------------

    if not transcript:

        raise ValueError(
            "Transcript file is empty."
        )


    if not summary:

        raise ValueError(
            "Summary file is empty."
        )


    print(
        f"[1] Transcript loaded: "
        f"{len(transcript)} characters"
    )

    print(
        f"[2] Summary loaded: "
        f"{len(summary)} characters"
    )


    # --------------------------------------------------------
    # Create story
    # --------------------------------------------------------

    story = []


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "SMART MEETING RECORDER REPORT",
            title_style
        )
    )

    story.append(
        Spacer(1, 5)
    )


    # --------------------------------------------------------
    # TRANSCRIPT
    # --------------------------------------------------------

    add_transcript(
        story,
        transcript
    )


    # --------------------------------------------------------
    # SPACE
    # --------------------------------------------------------

    story.append(
        Spacer(1, 10)
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    add_summary(
        story,
        summary
    )


    # --------------------------------------------------------
    # GENERATE PDF
    # --------------------------------------------------------

    doc.build(
        story
    )


    print(
        "[3] PDF generated successfully!"
    )

    print(
        f"[4] PDF location: {PDF_PATH}"
    )

    print(
        "===== PDF REPORT GENERATION COMPLETED ====="
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        generate_report()

    except Exception as error:

        print(
            "[ERROR] PDF generation failed:"
        )

        print(
            str(error)
        )