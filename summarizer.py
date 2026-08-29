import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Read transcript
with open("meetings/transcript.txt", "r", encoding="utf-8") as file:
    transcript = file.read()

# Check transcript
if not transcript.strip():
    print("Transcript is empty!")
    exit()

# Generate summary
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are a professional meeting summarizer."
        },
        {
            "role": "user",
            "content": f"""
Summarize the following meeting transcript.

Give the output in this format:

MEETING SUMMARY
- Main discussion points
- Project progress
- Important decisions

ACTION ITEMS
- Tasks to be completed
- Future improvements

NEXT STEPS
- What should happen next

Keep the summary clear and concise.

Meeting transcript:
{transcript}
"""
        }
    ],
    temperature=0.3
)

summary = response.choices[0].message.content

# Display summary
print("\n===== MEETING SUMMARY =====\n")
print(summary)

# Save summary
with open("meetings/summary.txt", "w", encoding="utf-8") as file:
    file.write(summary)

print("\nSummary saved successfully to meetings/summary.txt")