import os
import shutil
from collections import defaultdict
from pathlib import Path
import time

def get_size(path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    continue
    except OSError:
        pass
    return total_size

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def analyze_path(start_path, top_n=20):
    print(f"\n--- Analyzing: {start_path} ---")
    if not os.path.exists(start_path):
        print(f"Path not found: {start_path}")
        return

    file_sizes = []
    folder_sizes = {}
    ext_sizes = defaultdict(int)
    special_folders = {'node_modules': 0, '.git': 0, '__pycache__': 0, 'venv': 0, 'tmp': 0, 'cache': 0}
    
    start_time = time.time()
    
    # We'll use a stack-based approach for folder sizes to avoid recursion limits and improve tracking
    # But for simplicity in a quick script, we'll walk and aggregate
    
    scan_count = 0
    
    for dirpath, dirnames, filenames in os.walk(start_path):
        # Skip system folders to avoid permission errors and long hangs
        if 'Windows' in dirpath or 'Program Files' in dirpath: 
            if start_path == 'C:\\': # Only skip if scanning root
                continue
        
        folder_total = 0
        scan_count += 1
        if scan_count % 5000 == 0:
            print(f"Scanned {scan_count} folders...")

        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                size = os.path.getsize(fp)
                file_sizes.append((fp, size))
                folder_total += size
                
                ext = os.path.splitext(f)[1].lower()
                ext_sizes[ext] += size
            except OSError:
                continue
        
        # Track special folder sizes (approximate, based on name matching in path)
        path_parts = dirpath.split(os.sep)
        for special in special_folders:
            if special in path_parts:
                special_folders[special] += folder_total # Add files in this dir to the special category
        
        folder_sizes[dirpath] = folder_total
    
    # Aggregate folder sizes (bubbling up is hard in one pass, so we'll just list directories with most IMMEDIATE content for now
    # or better, simple largest files is often more actionable for immediate cleanup)
    
    print(f"Analysis complete in {time.time() - start_time:.2f}s")

    # Top Files
    print(f"\nTop {top_n} Largest Files:")
    file_sizes.sort(key=lambda x: x[1], reverse=True)
    for path, size in file_sizes[:top_n]:
        print(f"{format_size(size)} - {path}")

    # Top Extensions
    print(f"\nDisk Usage by File Type (Top 10):")
    sorted_exts = sorted(ext_sizes.items(), key=lambda x: x[1], reverse=True)
    for ext, size in sorted_exts[:10]:
        print(f"{ext or 'No Extension'}: {format_size(size)}")

    # Special Folders
    print(f"\n'Heavy' Directory Categories (Cumulative Content Found):")
    for category, size in special_folders.items():
        print(f"{category}: {format_size(size)}")

if __name__ == "__main__":
    # Scan User Directory
    user_dir = os.path.expanduser("~")
    analyze_path(user_dir)
    
    # Check X: drive
    if os.path.exists("X:\\"):
        analyze_path("X:\\")
    else:
        print("\nX: Drive not found.")
