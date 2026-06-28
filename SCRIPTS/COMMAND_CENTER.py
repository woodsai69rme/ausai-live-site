import os
import subprocess
import sys
import json
from datetime import datetime

# Master Orchestration Center
# Unified Interface for Scripts, Knowledge Bases, and AI Agents
# Powered by MASTER_ORCHESTRATION_INDEX.json

BASE_DIR = r"C:\Users\karma"
SCRIPTS_DIR = os.path.join(BASE_DIR, "SCRIPTS")
INDEX_FILE = os.path.join(SCRIPTS_DIR, "MASTER_ORCHESTRATION_INDEX.json")

def load_index():
    if not os.path.exists(INDEX_FILE):
        print("⚠️ Index not found. Run ORCHESTRATION_INDEXER.py first.")
        return None
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("="*70)
    print("🚀 MASTER ORCHESTRATION CENTER - ALL SYSTEMS READY")
    print("="*70)

def execute_script(script):
    print(f"\nExecuting: {script['name']}...")
    try:
        if script['type'] == "powershell":
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script['path']])
        elif script['type'] == "python":
            subprocess.run([sys.executable, script['path']])
        elif script['type'] == "batch":
            subprocess.run([script['path']], shell=True)
    except Exception as e:
        print(f"Error: {e}")
    input("\nPress Enter to return...")

def scripts_menu(index):
    while True:
        clear_screen()
        print_header()
        print("📂 SCRIPTS & AUTOMATIONS")
        print("-" * 30)
        
        # Group by category
        categories = {}
        for s in index['scripts']:
            cat = s['category']
            if cat not in categories: categories[cat] = []
            categories[cat].append(s)
        
        cat_list = list(categories.keys())
        for i, cat in enumerate(cat_list, 1):
            print(f"{i}. {cat} ({len(categories[cat])} scripts)")
        print("0. Back")
        
        choice = input("\nSelect Category: ")
        if choice == '0': break
        try:
            cat_idx = int(choice) - 1
            if 0 <= cat_idx < len(cat_list):
                script_selection_menu(categories[cat_list[cat_idx]])
        except: pass

def script_selection_menu(scripts):
    while True:
        clear_screen()
        print_header()
        print(f"📄 {scripts[0]['category']} SCRIPTS")
        print("-" * 30)
        for i, s in enumerate(scripts, 1):
            print(f"{i}. {s['name']}")
        print("0. Back")
        
        choice = input("\nSelect Script: ")
        if choice == '0': break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scripts):
                execute_script(scripts[idx])
        except: pass

def knowledge_menu(index):
    while True:
        clear_screen()
        print_header()
        print("📚 KNOWLEDGE COLLECTIONS (Awesome Lists)")
        print("-" * 30)
        for i, kb in enumerate(index['knowledge_bases'], 1):
            print(f"{i}. {kb['name']} ({len(kb['files'])} docs)")
        print("0. Back")
        
        choice = input("\nSelect Collection to open in Explorer: ")
        if choice == '0': break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(index['knowledge_bases']):
                os.startfile(index['knowledge_bases'][idx]['path'])
        except: pass

def agents_menu(index):
    while True:
        clear_screen()
        print_header()
        print("🤖 AI AGENTS & SKILLS")
        print("-" * 30)
        print(f"Total Agents Indexed: {len(index['agents'])}")
        print("\n1. Search for Agent")
        print("2. List Top 20 Recent")
        print("0. Back")
        
        choice = input("\nChoice: ")
        if choice == '0': break
        if choice == '1':
            query = input("Search term: ").lower()
            results = [a for a in index['agents'] if query in a['name'].lower()]
            print(f"\nFound {len(results)} matches:")
            for r in results[:20]:
                print(f"- {r['name']} ({r['path']})")
            if len(results) > 20: print(f"... and {len(results)-20} more.")
            input("\nPress Enter...")
        elif choice == '2':
            for a in index['agents'][:20]:
                print(f"- {a['name']}")
            input("\nPress Enter...")

def main():
    index = load_index()
    if not index: return

    while True:
        clear_screen()
        print_header()
        print(f"Last Indexed: {index['generated_at']}")
        print(f"System Capacity: {len(index['scripts'])} Scripts | {len(index['knowledge_bases'])} Collections | {len(index['agents'])} Agents")
        print("-" * 70)
        print("1. 🛠️  Execute Scripts & Automations")
        print("2. 📖  Browse Knowledge Base")
        print("3. 🧠  Access AI Agents & Skills")
        print("4. 🔄  Refresh Index")
        print("0. Exit")
        
        choice = input("\nSelect Action: ")
        if choice == '0':
            break
        elif choice == '1':
            scripts_menu(index)
        elif choice == '2':
            knowledge_menu(index)
        elif choice == '3':
            agents_menu(index)
        elif choice == '4':
            print("Refreshing index...")
            subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "ORCHESTRATION_INDEXER.py")])
            index = load_index()
            input("\nIndex refreshed. Press Enter...")

if __name__ == "__main__":
    main()
