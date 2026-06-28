import sys
import traceback
import time

sys.path.insert(0, 'x:\\GITHUBREPO\\aiarmy')

print("Starting import test...")
time.sleep(0.5)
try:
    print("Attempting to import src.agents.ai_content_agent")
    import src.agents.ai_content_agent
    print("SUCCESS: import src.agents.ai_content_agent")
except BaseException as e:
    print(f"CRASH: {type(e).__name__}")
    traceback.print_exc()

print("Test complete.")
