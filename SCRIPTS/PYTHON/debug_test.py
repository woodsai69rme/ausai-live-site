"""Debug test to see what's happening with the function import"""
import sys
sys.path.insert(0, '.')

# Import the same way as the test
from youtube_enhancement_tools import extract_video_id_from_url

def test_function():
    result = extract_video_id_from_url('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    print(f"Result: {result}, Type: {type(result)}, Is None: {result is None}")
    return result

if __name__ == "__main__":
    test_function()