import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_sweep_log.txt'),
        logging.StreamHandler()
    ]
)

TARGET_DIR = os.path.join("EXPERIMENTAL", "_UNSORTED")
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

# Folders to explicitly move (long list based on observation)
FOLDERS_TO_MOVE = [
    "normalizations", "normalizers", "notebooks", "notifications", "objects", 
    "obstruction_free_data_structures", "oh-my-opencode-setup", "optimization", 
    "optimizations", "orchestrations", "orchids-projects", "packages", "pages", 
    "paradigms", "parallelization", "patterns", "payloads", "performance_benchmarking", 
    "permissions", "pipelines", "plugins", "popovers", "postprocessing", 
    "preprocessing", "presenters", "pricing_pages", "processes", 
    "processor_consistency", "processors", "progress_guarantees", "PROJECT_METRICS", 
    "projections", "prototypes", "qnew", "qwendec25", "qwensetup", "rag_memory", 
    "realities", "relaxed_ordering", "release_consistency", "reliability", 
    "repositories", "responses", "roles", "routes", "safety_properties", 
    "scalability", "scenes", "sections", "Secure", "security_review", 
    "self_researching_system", "sequential_ordering", "serializers", "sessions", 
    "shaders", "signatures", "skins", "snapshots", "software_transactional_memory", 
    "src", "ssl", "standardizations", "starvation_freedom", "stickers", "storage", 
    "store_load_fences", "strong_ordering", "styles", "subscriptions", 
    "synchronization", "synchronizers", "system_intelligence", "SYSTEM_TOOLS", 
    "tables", "tags", "test_demo", "test_files", "test_output", "textures", "themes", 
    "thread_local_storage", "threads", "tiles", "tls_keys", "tokens", "tooltips", 
    "topologies", "traits", "transactions", "transformers", "transitions", 
    "translations", "ultimate-crypto-ai-platform", "universes", "uploads", "users", 
    "utilities", "ux_assessment", "validators", "value_objects", "venv_playwright", 
    "verifiers", "vertices", "views", "visualizations", "VOICE_ORCHESTRATOR_SYSTEM", 
    "wait_free_data_structures", "warnings", "weak_ordering", "widgets", "wiki", 
    "workflows", "worlds", "youtube_research", "node_modules"
]

def run_sweep():
    for item in FOLDERS_TO_MOVE:
        if os.path.exists(item):
            try:
                shutil.move(item, os.path.join(TARGET_DIR, item))
                logging.info(f"Moved '{item}' to {TARGET_DIR}")
            except Exception as e:
                logging.error(f"Failed to move '{item}': {e}")

    # Move any folders starting with "production_deployment_"
    for item in os.listdir('.'):
        if item.startswith("production_deployment_") and os.path.isdir(item):
             try:
                shutil.move(item, os.path.join(TARGET_DIR, item))
                logging.info(f"Moved '{item}' to {TARGET_DIR}")
             except Exception as e:
                logging.error(f"Failed to move '{item}': {e}")

if __name__ == "__main__":
    run_sweep()
