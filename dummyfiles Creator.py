import os
import random
from datetime import datetime, timedelta

# CHANGE THIS PATH to where you want the messy folder
MESSY_FOLDER = os.path.expanduser("~/Desktop/messy_folder")

# File types to generate
FILE_TYPES = [
    # (extension, category, realistic names)
    ('.pdf', ['report', 'invoice', 'contract', 'proposal', 'manual', 'guide', 'summary', 'draft']),
    ('.jpg', ['photo', 'image', 'screenshot', 'selfie', 'vacation', 'pic', 'snap', 'family']),
    ('.png', ['logo', 'icon', 'graphic', 'banner', 'chart', 'diagram', 'screenshot', 'design']),
    ('.xlsx', ['budget', 'spreadsheet', 'data', 'sales', 'expenses', 'forecast', 'tracking', 'Q4']),
    ('.docx', ['document', 'letter', 'resume', 'notes', 'outline', 'draft', 'memo', 'cover_letter']),
    ('.csv', ['export', 'data', 'contacts', 'inventory', 'logs', 'results', 'backup', 'records']),
    ('.txt', ['notes', 'readme', 'todo', 'ideas', 'scratch', 'log', 'output', 'temp']),
    ('.mp3', ['song', 'audio', 'recording', 'podcast', 'voice_memo', 'track', 'interview', 'lecture']),
    ('.mp4', ['video', 'recording', 'tutorial', 'clip', 'meeting', 'presentation', 'walkthrough', 'demo']),
    ('.zip', ['archive', 'backup', 'project', 'files', 'old_stuff', 'download', 'package', 'bundle']),
]

# Create the messy folder
os.makedirs(MESSY_FOLDER, exist_ok=True)

print(f"Creating messy files in: {MESSY_FOLDER}\n")

file_count = 0

# Generate random files
for ext, name_list in FILE_TYPES:
    # Create 20-40 files of each type
    num_files = random.randint(20, 40)
    
    for i in range(num_files):
        base_name = random.choice(name_list)
        
        # Add variations to make it messy
        variation = random.choice([
            f"_{random.randint(1, 999)}",
            f" ({random.randint(2000, 2025)})",
            f"_v{random.randint(1,5)}",
            f"_FINAL",
            f"_COPY",
            f" ({random.choice(['final', 'draft', 'old', 'new', 'updated', 'revised'])})",
            f" - Copy",
            "",
        ])
        
        filename = f"{base_name}{variation}{ext}"
        filepath = os.path.join(MESSY_FOLDER, filename)
        
        # Skip if already exists
        if os.path.exists(filepath):
            continue
        
        # Create the file with random size
        size_kb = random.randint(1, 5000)  # 1KB to 5MB
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * (size_kb * 1024))
        
        # Set random modified date (within last 2 years)
        days_ago = random.randint(0, 730)
        mod_time = datetime.now() - timedelta(days=days_ago)
        timestamp = mod_time.timestamp()
        os.utime(filepath, (timestamp, timestamp))
        
        file_count += 1

# Also create some empty folders to make it messier
folder_names = ['Old Projects', 'Temp', 'Stuff', 'Misc', 'Archive', 'From Laptop', 'Backup']
for name in folder_names:
    os.makedirs(os.path.join(MESSY_FOLDER, name), exist_ok=True)
    # Put a few random files inside each subfolder too
    for _ in range(random.randint(2, 8)):
        ext, name_list = random.choice(FILE_TYPES)
        filename = f"{random.choice(name_list)}_{random.randint(1,99)}{ext}"
        filepath = os.path.join(MESSY_FOLDER, name, filename)
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * random.randint(1, 500) * 1024)

print(f" Created {file_count} messy files in '{MESSY_FOLDER}'")
print(f" Created {len(folder_names)} subfolders with extra files")
print("\nOpen this folder now — it should look satisfyingly chaotic.")