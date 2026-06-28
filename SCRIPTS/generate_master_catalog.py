import os
import json
import re

HUBS = {
    "ACTIVE_PROJECTS": r"C:\Users\karma\ACTIVE_PROJECTS",
    "REVENUE_GENERATORS": r"C:\Users\karma\REVENUE_GENERATORS",
    "GITHUB_REPOS": r"X:\GITHUBREPO",
    "EXPERIMENTAL": r"C:\Users\karma\EXPERIMENTAL"
}

OUT_DIR = r"C:\Users\karma\MASTER_ECOSYSTEM_CATALOG_2026"
os.makedirs(OUT_DIR, exist_ok=True)

def extract_summary(path, skip_reads=False):
    summary = "No description available."
    if skip_reads:
        return "Imported Repository / Project"
        
    for file_to_try in ["package.json"]:
        pkg_path = os.path.join(path, file_to_try)
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    if "description" in data and data["description"].strip():
                        return f"(Node/JS) {data['description']}"
            except:
                pass

    return summary

def main():
    total_projects = 0
    with open(os.path.join(OUT_DIR, "00_README.md"), "w", encoding="utf-8") as main_f:
        main_f.write("# Master Ecosystem Catalog (2026)\n\n")

    for idx, (hub_name, hub_path) in enumerate(HUBS.items(), start=1):
        md_file = os.path.join(OUT_DIR, f"{idx:02d}_{hub_name}.md")
        num_projects = 0
        skip_reads = (hub_name == "GITHUB_REPOS")
        
        if not os.path.exists(hub_path):
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(f"# {hub_name}\n\n*Not found.*\n")
            continue

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# {hub_name}\n\n| Repository / Project | Type | Summary | Location |\n| --- | --- | --- | --- |\n")
            try:
                for item in os.listdir(hub_path):
                    item_path = os.path.join(hub_path, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        num_projects += 1
                        total_projects += 1
                        summary = extract_summary(item_path, skip_reads)
                        
                        p_type = "Python" if "python" in item.lower() or "ai" in item.lower() else "App"
                        if os.path.exists(os.path.join(item_path, "package.json")): p_type = "Node"
                        
                        safe_sum = summary.replace('|', '').replace('\n', ' ')
                        f.write(f"| **{item}** | {p_type} | {safe_sum} | `{item_path}` |\n")
            except Exception as e:
                f.write(f"\n*Error: {str(e)}*\n")
                
        with open(os.path.join(OUT_DIR, "00_README.md"), "a", encoding="utf-8") as main_f:
            main_f.write(f"- **{hub_name}**: {num_projects} projects\n")
            
    with open(os.path.join(OUT_DIR, "00_README.md"), "a", encoding="utf-8") as main_f:
        main_f.write(f"\n**Total Indexed:** {total_projects}\n")
    print("Catalog Complete.")

if __name__ == "__main__":
    main()
