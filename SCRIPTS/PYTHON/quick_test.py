import sys
import os

# Temporarily suppress logging for this test
import logging
logging.disable(logging.CRITICAL)

sys.path.insert(0, os.getcwd())

try:
    # Import specific functions without triggering full module initialization
    from youtube_enhancement_tools import validate_youtube_url, DEFAULT_CONFIG
    
    print("Module imported successfully")
    print("Testing URL validation:", validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
    print("Default config max_retries:", DEFAULT_CONFIG['settings']['max_retries'])
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()