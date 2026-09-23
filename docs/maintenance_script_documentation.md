# Maintenance Script Documentation
# File: maintenance_script.bat

## Purpose
The maintenance script performs regular cleanup and monitoring tasks to keep your organized drives running smoothly. It cleans temporary directories, checks disk space, and provides recommendations for ongoing maintenance.

## Features
- Cleans TEMP directories on both C:\Users\karma and X: drives
- Checks and reports disk space usage
- Provides recommendations for ongoing maintenance
- Can be scheduled to run automatically

## How to Use
1. Double-click the maintenance_script.bat file to run it
2. Alternatively, run it from Command Prompt by navigating to the directory and typing: `maintenance_script.bat`
3. The script will display progress and results
4. Review the recommendations at the end of the run

## Scheduling for Automatic Runs
To schedule this script to run automatically:
1. Press Win+R, type "taskschd.msc", and press Enter
2. Click "Create Basic Task" in the right panel
3. Give it a name like "Drive Maintenance"
4. Choose a schedule (weekly recommended)
5. For the action, select "Start a program"
6. Browse to the maintenance_script.bat file
7. Finish the wizard

## Customization
You can modify the script to:
- Add more cleanup tasks
- Change which directories are cleaned
- Add additional monitoring features

## Safety Notes
- The script only deletes files in TEMP directories
- It does not move or delete any other files
- Always review the script before running if you've made modifications