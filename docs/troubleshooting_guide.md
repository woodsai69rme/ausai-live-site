# Troubleshooting Guide for Organized Drive System

## Common Issues and Solutions

### 1. Scripts Won't Execute

#### Problem: "Access is denied" error when running scripts
**Solution:**
- Right-click the script file and select "Run as administrator"
- Check that you have write permissions to the directories the script accesses
- Temporarily disable antivirus real-time protection for the script execution

#### Problem: "Windows protected your PC" warning
**Solution:**
- Click "More info" in the warning dialog
- Click "Run anyway"
- To prevent future warnings, add the scripts folder to Windows Defender exclusions:
  1. Open Windows Security
  2. Go to Virus & threat protection
  3. Click "Add or remove exclusions"
  4. Add the C:\Users\karma folder

#### Problem: Scripts appear to run but do nothing
**Solution:**
- Check that all destination directories exist
- Verify file paths in the scripts are correct
- Ensure the scripts have not been accidentally modified

### 2. Files Not Sorting Correctly

#### Problem: Files in Downloads are not being sorted
**Solution:**
- Verify that the destination directories exist (DOCUMENTATION, MEDIA, SCRIPTS, etc.)
- Check that file extensions match what the auto_sort_script.bat expects
- Ensure you're running the script from the correct location
- Make sure the Downloads path in the script is correct (%USERPROFILE%\Downloads)

#### Problem: Some file types are not being sorted
**Solution:**
- Open the auto_sort_script.bat in a text editor
- Add the missing file extension to the appropriate section
- Example: To add .xlsx files to documents, add it to the doc/docx section

### 3. Directory Structure Issues

#### Problem: Missing directories after organization
**Solution:**
- Re-run the original organization scripts to recreate missing directories
- Check that the original organization was completed successfully
- Manually create missing directories if needed using the structure:
  - C:\Users\karma\CONFIG
  - C:\Users\karma\PROJECTS\ACTIVE
  - C:\Users\karma\PROJECTS\ARCHIVED
  - C:\Users\karma\PROJECTS\BACKUPS
  - C:\Users\karma\DOCUMENTATION
  - C:\Users\karma\SCRIPTS
  - C:\Users\karma\AI_TOOLS\CHATGPT
  - C:\Users\karma\AI_TOOLS\CLAUDE
  - C:\Users\karma\AI_TOOLS\GEMINI
  - C:\Users\karma\AI_TOOLS\GENERAL
  - C:\Users\karma\TOOLS
  - C:\Users\karma\MEDIA
  - C:\Users\karma\TEMP
  - C:\Users\karma\PERSONAL

#### Problem: X: drive directories not created
**Solution:**
- Verify that the X: drive is accessible and mounted
- Check that you have write permissions to the X: drive
- Run the organize_x_drive.bat script again with administrator privileges

### 4. Performance Issues

#### Problem: Scripts take too long to run
**Solution:**
- This is normal for large drives with many files
- The scripts will eventually complete
- Consider running scripts during off-hours
- For very large drives, consider running scripts in sections

#### Problem: System slows down during script execution
**Solution:**
- Close unnecessary applications before running scripts
- Run scripts when the system is not in heavy use
- Consider scheduling scripts during idle times

### 5. Archive Script Problems

#### Problem: Archive script doesn't find any old projects
**Solution:**
- Verify that projects exist in ACTIVE_PROJECTS directories
- Check that the age threshold (-90 days) is appropriate
- Ensure the ARCHIVED_PROJECTS destinations exist

#### Problem: Archive script fails to move projects
**Solution:**
- Check that destination directories exist
- Verify you have write permissions to both source and destination
- Ensure no programs are using the project files
- Run the script as administrator

### 6. Dashboard Issues

#### Problem: Dashboard shows incorrect item counts
**Solution:**
- This is normal if files have been added/deleted since the last run
- The counts reflect the current state
- Run the dashboard script again to refresh

#### Problem: Dashboard doesn't show X: drive information
**Solution:**
- Verify that the X: drive is connected and accessible
- Check that the X: drive directories were created successfully
- Run the organize_x_drive.bat script again if needed

### 7. Scheduled Task Issues

#### Problem: Scheduled tasks don't run
**Solution:**
- Open Task Scheduler and check the task status
- Verify the task is enabled
- Check the "Run with highest privileges" option
- Ensure the script path is correct and the file exists

#### Problem: Scheduled tasks fail with errors
**Solution:**
- Check the task history in Task Scheduler
- Verify the user account has appropriate permissions
- Ensure the script path is absolute, not relative
- Test the script manually before scheduling

### 8. General Tips

#### To reset the system:
1. Back up any important files that may have been mis-sorted
2. Delete the organizational directories (if needed)
3. Re-run the original organization scripts

#### To customize the system:
1. Make copies of scripts before modifying
2. Test modifications on a small scale first
3. Update this documentation if you make significant changes

#### For additional help:
- Refer to the individual documentation files in the docs directory
- Check the complete user manual
- Contact technical support if issues persist

### 9. Prevention Tips

- Regularly run the maintenance script to keep the system clean
- Use the auto-sort script regularly for new downloads
- Periodically run the archive script to keep active directories clean
- Keep the system dashboard handy for monitoring
- Back up important data regularly