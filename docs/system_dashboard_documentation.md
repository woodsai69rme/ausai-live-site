# System Dashboard Script Documentation
# File: system_dashboard.bat

## Purpose
The system dashboard script provides an overview of your organized drive system. It displays the status of all organizational directories, disk space information, and available maintenance tools.

## Features
- Shows status of all organizational directories on C:\Users\karma
- Shows status of all organizational directories on X: drive
- Displays disk space usage for both drives
- Lists available maintenance scripts
- Provides recommendations for ongoing maintenance
- Counts items in each organizational directory

## How to Use
1. Run system_dashboard.bat by double-clicking it
2. The script will display the status of all directories
3. Review the disk space information
4. Check the list of available maintenance scripts
5. Review the recommendations at the end

## Information Displayed
### C:\Users\karma Status
- CONFIG directory status and item count
- PROJECTS directory status and item count
- DOCUMENTATION directory status and item count
- SCRIPTS directory status and item count
- AI_TOOLS directory status and item count
- TEMP directory status and item count

### X: Drive Status
- AI_MODELS directory status and item count
- DEVELOPMENT directory status and item count
- CONTENT_CREATION directory status and item count
- TOOLS directory status and item count
- VIRTUAL_MACHINES directory status and item count

### Disk Space Information
- C: drive space usage
- X: drive space usage

### Available Scripts
- Lists all maintenance scripts with their purposes

## Scheduling for Automatic Runs
To schedule this script to run automatically:
1. Press Win+R, type "taskschd.msc", and press Enter
2. Click "Create Basic Task" in the right panel
3. Give it a name like "System Dashboard"
4. Choose a schedule (weekly recommended)
5. For the action, select "Start a program"
6. Browse to the system_dashboard.bat file
7. Finish the wizard

## Customization
You can modify the script to:
- Add additional directories to monitor
- Change the information displayed
- Modify the recommendation section

## Safety Notes
- The script only reads information, it doesn't modify any files
- Safe to run at any time
- Always review the script before running if you've made modifications