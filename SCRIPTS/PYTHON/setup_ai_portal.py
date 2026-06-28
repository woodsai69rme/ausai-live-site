import os
import json
import shutil
from pathlib import Path

# Config
SOURCE_ROOT = r"C:\Users\karma"
PORTAL_ROOT = r"C:\Users\karma\ai_portal"
SCAN_FILE = "full_scan_output.json"

# Directory Mapping
DIRS = {
    "Crypto projects": "crypto_dashboards",
    "AI voice assistants": "voice_assistant",
    "Foot Clan AI agents": "agents",
    "Social media / Influencer": "social_media_dashboard",
    "RAG / Knowledge Base": "knowledge_base",
    "Automation & control": "automation_scripts",
    "Utilities / Helpers": "utilities",
    "Unclassified": "scripts", # Move loose scripts here
    "Documentation": "docs"
}

# Files to NEVER move (Safety whitelist)
EXCLUDE_FILES = {
    "full_scan_output.json", "full_scan_summary.md", "setup_ai_portal.py", "portal_launcher.py",
    "NTUSER.DAT", "ntuser.ini", "desktop.ini", "explorer.exe"
}
EXCLUDE_PREFIXES = {".", "NTUSER", "ntuser"}

def setup_portal():
    print(f"Creating AI Portal structure in {PORTAL_ROOT}...")
    
    # 1. Create Directories
    for key, folder in DIRS.items():
        path = os.path.join(PORTAL_ROOT, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Created: {path}")

    # 2. Load Scan Data
    if not os.path.exists(SCAN_FILE):
        print(f"Error: {SCAN_FILE} not found. Run system audit first.")
        return

    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, dict) and "projects" in data:
            items = data["projects"]
        else:
            items = data

    # 3. Organize / Cleanup (Moving loose scripts)
    moved_count = 0
    
    print("\nStarting Cleanup of Root Directory...")
    for item in items:
        # Only move items that are:
        # 1. In the source root
        # 2. Standalone Scripts or Unclassified
        # 3. NOT in the exclusion list
        
        original_path = item['path']
        if not os.path.exists(original_path):
            continue
            
        is_in_root = os.path.dirname(original_path).lower() == SOURCE_ROOT.lower()
        is_script = item.get("project_type") == "Standalone Script" or item.get("category") == "Unclassified"
        filename = os.path.basename(original_path)
        
        if is_in_root and is_script:
            # Safety Checks
            if filename in EXCLUDE_FILES:
                continue
            if any(filename.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            if filename.lower().endswith((".bat", ".lnk", ".url")): # Keep shortcuts/bats in root for convenience? Maybe move .py/.js
                # Let's move .py, .js, .ts, .json, .md
                if not filename.lower().endswith((".py", ".js", ".ts", ".json", ".md", ".txt")):
                    continue
            
            # Determine target category
            category = item.get("category", "Unclassified")
            target_folder = DIRS.get(category, "scripts")
            target_path = os.path.join(PORTAL_ROOT, target_folder, filename)
            
            try:
                shutil.move(original_path, target_path)
                print(f"Moved: {filename} -> {target_folder}/")
                moved_count += 1
                
                # Update path in the item dict for the launcher (optional, strictly we'd re-scan)
                item['path'] = target_path
            except Exception as e:
                print(f"Failed to move {filename}: {e}")

    print(f"\nCleanup Complete. Moved {moved_count} files.")

    # 4. Create Portal Launcher
    launcher_code = f'''import json
import os
import sys
import subprocess

PORTAL_ROOT = r"{PORTAL_ROOT}"
SCAN_FILE = r"{os.path.abspath(SCAN_FILE)}"

def load_projects():
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, dict) and "projects" in data:
            return data["projects"]
        return data

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    projects = load_projects()
    
    while True:
        clear()
        print("=========================================")
        print("   🔮  AI PORTAL ORCHESTRATOR  🔮")
        print("=========================================")
        print(f"Total Resources: {{len(projects)}}")
        print("\nCategories:")
        
        categories = sorted(list(set(p.get('category', 'Unclassified') for p in projects)))
        for i, cat in enumerate(categories):
            count = len([p for p in projects if p.get('category') == cat])
            print(f"{{i + 1}}. {{cat}} ({{count}})")
            
        print("\nQ. Quit")
        print(f"Total Resources: {{len(projects)}}")
        print("\nCategories:")
        
        categories = sorted(list(set(p.get('category', 'Unclassified') for p in projects)))
        for i, cat in enumerate(categories):
            count = len([p for p in projects if p.get('category') == cat])
            print(f"{{i + 1}}. {{cat}} ({{count}})")
            
        print("\nQ. Quit")
        choice = input(f"\nSelect a category (1-{{len(categories)}}): ")
        
        if choice.lower() == 'q':
            break
            
        try:
            cat_idx = int(choice) - 1
            selected_cat = categories[cat_idx]
            
            # Sub-menu for category
            cat_projects = [p for p in projects if p.get('category') == selected_cat]
            while True:
                clear()
                print(f"=== {{selected_cat}} ===")
                for j, p in enumerate(cat_projects[:20]): # Show top 20
                    print(f"{{j + 1}}. {{p['project_name']}}")
                if len(cat_projects) > 20:
                    print(f"... and {{len(cat_projects) - 20}} more")
                    
                print("\n0. Back")
                p_choice = input("Select a project to inspect/launch: ")
                
                if p_choice == '0':
                    break
                    
                try:
                    p_idx = int(p_choice) - 1
                    proj = cat_projects[p_idx]
                    
                    print(f"\nProject: {{proj['project_name']}}")
                    print(f"Path: {{proj['path']}}")
                    print(f"Type: {{proj['project_type']}}")
                    print(f"Entry: {{', '.join(proj.get('main_files', []))}}")
                    
                    if proj.get('project_type') == "Standalone Script":
                        run = input("\nRun this script? (y/n): ")
                        if run.lower() == 'y':
                            # Detect runner
                            if proj['path'].endswith('.py'):
                                subprocess.run(['python', proj['path']])
                            elif proj['path'].endswith('.js'):
                                subprocess.run(['node', proj['path']])
                            else:
                                os.startfile(proj['path'])
                            input("\nPress Enter to continue...")
                    else:
                        opn = input("\nOpen folder? (y/n): ")
                        if opn.lower() == 'y':
                            os.startfile(proj['path'])
                            
                except (ValueError, IndexError):
                    pass
                    
        except (ValueError, IndexError):
            pass

if __name__ == "__main__":
    main()
'''
    
    with open(os.path.join(PORTAL_ROOT, "portal_launcher.py"), "w", encoding='utf-8') as f:
        f.write(launcher_code)
    
    print(f"\nPortal Launcher created at: {os.path.join(PORTAL_ROOT, 'portal_launcher.py')}")
    print("Run it to explore and execute your AI projects.")

if __name__ == "__main__":
    setup_portal()
