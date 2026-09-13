import os

practice_folder = os.path.expanduser("~/Desktop/neca ict academy 2026 advanced ai class/practice_folder")
os.makedirs(practice_folder, exist_ok=True)

files = [
    "report.pdf",
    "vacation_photo.jpg",
    "budget_2025.xlsx",
    "meeting_notes.docx",
    "screenshot.png",
    "data_export.csv",
    "song.mp3",
    "readme.txt",
    "logo.jpg",
    "weird_file.xyz"  # No extension match — goes to Others
]

for f in files:
    filepath = os.path.join(practice_folder, f)
    with open(filepath, 'w') as file:
        file.write("sample content")
    print(f"Created: {f}")

print(f"\n Created {len(files)} files in practice_folder")