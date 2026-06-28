import os
import subprocess
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

def review_all_projects(parent_dir: str):
    parent_dir = os.path.abspath(parent_dir)
    print(Fore.CYAN + f"\n[!] INITIATING THE GREAT CODEBASE AUDIT")
    print(Fore.CYAN + f"[*] Target Parent Directory: {parent_dir}\n")

    if not os.path.isdir(parent_dir):
        print(Fore.RED + f"Error: The directory {parent_dir} does not exist.")
        return

    # Get all immediate subdirectories
    subdirs = [f.path for f in os.scandir(parent_dir) if f.is_dir()]
    total = len(subdirs)
    
    print(Fore.YELLOW + f"Found {total} project folders to audit.\n")

    success_count = 0
    skip_count = 0
    fail_count = 0

    reviewer_script = os.path.join("C:\\", "Users", "karma", "ai-reviewer.py")
    if not os.path.exists(reviewer_script):
        print(Fore.RED + f"Error: Cannot find ai-reviewer.py at {reviewer_script}")
        return

    for i, project_dir in enumerate(subdirs, 1):
        project_name = os.path.basename(project_dir)
        summary_path = os.path.join(project_dir, "AI_SUMMARY.md")
        
        print(Fore.BLUE + f"[{i}/{total}] Analyzing: {project_name}")

        # Check if it was already processed
        if os.path.exists(summary_path):
            print(Fore.YELLOW + f"   -> Skipped (AI_SUMMARY.md already exists)\n")
            skip_count += 1
            continue
            
        print(Fore.MAGENTA + f"   -> Generating deep audit report...")

        try:
            # We run ai-reviewer.py and capture the output
            # We don't want to show all the streaming output, just collect it
            # But the free API can time out, so we add a timeout (5 mins per repo)
            result = subprocess.run(
                ['python', reviewer_script, project_dir],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300
            )

            if result.returncode == 0:
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                
                # Cleanup the markdown blocks if present (basic clean)
                # But actually ai-reviewer's stdout also prints progress bars
                # Let's cleanly separate it. ai-reviewer.py writes to stdout.
                # Since ai-reviewer prints some console info ("[*] Analzying..."), 
                # we should only keep the markdown content.
                # The markdown usually starts with `# ` or `## `.
                
                contentLines = result.stdout.split('\n')
                markdown_lines = []
                capturing = False
                for line in contentLines:
                    # heuristic: OpenRouter content starts after "[✓] Analysis complete."
                    # Let's just find the first Markdown header
                    if line.startswith("# ") or line.startswith("## ") or line.startswith("```"):
                        capturing = True
                    if capturing:
                        markdown_lines.append(line)
                        
                final_content = "\n".join(markdown_lines) if markdown_lines else result.stdout

                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(final_content.strip())
                
                print(Fore.GREEN + f"   -> [SUCCESS] AI_SUMMARY.md saved.\n")
                success_count += 1
            else:
                print(Fore.RED + f"   -> [FAILED] Error during analysis.")
                print(Fore.RED + f"      Details: {result.stderr.strip()[:200]}...\n")
                fail_count += 1
                
        except subprocess.TimeoutExpired:
            print(Fore.RED + f"   -> [FAILED] Timed out after 5 minutes. (Rate limit or huge repo?)\n")
            fail_count += 1
            
        except Exception as e:
            print(Fore.RED + f"   -> [FAILED] Unexpected error: {e}\n")
            fail_count += 1

    print(Fore.CYAN + "==================================================")
    print(Fore.CYAN + "               AUDIT COMPLETE")
    print(Fore.CYAN + "==================================================")
    print(Fore.GREEN + f" Successful Audits: {success_count}")
    print(Fore.YELLOW + f" Skipped (Existing): {skip_count}")
    print(Fore.RED + f" Failed/Timed Out:   {fail_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mass Pipeline Codebase Auditor")
    parser.add_argument("parent", help="Parent directory containing multiple project folders")
    args = parser.parse_args()
    
    review_all_projects(args.parent)
