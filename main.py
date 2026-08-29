import os

print("===================================")
print(" SMART MEETING RECORDER ")
print("===================================")

print("\nStep 1: Recording Audio")
os.system("python recorder.py")

print("\nStep 2: Speech to Text")
os.system("python speech_to_text.py")

print("\nStep 3: Meeting Summary")
os.system("python summarizer.py")

print("\nStep 4: Generate PDF Report")
os.system("python report_generator.py")

print("\nProject Completed Successfully!")