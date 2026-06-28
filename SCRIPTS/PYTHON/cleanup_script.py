import json
import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_log.txt'),
        logging.StreamHandler()
    ]
)

# Configuration
CATEGORY_MAPPING = {
    "revenue": "REVENUE_GENERATORS",
    "active": "ACTIVE_PROJECTS",
    "experimental": "EXPERIMENTAL",
    "completed": "COMPLETED_PROJECTS",
    "archived": "ARCHIVED_PROJECTS"
}

# Protected system directories and files to NEVER move
PROTECTED_ITEMS = {
    "AppData", "Application Data", "Contacts", "Cookies", "Desktop", "Documents", 
    "Downloads", "Favorites", "Links", "Local Settings", "Music", "My Documents", 
    "NetHood", "Pictures", "PrintHood", "Recent", "Saved Games", "Searches", 
    "SendTo", "Start Menu", "Templates", "Videos", "Windows", "Program Files", 
    "Program Files (x86)", "Users", "Intel", "PerfLogs", "ProgramData",
    "NTUSER.DAT", "ntuser.dat.LOG1", "ntuser.dat.LOG2", "ntuser.ini",
    "ACTIVE_PROJECTS", "COMPLETED_PROJECTS", "ARCHIVED_PROJECTS", 
    "EXPERIMENTAL", "REVENUE_GENERATORS", "SYSTEM_SCRIPTS",
    "PROJECT_REGISTRY.json", "Project_Registry.md", "IMMEDIATE_ACTIONS.md",
    "cleanup_log.txt", "cleanup_script.py", ".git", ".gitignore", ".ssh",
    "DASHBOARD_SYSTEM_SCRIPTS", "System Volume Information", "$RECYCLE.BIN"
}

def create_directories():
    """Create the organization directories if they don't exist."""
    for folder in CATEGORY_MAPPING.values():
        if not os.path.exists(folder):
            os.makedirs(folder)
            logging.info(f"Created directory: {folder}")
    
    # Create extra folders
    if not os.path.exists("DASHBOARD_SYSTEM_SCRIPTS"):
        os.makedirs("DASHBOARD_SYSTEM_SCRIPTS")
        logging.info("Created directory: DASHBOARD_SYSTEM_SCRIPTS")

def is_safe_to_move(name):
    """Check if the directory is safe to move."""
    if name in PROTECTED_ITEMS:
        return False
    if name.startswith('.'): # Skip dotfiles/folders for now unless explicitly known
        return False
    if name.startswith('$'): # Skip system files
        return False
    return True

def move_projects_from_registry():
    """Move projects based on PROJECT_REGISTRY.json."""
    try:
        with open('PROJECT_REGISTRY.json', 'r') as f:
            registry = json.load(f)
    except FileNotFoundError:
        logging.error("PROJECT_REGISTRY.json not found!")
        return
    except json.JSONDecodeError:
        logging.error("Error decoding PROJECT_REGISTRY.json")
        return

    moved_count = 0
    
    for project in registry:
        name = project.get('name')
        category = project.get('category', 'experimental').lower() # Default to experimental if missing
        
        # Map category to folder
        target_folder = CATEGORY_MAPPING.get(category, "EXPERIMENTAL")
        
        if not name:
            continue
            
        # Check if it exists in current directory
        if os.path.exists(name):
            if is_safe_to_move(name):
                try:
                    target_path = os.path.join(target_folder, name)
                    # Handle name collision
                    if os.path.exists(target_path):
                        logging.warning(f"Target already exists: {target_path}. Skipping {name}")
                        continue
                        
                    shutil.move(name, target_path)
                    logging.info(f"Moved '{name}' to '{target_folder}'")
                    moved_count += 1
                except Exception as e:
                    logging.error(f"Failed to move {name}: {e}")
            else:
                logging.debug(f"Skipping protected/unsafe item: {name}")
        else:
            # logging.debug(f"Project not found in root: {name}")
            pass

    logging.info(f"Registry cleanup complete. Moved {moved_count} items.")

def cleanup_dashboard_scripts():
    """Move loose dashboard python scripts to DASHBOARD_SYSTEM_SCRIPTS."""
    # List of keywords or files to move
    keywords = [
        "audit", "dashboard", "consolidation", "verification", "validation",
        "implementation", "system_documentation", "ecosystem", "generator",
        "report", "summary", "test_suite", "monitor"
    ]
    
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    
    moved_count = 0
    for file in files:
        if not file.endswith('.py') and not file.endswith('.json') and not file.endswith('.md') and not file.endswith('.txt'):
            continue
            
        if file in PROTECTED_ITEMS:
            continue
            
        # Check if it looks like a dashboard script
        if any(keyword in file.lower() for keyword in keywords):
             # Double check it's not a critical config file
            if file == "PROJECT_REGISTRY.json" or file == "IMMEDIATE_ACTIONS.md":
                continue
                
            try:
                shutil.move(file, os.path.join("DASHBOARD_SYSTEM_SCRIPTS", file))
                logging.info(f"Moved script '{file}' to DASHBOARD_SYSTEM_SCRIPTS")
                moved_count += 1
            except Exception as e:
                logging.error(f"Failed to move script {file}: {e}")
                
    logging.info(f"Dashboard scripts cleanup complete. Moved {moved_count} files.")

if __name__ == "__main__":
    logging.info("Starting cleanup process...")
    create_directories()
    move_projects_from_registry()
    cleanup_dashboard_scripts()
    logging.info("Cleanup process finished.")
