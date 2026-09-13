"""
FILE AUTOMATION ENGINE
Organizes messy folders by file type with full error handling and logging.
Built for Week 1 — Python for Automation
"""

import os
import shutil
import logging
from datetime import datetime, timedelta

# ============================================
# CONFIGURATION
# ============================================

# CHANGE THIS to your messy folder path
FOLDER_TO_ORGANIZE = os.path.expanduser("~/Desktop/messy_folder")

# Define where each file type goes
CATEGORIES = {
    'PDFs': ['.pdf'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'Spreadsheets': ['.xlsx', '.xls', '.csv', '.tsv'],
    'Documents': ['.docx', '.doc', '.txt', '.rtf', '.odt', '.pages'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
    'Video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Code': ['.py', '.js', '.html', '.css', '.json', '.xml', '.sql', '.ipynb'],
    'Presentations': ['.ppt', '.pptx', '.key', '.odp'],
}

# Files over this size get flagged (in MB)
LARGE_FILE_THRESHOLD_MB = 100

# Files modified within this many days go to "Recent" folder
RECENT_DAYS = 7

# Set up logging
logging.basicConfig(
    filename='file_organizer.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_category(filename):
    """
    Determine which category a file belongs to based on its extension.
    Returns 'Others' if no match found.
    """
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'Others'


def get_file_size_mb(filepath):
    """Get file size in megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)


def is_recently_modified(filepath):
    """Check if file was modified in the last RECENT_DAYS days."""
    mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    return (datetime.now() - mod_time) <= timedelta(days=RECENT_DAYS)


def send_failure_alert(error_message):
    """Display and log a critical failure alert."""
    alert = f"""
    ╔═══════════════════════════════════════╗
    ║  AUTOMATION FAILURE ALERT             ║
    ╠═══════════════════════════════════════╣
    ║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ║  Script: file_organizer.py
    ║  Error: {error_message}
    ╚═══════════════════════════════════════╝
    """
    print(alert)
    logging.critical(f"AUTOMATION FAILURE: {error_message}")


# ============================================
# MAIN ORGANIZER FUNCTION
# ============================================

def organize_folder(folder_path):
    """
    Organize all files in a folder into categorized subfolders.
    Handles duplicates, hidden files, large files, and errors.
    """
    logging.info(f"=" * 50)
    logging.info(f"STARTING ORGANIZATION: {folder_path}")
    
    # ---- VALIDATION ----
    if not os.path.exists(folder_path):
        error_msg = f"Folder not found: {folder_path}"
        logging.error(error_msg)
        send_failure_alert(error_msg)
        return {'success': False, 'error': error_msg}
    
    # ---- STATISTICS TRACKING ----
    stats = {
        'total_files': 0,
        'moved': 0,
        'skipped_hidden': 0,
        'skipped_large': 0,
        'duplicates_renamed': 0,
        'errors': [],
        'categories': {},  # Count per category
        'start_time': datetime.now()
    }
    
    try:
        # ---- CREATE CATEGORY FOLDERS ----
        for category in CATEGORIES.keys():
            cat_path = os.path.join(folder_path, category)
            os.makedirs(cat_path, exist_ok=True)
        # Also create Others folder
        os.makedirs(os.path.join(folder_path, 'Others'), exist_ok=True)
        # Create Recent folder
        os.makedirs(os.path.join(folder_path, 'Recent'), exist_ok=True)
        
        # ---- SCAN AND PROCESS EACH FILE ----
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            stats['total_files'] += 1
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Skip hidden files (starting with .)
            if filename.startswith('.'):
                logging.info(f"Skipped hidden file: {filename}")
                stats['skipped_hidden'] += 1
                continue
            
            # ---- PROCESS EACH FILE IN TRY BLOCK ----
            try:
                # Get category
                category = get_category(filename)
                
                # Determine destination folder
                dest_folder = os.path.join(folder_path, category)
                
                # Check if file is recently modified
                if is_recently_modified(file_path):
                    dest_folder = os.path.join(folder_path, 'Recent', category)
                    os.makedirs(dest_folder, exist_ok=True)
                
                destination = os.path.join(dest_folder, filename)
                
                # Check file size
                file_size_mb = get_file_size_mb(file_path)
                if file_size_mb > LARGE_FILE_THRESHOLD_MB:
                    logging.warning(f"Large file: {filename} ({file_size_mb:.1f} MB)")
                    stats['skipped_large'] += 1
                    print(f" LARGE FILE: {filename} ({file_size_mb:.1f} MB) — skipping")
                    continue
                
                # Handle duplicate filenames
                if os.path.exists(destination):
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%H%M%S')
                    new_name = f"{name}_DUPLICATE_{timestamp}{ext}"
                    destination = os.path.join(dest_folder, new_name)
                    stats['duplicates_renamed'] += 1
                    logging.info(f"Duplicate renamed: {filename} → {new_name}")
                    print(f" Duplicate: {filename} → {new_name}")
                
                # MOVE THE FILE
                shutil.move(file_path, destination)
                stats['moved'] += 1
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                print(f" {filename} → {category}/")
                
            except PermissionError:
                error_msg = f"Permission denied: {filename}"
                stats['errors'].append(error_msg)
                logging.error(error_msg)
                print(f" {error_msg}")
                
            except Exception as e:
                error_msg = f"Error moving {filename}: {str(e)}"
                stats['errors'].append(error_msg)
                logging.error(error_msg, exc_info=True)
                print(f" {error_msg}")
        
        # ---- FINALIZE STATISTICS ----
        stats['end_time'] = datetime.now()
        stats['duration_seconds'] = (stats['end_time'] - stats['start_time']).total_seconds()
        stats['success'] = True
        
    except Exception as e:
        stats['success'] = False
        stats['critical_error'] = str(e)
        logging.critical(f"CRITICAL FAILURE: {e}", exc_info=True)
        send_failure_alert(str(e))
    
    # ---- PRINT SUMMARY ----
    print("\n" + "=" * 50)
    print(" ORGANIZATION SUMMARY")
    print("=" * 50)
    print(f" Total files found: {stats['total_files']}")
    print(f" Files moved: {stats['moved']}")
    print(f" Hidden files skipped: {stats['skipped_hidden']}")
    print(f" Large files skipped: {stats['skipped_large']}")
    print(f" Duplicates renamed: {stats['duplicates_renamed']}")
    print(f" Errors: {len(stats['errors'])}")
    print(f"  Duration: {stats.get('duration_seconds', 0):.2f} seconds")
    
    if stats['categories']:
        print("\n By category:")
        for cat, count in sorted(stats['categories'].items()):
            print(f"   {cat}: {count} files")
    
    if stats['errors']:
        print("\n  Errors encountered:")
        for err in stats['errors']:
            print(f"   - {err}")
    
    print(f"\n Full log saved to: file_organizer.log")
    print("=" * 50)
    
    logging.info(f"ORGANIZATION COMPLETE: {stats['moved']} moved, {len(stats['errors'])} errors")
    
    return stats


# ============================================
# RUN IT
# ============================================

if __name__ == "__main__":
    print("\n FILE AUTOMATION ENGINE")
    print(f" Target folder: {FOLDER_TO_ORGANIZE}")
    print("\nStarting organization...\n")
    
    result = organize_folder(FOLDER_TO_ORGANIZE)
    
    if result['success']:
        print("\n Organization complete!")
    else:
        print(f"\n Organization failed: {result.get('error', 'Unknown error')}")