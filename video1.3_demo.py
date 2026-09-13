# # Bad Way
# # If the file doesn't exist, everything breaks
# file = open('data.csv')
# data = file.read()
# print(f"Read {len(data)} characters")
# file.close()

# #Good way
# try:
#     file = open('data.csv')
#     data = file.read()
#     print(f"Read {len(data)} characters")
    
# except FileNotFoundError:
#     print("data.csv not found. Using backup instead.")
#     # You could load a backup file here
    
# except PermissionError:
#     print("Cannot access data.csv. Check your permissions.")
#     # You could try an alternative path
    
# except Exception as e:
#     print(f"Unexpected error: {e}")
#     # Catches anything you didn't specifically plan for
    
# finally:
#     # This ALWAYS runs -- error or no error
#     try:
#         file.close()
#     except:
#         pass  # File was never opened, nothing to close


import os
import shutil
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='file_organizer.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Categories dictionary (same as before)
CATEGORIES = {
    'PDFs': ['.pdf'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif'],
    'Spreadsheets': ['.xlsx', '.xls', '.csv'],
    'Documents': ['.docx', '.doc', '.txt'],
    'Code': ['.py', '.js', '.html'],
}

def get_category(filename):
    """Figure out which category a file belongs to."""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'Others'

def organize_folder_safe(folder_path):
    """
    Organize files with COMPLETE error handling.
    This can run at 3 AM unattended.
    """
    logging.info(f"Starting organization: {folder_path}")
    
    # VALIDATE FIRST
    if not os.path.exists(folder_path):
        logging.error(f"Folder not found: {folder_path}")
        return {'success': False, 'error': 'Folder not found'}
    
    # Statistics tracker
    stats = {
        'total_files': 0,
        'moved': 0,
        'skipped': 0,
        'errors': [],
        'start_time': datetime.now()
    }

    try:
        # Create category folders
        for category in CATEGORIES.keys():
            cat_path = os.path.join(folder_path, category)
            os.makedirs(cat_path, exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'Others'), exist_ok=True)
        
        # Process each file
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            stats['total_files'] += 1
            
            # Skip directories
            if os.path.isdir(file_path):
                stats['skipped'] += 1
                continue
            
            # Skip hidden files
            if filename.startswith('.'):
                logging.info(f"Skipping hidden file: {filename}")
                stats['skipped'] += 1
                continue
            try:
                category = get_category(filename)
                dest_folder = os.path.join(folder_path, category)
                destination = os.path.join(dest_folder, filename)
                
                # Handle duplicates
                if os.path.exists(destination):
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%H%M%S')
                    destination = os.path.join(
                        dest_folder, 
                        f"{name}_dup_{timestamp}{ext}"
                    )
                    logging.warning(f"Duplicate renamed: {filename}")
                
                # Move the file
                shutil.move(file_path, destination)
                stats['moved'] += 1
                
            except PermissionError:
                error_msg = f"Permission denied: {filename}"
                stats['errors'].append(error_msg)
                logging.error(error_msg)
                
            except Exception as e:
                error_msg = f"Failed to move {filename}: {str(e)}"
                stats['errors'].append(error_msg)
                logging.error(error_msg)

            # Finalize statistics
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = (
            stats['end_time'] - stats['start_time']
        ).total_seconds()
        stats['success'] = True
        
        logging.info(
            f"Complete: {stats['moved']} moved, "
            f"{stats['skipped']} skipped, "
            f"{len(stats['errors'])} errors"
        )
        
    except Exception as e:
        # Catastrophic failure -- the whole thing crashed
        logging.critical(f"Critical failure: {e}", exc_info=True)
        stats['success'] = False
        stats['critical_error'] = str(e)
    
    return stats

folder = "C:/Users/zeena/Desktop/NECA ICT Academy Advanced AI 2026/practice_folder" # add your folder path here
result = organize_folder_safe(folder)

print(f"Moved: {result['moved']} | Errors: {len(result['errors'])}")
print(f"Duration: {result['duration_seconds']:.2f} seconds")

def send_failure_alert(error_message):
    """
    Send an alert when automation fails critically.
    In Week 2, we'll upgrade this to send actual emails.
    """
    alert = f"""
    AUTOMATION FAILURE ALERT
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Script: file_organizer.py
    Error: {error_message}
    Action: Manual intervention required
    """
    print(alert)
    logging.critical(f"AUTOMATION FAILURE ALERT: {error_message}")


    if not result['success']:
        send_failure_alert(result.get('critical_error', 'Unknown error occurred'))
    else:
        print(f"Success: {result['moved']} files organized in {result['duration_seconds']:.2f} seconds")