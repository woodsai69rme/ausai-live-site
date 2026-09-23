# Archive Old Projects Script Documentation
# File: archive_old_projects.bat

## Purpose
The archive old projects script identifies projects that haven't been modified recently and offers to move them to archived directories. This helps keep active project directories clean and organized.

## Features
- Scans ACTIVE_PROJECTS directories on both drives
- Identifies projects not modified in the last 90 days
- Prompts for confirmation before moving each project
- Moves projects to appropriate archived directories
- Works on both C:\Users\karma\PROJECTS\ACTIVE and X:\DEVELOPMENT\ACTIVE_PROJECTS

## How to Use
1. Run archive_old_projects.bat by double-clicking it
2. The script will scan for projects older than 90 days
3. For each old project found, you'll be prompted to confirm archiving
4. Type 'y' to archive or 'n' to skip
5. Archived projects will be moved to the appropriate ARCHIVED directory

## Configuration
The script currently looks for projects older than 90 days. To change this:
1. Open the script in a text editor
2. Find the line with "-90" (appears twice)
3. Change the number to your desired threshold (e.g., -60 for 60 days)
4. Save the file

## Archive Locations
- C:\Users\karma\PROJECTS\ACTIVE → C:\Users\karma\PROJECTS\ARCHIVED
- X:\DEVELOPMENT\ACTIVE_PROJECTS → X:\DEVELOPMENT\ARCHIVED_PROJECTS

## Scheduling for Automatic Runs
To schedule this script to run automatically:
1. Press Win+R, type "taskschd.msc", and press Enter
2. Click "Create Basic Task" in the right panel
3. Give it a name like "Archive Old Projects"
4. Choose a schedule (monthly recommended)
5. For the action, select "Start a program"
6. Browse to the archive_old_projects.bat file
7. Finish the wizard

## Customization
You can modify the script to:
- Change the age threshold for archiving
- Add additional project directories to scan
- Modify the confirmation prompts

## Safety Notes
- The script prompts for confirmation before moving each project
- Projects are only moved, not deleted
- Always review the script before running if you've made modifications
- Make sure the destination ARCHIVED directories exist before running