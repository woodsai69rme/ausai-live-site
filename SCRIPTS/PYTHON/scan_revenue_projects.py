import os
import json
import glob

def scan_projects():
    root = "REVENUE_GENERATORS"
    projects = []
    
    if not os.path.exists(root):
        print(f"Directory {root} not found.")
        return

    for item in os.listdir(root):
        path = os.path.join(root, item)
        if os.path.isdir(path):
            project_info = {
                "name": item,
                "path": path,
                "type": "unknown",
                "has_env": False,
                "has_env_example": False,
                "dependencies_file": None,
                "security_issues": []
            }
            
            # Detect Type & Dependencies
            if os.path.exists(os.path.join(path, "package.json")):
                project_info["type"] = "node"
                project_info["dependencies_file"] = "package.json"
            elif os.path.exists(os.path.join(path, "requirements.txt")):
                project_info["type"] = "python"
                project_info["dependencies_file"] = "requirements.txt"
                
            # Detect Config
            if os.path.exists(os.path.join(path, ".env")):
                project_info["has_env"] = True
            if os.path.exists(os.path.join(path, ".env.example")):
                project_info["has_env_example"] = True
                
            projects.append(project_info)
            
    print(json.dumps(projects, indent=2))

if __name__ == "__main__":
    scan_projects()
