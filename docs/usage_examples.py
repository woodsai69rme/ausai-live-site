"""
Usage Examples for YouTube Enhancement Tools
============================================

This document provides practical examples of how to use the YouTube Enhancement Tools package.
"""

# Example 1: Basic usage of the command-line interface
"""
To download and process a single YouTube video:

```bash
youtube-enhancement-tools --url "https://www.youtube.com/watch?v=example"
```

To process multiple videos from a file:

```bash
youtube-enhancement-tools --batch-file urls.txt
```

To run the interactive setup:

```bash
youtube-enhancement-tools --setup
```
"""

# Example 2: Using the API programmatically
"""
from youtube_enhancement_tools.downloaders.downloader import download_youtube_video
from youtube_enhancement_tools.editors.editor import auto_edit_video
from youtube_enhancement_tools.config.config_manager import load_config

# Load configuration
config = load_config()

# Download a video
download_path = "./downloads/my_video.mp4"
download_youtube_video(
    url="https://www.youtube.com/watch?v=example", 
    output_path=download_path,
    quality="720p"
)

# Auto-edit the video
edited_path = "./output/edited_video.mp4"
auto_edit_video(input_path=download_path, output_path=edited_path, config=config)
"""

# Example 3: Validating YouTube URLs
"""
from youtube_enhancement_tools.utils.validator import validate_youtube_video

url = "https://www.youtube.com/watch?v=example"
if validate_youtube_url(url):
    print("URL is valid")
else:
    print("URL is invalid")
"""

# Example 4: Configuring the tool programmatically
"""
from youtube_enhancement_tools.config.config_manager import load_config, save_config

# Load existing config
config = load_config()

# Modify settings
config['settings']['default_quality'] = '1080p'
config['settings']['download_dir'] = './my_downloads/'

# Save the updated config
save_config(config)
"""

# Example 5: Handling errors gracefully
"""
from youtube_enhancement_tools.utils.exceptions import DownloadError
from youtube_enhancement_tools.downloaders.downloader import download_youtube_video

try:
    download_youtube_video(url="https://www.youtube.com/watch?v=example", output_path="./output.mp4")
except DownloadError as e:
    print(f"Download failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
"""

# Example 6: Using the rate limiter
"""
from youtube_enhancement_tools.utils.rate_limiter import RateLimiter

# Create a rate limiter that allows 10 calls per minute
rate_limiter = RateLimiter(max_calls=10, time_window=60)

# Before making an API call, check if it's allowed
if rate_limiter.is_allowed():
    # Make your API call here
    pass
else:
    # Wait before trying again
    rate_limiter.wait_if_needed()
"""