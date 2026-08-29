from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("meetings/Meeting_Report.pdf")
styles = getSampleStyleSheet()
story = []

# Title
story.append(Paragraph("<b>SMART MEETING RECORDER REPORT</b>", styles["Title"]))

# Read Transcript
with open("meetings/transcript.txt", "r", encoding="utf-8") as file:
    transcript = file.read()

story.append(Paragraph("<b>Transcript:</b>", styles["Heading2"]))
story.append(Paragraph(transcript, styles["BodyText"]))

# Read Summary
with open("meetings/summary.txt", "r", encoding="utf-8") as file:
    summary = file.read()

story.append(Paragraph("<b>Summary:</b>", styles["Heading2"]))
story.append(Paragraph(summary, styles["BodyText"]))

# Generate PDF
doc.build(story)

print("Meeting_Report.pdf created successfully!")