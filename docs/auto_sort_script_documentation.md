# Auto-Sort Script Documentation
# File: auto_sort_script.bat

## Purpose
The auto-sort script automatically organizes files from your Downloads folder into the appropriate directories in your organized system. It identifies file types and moves them to their designated locations.

## Features
- Sorts documents to DOCUMENTATION directory
- Moves images to MEDIA directory
- Moves videos to MEDIA directory
- Moves audio files to MEDIA directory
- Moves scripts to SCRIPTS directory
- Moves executables and archives to TOOLS directory
- Prevents re-processing of already sorted files

## How to Use
1. Place files in your Downloads folder
2. Run auto_sort_script.bat by double-clicking it
3. The script will move files to appropriate directories
4. Any remaining files will be temporarily moved to a processed folder and then deleted

## Supported File Types
### Documents
- PDF (.pdf)
- Word documents (.doc, .docx)
- Text files (.txt)
- Rich Text Format (.rtf)
- Markdown (.md)

### Media
- Images (.jpg, .jpeg, .png, .gif, .bmp, .svg)
- Videos (.mp4, .avi, .mov, .wmv, .mkv)
- Audio (.mp3, .wav, .flac, .aac)

### Scripts
- Python (.py)
- JavaScript (.js)
- Batch (.bat)
- Shell (.sh)
- TypeScript (.ts, .tsx)

### Tools
- Executables (.exe)
- Installers (.msi)
- Archives (.zip, .rar, .7z, .tar, .gz)

## Scheduling for Automatic Runs
To schedule this script to run automatically:
1. Press Win+R, type "taskschd.msc", and press Enter
2. Click "Create Basic Task" in the right panel
3. Give it a name like "Auto-Sort Downloads"
4. Choose a schedule (daily recommended)
5. For the action, select "Start a program"
6. Browse to the auto_sort_script.bat file
7. Finish the wizard

## Customization
You can modify the script to:
- Add support for additional file types
- Change destination directories
- Adjust file filtering criteria

## Safety Notes
- The script only moves files from the Downloads folder
- It does not delete files directly, only moves them
- Always review the script before running if you've made modifications
- Files that don't match any criteria will be moved to a temporary folder and then deleted