# importing os module
import os

# see what is in a folder
# files = os.listdir('/path/to/folder')

# #check if something exists
# exists = os.path.exists('/path/to/file.pdf')

# #Split (filename and extension (ext))
# name, ext = os.path.splitext('report.pdf')

# #  create folder
# os.makedirs('/path/to/new/folder', exist_ok = True)

# #move or rename
# os.rename('/old/path/file.pdf', '/new/path/file.pdf')

# # get file information(size)
# size = os.path.getsize('/path/to/file.pdf')

#Scanning a folder
import shutil
folder_path = "C:/Users/zeena/Desktop/neca ict academy 2026 advanced ai class/practice_folder" #Add your folder path here

all_items = os.listdir(folder_path)
print(f"Found {len(all_items)} items")

for item in all_items:
    item_path = os.path.join(folder_path, item)

    if os.path.isfile(item_path):
        size = os.path.getsize(item_path)
        print(f"File:{item}-({size} bytes)")
    elif os.path.isdir(item_path):
        print(f"Folder: {item}")


CATEGORIES = {"PDF": '.pdf', 'Images': ['.png','.jpg','.jpeg','.gif'], 'Spreadsheets':['.xlsx','.xls','.csv'], 'Documents':['.docx','.doc','.txt'],
              'Code':['.py','.js','.html'],
              }

#Helper Function
def get_category(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return 'Others'

for category in CATEGORIES.keys():
    os.makedirs(os.path.join(folder_path , category), exist_ok =True)
os.makedirs(os.path.join(folder_path, 'Others'), exist_ok = True)
print(f"Folder ready.\n")

moved = 0
skipped = 0

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    if os.path.isdir(file_path):
        continue
    if filename.startswith('.'):
        print(f"Skipped (hidden): {filename}")
        skipped +=1
        continue
    MAX_SIZE = 100 * 1024 * 1024
    file_size = os.path.getsize(file_path)

    if file_size > MAX_SIZE:
        size_mb = file_size / (1024 * 1024)
        print (f"Skipped(too large): {filename}({size_mb:.1f}MB)")
        skipped += 1
        continue

    category = get_category(filename)
    dest_folder = os.path.join(folder_path, category)
    destination = os.path.join(dest_folder, filename)

    if os.path.exists(destination):
        name, ext = os.path.splitext(filename)
        new_name = f"{name}_DUPLICATE{ext}"
        destination = os.path.join(dest_folder, new_name)
        print(f"DUPLICATE: {filename}-{new_name}")

    shutil.move(file_path, destination)
    moved += 1
    print(f"{filename}-{category}")

    print(f"\n{'='*50}")
    print(f"Organization Complete")
    print(f"Files moved: {moved}")
    print(f"Files Skipped: {skipped}")

