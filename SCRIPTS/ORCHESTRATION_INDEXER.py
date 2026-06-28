import os
import json
import re
from datetime import datetime

# Master Orchestration Indexer v2
# Catalogs scripts, knowledge bases, and AI agents for the Command Center.

BASE_DIR = r"C:\Users\karma"
SCRIPTS_DIR = os.path.join(BASE_DIR, "SCRIPTS")
KNOWLEDGE_ROOTS = [
    r"C:\Users\karma\X\githubrepo",
    r"C:\Users\karma\github_repos",
    r"C:\Users\karma\MASTER_ECOSYSTEM"
]
SKILLS_ROOTS = [
    os.path.join(BASE_DIR, "skills"),
    os.path.join(BASE_DIR, ".agents", "skills"),
    os.path.join(BASE_DIR, ".claude", "skills"),
    os.path.join(BASE_DIR, ".cline", "skills"),
    os.path.join(BASE_DIR, ".gemini", "skills"),
    os.path.join(BASE_DIR, ".qwen", "skills"),
    os.path.join(BASE_DIR, ".agent", "skills")
]

OUTPUT_FILE = os.path.join(SCRIPTS_DIR, "MASTER_ORCHESTRATION_INDEX.json")

def find_scripts():
    print("🔍 Indexing scripts...")
    scripts = []
    extensions = ('.py', '.ps1', '.bat', '.sh')
    # Scan SCRIPTS dir
    for root, dirs, files in os.walk(SCRIPTS_DIR):
        if 'BACKUPS' in dirs: dirs.remove('BACKUPS')
        for file in files:
            if file.endswith(extensions):
                path = os.path.join(root, file)
                s_type = "python" if file.endswith('.py') else \
                         "powershell" if file.endswith('.ps1') else \
                         "batch" if file.endswith('.bat') else "shell"
                scripts.append({
                    "name": file,
                    "path": path,
                    "type": s_type,
                    "category": os.path.basename(root)
                })
    return scripts

def find_knowledge():
    print("🔍 Indexing knowledge collections...")
    collections = []
    for root_path in KNOWLEDGE_ROOTS:
        if os.path.exists(root_path):
            try:
                for item in os.listdir(root_path):
                    path = os.path.join(root_path, item)
                    if os.path.isdir(path) and (item.startswith("awesome-") or "collection" in item.lower()):
                        collections.append({
                            "name": item,
                            "path": path,
                            "files": [f for f in os.listdir(path) if f.endswith('.md')]
                        })
            except Exception as e:
                print(f"Error scanning {root_path}: {e}")
    return collections

def find_agents():
    print("🔍 Indexing AI agents (skills)...")
    agents = []
    for root_path in SKILLS_ROOTS:
        if os.path.exists(root_path):
            for root, dirs, files in os.walk(root_path):
                if 'node_modules' in dirs: dirs.remove('node_modules')
                if '.git' in dirs: dirs.remove('.git')
                
                if 'SKILL.md' in files:
                    agents.append({
                        "name": os.path.basename(root),
                        "path": root,
                        "file": "SKILL.md"
                    })
    return agents

def main():
    index = {
        "generated_at": datetime.now().isoformat(),
        "scripts": find_scripts(),
        "knowledge_bases": find_knowledge(),
        "agents": find_agents()
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)
    
    print(f"\n✅ Master Index generated: {OUTPUT_FILE}")
    print(f"📈 Scripts: {len(index['scripts'])}")
    print(f"📚 Knowledge: {len(index['knowledge_bases'])}")
    print(f"🤖 Agents: {len(index['agents'])}")

if __name__ == "__main__":
    main()
