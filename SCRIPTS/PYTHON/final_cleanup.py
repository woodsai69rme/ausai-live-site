import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_cleanup_log.txt'),
        logging.StreamHandler()
    ]
)

SYSTEM_CORE_FILES = [
    "AI_ARMY_MANAGER.py",
    "AI_VOICE_ASSISTANT.py",
    "master_organization_system.py",
    "GITHUB_REPO_MANAGER.py",
    "RUN_GITHUB_MANAGER.bat",
    "agent_system_config.ini",
    "system_config.json",
    "automated_documentation.py",
    "maintenance_scheduler.py",
    "security_config.py",
    "AI_ECOSYSTEM_INTEGRATOR.py" # If it exists
]

PROTECTED_DIRS = {
    "AppData", "Application Data", "Contacts", "Cookies", "Desktop", "Documents", 
    "Downloads", "Favorites", "Links", "Local Settings", "Music", "My Documents", 
    "NetHood", "Pictures", "PrintHood", "Recent", "Saved Games", "Searches", 
    "SendTo", "Start Menu", "Templates", "Videos", "Windows", "Program Files", 
    "Program Files (x86)", "Users", "Intel", "PerfLogs", "ProgramData",
    "ACTIVE_PROJECTS", "COMPLETED_PROJECTS", "ARCHIVED_PROJECTS", 
    "EXPERIMENTAL", "REVENUE_GENERATORS", "SYSTEM_SCRIPTS", "DASHBOARD_SYSTEM_SCRIPTS",
    "SYSTEM_CORE", ".git", ".ssh", ".vscode", ".config", "__pycache__"
}

def move_system_core_files():
    if not os.path.exists("SYSTEM_CORE"):
        os.makedirs("SYSTEM_CORE")
        logging.info("Created SYSTEM_CORE directory")

    for file in SYSTEM_CORE_FILES:
        if os.path.exists(file):
            try:
                shutil.move(file, os.path.join("SYSTEM_CORE", file))
                logging.info(f"Moved {file} to SYSTEM_CORE")
            except Exception as e:
                logging.error(f"Failed to move {file}: {e}")

def move_unsorted_folders():
    target_dir = os.path.join("EXPERIMENTAL", "_UNSORTED")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        logging.info(f"Created {target_dir}")

    for item in os.listdir('.'):
        if os.path.isdir(item):
            if item in PROTECTED_DIRS:
                continue
            if item.startswith('.'): # Skip hidden folders
                continue
            if item.startswith('$'): # Skip system folders
                continue
            
            # Move to unsorted
            try:
                shutil.move(item, os.path.join(target_dir, item))
                logging.info(f"Moved folder '{item}' to {target_dir}")
            except Exception as e:
                logging.error(f"Failed to move folder {item}: {e}")

def create_safe_launcher():
    launcher_content = """@echo off
echo Starting Essential AI Ecosystem...
echo.

echo Launching AI Army Manager...
start /min python "SYSTEM_CORE\AI_ARMY_MANAGER.py"

echo.
echo Launching AI Voice Assistant...
start /min python "SYSTEM_CORE\AI_VOICE_ASSISTANT.py"

echo.
echo Systems started. Dashboard logic disabled for safety.
pause
"""
    with open("SAFE_START_ECOSYSTEM.bat", "w") as f:
        f.write(launcher_content)
    logging.info("Created SAFE_START_ECOSYSTEM.bat")

if __name__ == "__main__":
    move_system_core_files()
    move_unsorted_folders()
    create_safe_launcher()
