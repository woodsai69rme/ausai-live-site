import os
import json
import subprocess
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# CONFIGURATION
ARCHIVE_DIR = r"X:/AETHER_CORE_SYSTEM/backups/GITHUB_REMOTE_ARCHIVE"
GITHUB_TOKEN = "REDACTED_ghp_TOKEN"
OS_ENV = os.environ.copy()
OS_ENV["GH_TOKEN"] = GITHUB_TOKEN

def get_repo_list():
    """Fetches all repos from GitHub CLI."""
    logger.info("Fetching remote repository list from GitHub...")
    try:
        cmd = ["gh", "repo", "list", "--limit", "1000", "--json", "name,url,isPrivate"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=OS_ENV, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"Failed to fetch repo list: {e}")
        return []

def download_repos(repos):
    """Clones or updates repositories locally."""
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    total = len(repos)
    logger.info(f"Starting archival of {total} repositories to {ARCHIVE_DIR}...")
    
    for i, repo in enumerate(repos, 1):
        name = repo["name"]
        url = repo["url"]
        is_private = repo["isPrivate"]
        repo_path = os.path.join(ARCHIVE_DIR, name)
        
        type_str = "[PRIVATE]" if is_private else "[PUBLIC]"
        logger.info(f"[{i}/{total}] {type_str} {name}...")

        try:
            if os.path.exists(repo_path):
                # Update existing
                subprocess.run(["git", "-C", repo_path, "pull"], capture_output=True, check=False)
                logger.info(f"  - Updated {name}")
            else:
                # Clone new
                subprocess.run(["git", "clone", url, repo_path], capture_output=True, check=True)
                logger.info(f"  - Cloned {name}")
            
            # Respectful delay to avoid hitting API limits too hard
            time.sleep(0.5)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"  - Error processing {name}: {e.stderr}")
        except Exception as e:
            logger.error(f"  - Unexpected error for {name}: {e}")

if __name__ == "__main__":
    start_time = datetime.now()
    repos = get_repo_list()
    if repos:
        download_repos(repos)
    
    duration = datetime.now() - start_time
    logger.info(f"Archival complete. Duration: {duration.total_seconds():.2f}s")
