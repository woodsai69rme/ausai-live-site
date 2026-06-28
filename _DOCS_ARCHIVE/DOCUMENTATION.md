# YouTube Enhancement Tools - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Features](#features)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Command Line Usage](#command-line-usage)
8. [Advanced Features](#advanced-features)
9. [Development](#development)
10. [Contributing](#contributing)
11. [License](#license)

## Overview

YouTube Enhancement Tools is a comprehensive toolkit for YouTube content creators with automation, AI tools, and productivity enhancements. The package provides functionality for downloading, editing, and optimizing YouTube videos, along with tools for SEO optimization and social media cross-posting.

### Key Features
- YouTube video downloading with yt-dlp
- Automatic video editing to remove silences
- AI-powered thumbnail generation
- SEO optimization suggestions
- Social media cross-posting tools
- Batch processing capabilities
- Comprehensive configuration management
- Rate limiting and resource monitoring

## Installation

### Prerequisites
- Python 3.8 or higher
- yt-dlp
- auto-editor

### Installing from PyPI
```bash
pip install youtube-enhancement-tools
```

### Installing from Source
```bash
git clone https://github.com/youtube-enhancement-tools/youtube-enhancement-tools.git
cd youtube-enhancement-tools
pip install -e .
```

### Installing Dependencies
```bash
pip install -r requirements-enhanced.txt
```

## Quick Start

### Command Line Usage
```bash
# Process a single video
youtube-enhancement-tools --url "https://www.youtube.com/watch?v=example"

# Process multiple videos from a file
youtube-enhancement-tools --batch-file urls.txt

# Run interactive setup
youtube-enhancement-tools --setup
```

### Programmatic Usage
```python
from youtube_enhancement_tools.processors.video_processor import process_youtube_video
from youtube_enhancement_tools.config.config_manager import load_config

config = load_config()
success = process_youtube_video(
    url="https://www.youtube.com/watch?v=example",
    config=config
)
```

## Features

### Downloading
The package uses yt-dlp to download YouTube videos with support for various quality levels and formats.

### Editing
Automatic editing removes silences and adjusts video speed using auto-editor.

### AI Thumbnail Generation
Generate custom thumbnails from video frames with various styling options.

### SEO Optimization
Analyze titles, descriptions, and tags for SEO optimization with actionable suggestions.

### Social Media Cross-Posting
Cross-post content to multiple social media platforms with appropriate formatting.

### Batch Processing
Process multiple videos in batches with configurable batch sizes and delays.

## API Reference

### Main Module
#### `main()`
Primary entry point for command-line interface.

### Downloaders Module
#### `download_youtube_video(url, output_path, quality="720p", max_retries=None)`
Downloads a YouTube video to the specified output path.

Parameters:
- `url` (str): YouTube URL to download
- `output_path` (str): Path to save the downloaded video
- `quality` (str): Video quality (480p, 720p, 1080p)
- `max_retries` (int): Number of retry attempts

Returns:
- `bool`: True if download successful, False otherwise

#### `validate_youtube_url(url)`
Validates a YouTube URL for correctness and safety.

Parameters:
- `url` (str): URL to validate

Returns:
- `bool`: True if valid, False otherwise

### Editors Module
#### `auto_edit_video(input_path, output_path, config=None)`
Automatically edits a video to remove silences.

Parameters:
- `input_path` (str): Path to input video
- `output_path` (str): Path to save edited video
- `config` (dict): Configuration for editing settings

Returns:
- `bool`: True if editing successful, False otherwise

### AI Tools Module
#### `generate_thumbnail_from_video(video_path, output_path, timestamp=None, quality=95)`
Generates a thumbnail from a video at a specific timestamp.

Parameters:
- `video_path` (str): Path to input video
- `output_path` (str): Path to save thumbnail
- `timestamp` (float): Timestamp in seconds (middle of video if None)
- `quality` (int): JPEG quality (1-100)

Returns:
- `bool`: True if successful, False otherwise

#### `generate_ai_enhanced_thumbnail(video_path, output_path, style="default", quality=95)`
Generates an AI-enhanced thumbnail with styling options.

Parameters:
- `video_path` (str): Path to input video
- `output_path` (str): Path to save thumbnail
- `style` (str): Style option ("default", "cinematic", "bright", "contrast")
- `quality` (int): JPEG quality (1-100)

Returns:
- `bool`: True if successful, False otherwise

#### `generate_seo_suggestions(title, description, tags)`
Generates SEO optimization suggestions for YouTube content.

Parameters:
- `title` (str): Video title
- `description` (str): Video description
- `tags` (List[str]): List of video tags

Returns:
- `dict`: SEO analysis and suggestions

### Social Media Module
#### `create_social_media_post(title, description, tags, video_url, platforms, thumbnail_path=None)`
Creates and posts social media updates for a YouTube video.

Parameters:
- `title` (str): Video title
- `description` (str): Video description
- `tags` (List[str]): Video tags
- `video_url` (str): URL to YouTube video
- `platforms` (List[str]): Platforms to post to
- `thumbnail_path` (str): Path to thumbnail image

Returns:
- `Dict[str, bool]`: Results for each platform

### Processors Module
#### `process_youtube_video(url, config)`
Complete workflow to process a YouTube video.

Parameters:
- `url` (str): YouTube URL to process
- `config` (dict): Configuration settings

Returns:
- `bool`: True if processing successful, False otherwise

#### `batch_process_urls(urls, config)`
Process multiple YouTube URLs in batch.

Parameters:
- `urls` (List[str]): List of YouTube URLs
- `config` (dict): Configuration settings

Returns:
- `List[dict]`: Results for each URL

### Configuration Module
#### `load_config()`
Loads configuration from file or creates default if not exists.

Returns:
- `dict`: Configuration settings

#### `save_config(config)`
Saves configuration to file.

Parameters:
- `config` (dict): Configuration to save

#### `get_api_key(key_name)`
Gets API key from environment or config file.

Parameters:
- `key_name` (str): Name of the API key

Returns:
- `str`: API key value or None

## Configuration

### Default Configuration
The default configuration includes:

```json
{
  "settings": {
    "download_dir": "./downloads/",
    "output_dir": "./output/",
    "temp_dir": "./temp/",
    "default_quality": "720p",
    "batch_size": 5,
    "max_retries": 3,
    "timeout_seconds": 300,
    "delay_between_videos": 1,
    "delay_between_batches": 5,
    "auto_edit_settings": {
      "silent_threshold": 0.04,
      "video_speed": 1.25
    }
  }
}
```

### Environment Variables
API keys can be set as environment variables:
- `YOUTUBE_TOOLS_OPENAI_KEY`
- `YOUTUBE_TOOLS_YOUTUBE_KEY`
- `YOUTUBE_TOOLS_ELEVENLABS_KEY`
- `YOUTUBE_TOOLS_TWITTER_KEY`
- `YOUTUBE_TOOLS_FACEBOOK_KEY`
- `YOUTUBE_TOOLS_LINKEDIN_KEY`
- `YOUTUBE_TOOLS_INSTAGRAM_KEY`
- `YOUTUBE_TOOLS_TIKTOK_KEY`
- `YOUTUBE_TOOLS_REDDIT_KEY`

### Interactive Setup
Run `youtube-enhancement-tools --setup` to configure settings interactively.

## Command Line Usage

### Options
- `--setup`: Run interactive setup
- `--url`: Process a single YouTube URL
- `--batch-file`: Process multiple URLs from a file
- `--check-deps`: Check dependencies only
- `--verbose`, `-v`: Enable verbose logging

### Examples
```bash
# Process a single video
youtube-enhancement-tools --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Process multiple videos
youtube-enhancement-tools --batch-file my_videos.txt

# Check dependencies
youtube-enhancement-tools --check-deps

# Verbose output
youtube-enhancement-tools --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -v
```

## Advanced Features

### AI-Powered Thumbnail Generation
The package includes sophisticated thumbnail generation with multiple styling options:

- **Default**: Basic frame extraction
- **Cinematic**: Darker edges, brighter center
- **Bright**: Increased brightness
- **Contrast**: Enhanced contrast

### SEO Optimization
The SEO optimizer provides detailed analysis of titles, descriptions, and tags with specific suggestions for improvement.

### Social Media Cross-Posting
Supports posting to Twitter, Facebook, LinkedIn, Instagram, TikTok, and Reddit with platform-specific formatting.

### Batch Processing Improvements
Enhanced batch processing includes:
- Configurable batch sizes
- Delays between videos and batches
- Detailed result tracking
- Automatic result saving to JSON files

## Development

### Setting up for Development
```bash
git clone https://github.com/youtube-enhancement-tools/youtube-enhancement-tools.git
cd youtube-enhancement-tools
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

### Building Documentation
```bash
cd docs
make html
```

### Code Quality Checks
```bash
flake8 youtube_enhancement_tools/
black --check youtube_enhancement_tools/
mypy youtube_enhancement_tools/
```

## Contributing

### Reporting Bugs
Please use the GitHub issue tracker to report bugs. Include:
- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment information

### Feature Requests
Submit feature requests through the GitHub issue tracker with:
- A clear description of the desired feature
- Use cases for the feature
- Any relevant examples

### Pull Requests
1. Fork the repository
2. Create a feature branch
3. Make changes following the code style
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.