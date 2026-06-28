import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fix_configs():
    root = "REVENUE_GENERATORS"
    
    # Projects that need a basic .env if they don't have one
    basic_env_content = """# Basic Configuration
PORT=3000
NODE_ENV=development
# Add your API keys below
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DATABASE_URL=sqlite:///./data.db
"""
    
    for item in os.listdir(root):
        path = os.path.join(root, item)
        if not os.path.isdir(path):
            continue
            
        env_path = os.path.join(path, ".env")
        example_path = os.path.join(path, ".env.example")
        
        # Case 1: Has example, missing .env -> Copy it
        if os.path.exists(example_path) and not os.path.exists(env_path):
            try:
                shutil.copy(example_path, env_path)
                logging.info(f"✅ Created .env from example for {item}")
            except Exception as e:
                logging.error(f"Failed to copy .env for {item}: {e}")
                
        # Case 2: No config at all -> Create skeleton
        elif not os.path.exists(env_path) and not os.path.exists(example_path):
            # Only if it looks like a code project (has package.json or requirements.txt)
            if os.path.exists(os.path.join(path, "package.json")) or os.path.exists(os.path.join(path, "requirements.txt")):
                try:
                    with open(env_path, "w") as f:
                        f.write(basic_env_content)
                    logging.info(f"⚠️ Created skeleton .env for {item}")
                except Exception as e:
                    logging.error(f"Failed to create .env for {item}: {e}")
                    
        else:
            logging.info(f"ℹ️ Config already exists for {item}")

if __name__ == "__main__":
    fix_configs()
