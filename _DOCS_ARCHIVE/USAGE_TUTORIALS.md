# YouTube Enhancement Tools - Usage Tutorials and Examples

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage Examples](#basic-usage-examples)
3. [Advanced Usage Examples](#advanced-usage-examples)
4. [Multi-Platform Usage](#multi-platform-usage)
5. [AI-Powered Features](#ai-powered-features)
6. [Automation Workflows](#automation-workflows)
7. [Performance Optimization Tips](#performance-optimization-tips)

## Getting Started

### Prerequisites
Before using the YouTube Enhancement Tools, ensure you have:
1. Python 3.8 or higher installed
2. FFmpeg installed on your system
3. Required Python packages installed via `pip install -r requirements.txt`
4. A valid `.env` file with your API keys (for AI features)

### Quick Start
To quickly process a YouTube video:

```bash
python youtube_enhancement_tools.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Basic Usage Examples

### 1. Process a Single Video
Process a single YouTube video with default settings:

```python
from youtube_enhancement_tools import process_youtube_video, load_config

# Load configuration
config = load_config()

# Process a video
success = process_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", config)
if success:
    print("Video processed successfully!")
else:
    print("Video processing failed!")
```

### 2. Batch Processing Multiple Videos
Process multiple videos from a list:

```python
from youtube_enhancement_tools import batch_process_urls, load_config

# Load configuration
config = load_config()

# List of URLs to process
urls = [
    "https://www.youtube.com/watch?v=video1",
    "https://www.youtube.com/watch?v=video2",
    "https://www.youtube.com/watch?v=video3"
]

# Process all videos
batch_process_urls(urls, config)
```

### 3. Batch Processing from File
Process videos listed in a text file (one URL per line):

```bash
python youtube_enhancement_tools.py --batch-file urls.txt
```

### 4. Check Dependencies
Verify that all required tools are installed:

```bash
python youtube_enhancement_tools.py --check-deps
```

### 5. Interactive Setup
Run the interactive setup to configure the tool:

```bash
python youtube_enhancement_tools.py --setup
```

## Advanced Usage Examples

### 1. Enhanced Video Processing with Watermark
Add a watermark to a processed video:

```python
from youtube_enhancement_tools import process_youtube_video, load_config
from advanced_video_processing import add_watermark_to_video
import os

# Load configuration
config = load_config()

# Process the video first
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
success = process_youtube_video(url, config)

if success:
    # Extract video ID to locate the processed file
    from youtube_enhancement_tools import extract_video_id_from_url
    video_id = extract_video_id_from_url(url)
    
    # Define paths
    output_dir = config['settings']['output_dir']
    original_path = os.path.join(output_dir, f"{video_id}_edited.mp4")
    watermarked_path = os.path.join(output_dir, f"{video_id}_watermarked.mp4")
    watermark_path = "./watermarks/my_logo.png"
    
    # Add watermark
    if add_watermark_to_video(original_path, watermarked_path, watermark_path):
        print("Watermark added successfully!")
    else:
        print("Failed to add watermark!")
```

### 2. Generate Custom Thumbnails
Create thumbnails from processed videos:

```python
from advanced_video_processing import generate_thumbnail_from_video
import os

# Define paths
video_path = "./output/video_edited.mp4"
thumbnail_path = "./output/video_thumbnail.jpg"

# Generate thumbnail
if generate_thumbnail_from_video(video_path, thumbnail_path):
    print("Thumbnail generated successfully!")
else:
    print("Failed to generate thumbnail!")
```

### 3. Create Custom Intro/Outro
Add custom intro and outro to videos:

```python
from advanced_video_processing import create_custom_intro, create_custom_outro, add_intro_outro_to_video
import os

# Create custom intro
intro_path = "./intros/tutorial_intro.mp4"
create_custom_intro(
    title="Python Tutorial Series",
    creator_name="Coding Expert",
    duration=5,
    output_path=intro_path
)

# Create custom outro
outro_path = "./outros/tutorial_outro.mp4"
create_custom_outro(
    message="Thanks for watching! Subscribe for more tutorials!",
    duration=5,
    output_path=outro_path
)

# Add intro and outro to a video
input_path = "./output/original_video.mp4"
output_path = "./output/video_with_intro_outro.mp4"
add_intro_outro_to_video(input_path, output_path, intro_path, outro_path)
```

### 4. Enhanced CLI Usage
Use the enhanced CLI with additional features:

```bash
# Process a video with enhancements
python enhanced_cli.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --enhance --thumbnail

# Add a watermark during processing
python enhanced_cli.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --watermark "./logo.png"

# Analyze content with AI
python enhanced_cli.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --analyze
```

## Multi-Platform Usage

### 1. Process Vimeo Videos
Process videos from Vimeo:

```python
from multi_platform_support import process_cross_platform_video, MultiPlatformProcessor
from youtube_enhancement_tools import load_config

# Load configuration
config = load_config()

# Process a Vimeo video
vimeo_url = "https://vimeo.com/123456789"
success = process_cross_platform_video(vimeo_url, config)

if success:
    print("Vimeo video processed successfully!")
else:
    print("Vimeo video processing failed!")
```

### 2. Process TikTok Videos
Process videos from TikTok:

```python
from multi_platform_support import process_cross_platform_video
from youtube_enhancement_tools import load_config

# Load configuration
config = load_config()

# Process a TikTok video
tiktok_url = "https://www.tiktok.com/@username/video/1234567890123456789"
success = process_cross_platform_video(tiktok_url, config)

if success:
    print("TikTok video processed successfully!")
else:
    print("TikTok video processing failed!")
```

### 3. Process Instagram Videos
Process videos from Instagram:

```python
from multi_platform_support import process_cross_platform_video
from youtube_enhancement_tools import load_config

# Load configuration
config = load_config()

# Process an Instagram video
instagram_url = "https://www.instagram.com/p/Ck123abcDEF/"
success = process_cross_platform_video(instagram_url, config)

if success:
    print("Instagram video processed successfully!")
else:
    print("Instagram video processing failed!")
```

## AI-Powered Features

### 1. Content Analysis
Analyze video content with AI:

```python
from ai_content_analysis import analyze_video_content

# Analyze a video's content
title = "Learn Python in 1 Hour - Beginner Tutorial"
description = "In this tutorial, you'll learn Python programming basics in just 1 hour. Perfect for beginners!"

analysis = analyze_video_content(title, description, "")

print("Sentiment Analysis:", analysis['sentiment_analysis'])
print("Content Suggestions:", analysis['content_suggestions'][:3])  # Show first 3
print("Recommended Tags:", analysis['recommended_tags'][:5])  # Show first 5
print("Engagement Prediction:", analysis['engagement_prediction'])
```

### 2. Generate AI Tags
Generate relevant tags for a video:

```python
from ai_content_analysis import AIContentAnalyzer

# Initialize analyzer
analyzer = AIContentAnalyzer()

# Generate tags
title = "Python Tutorial for Beginners"
description = "Learn Python programming from scratch with this comprehensive tutorial."

tags = analyzer.generate_tags(title, description)
print("Generated tags:", tags)
```

### 3. Predict Engagement
Predict how well a video might perform:

```python
from ai_content_analysis import AIContentAnalyzer

# Initialize analyzer
analyzer = AIContentAnalyzer()

# Predict engagement
title = "Python Tutorial for Beginners"
description = "Learn Python programming from scratch with this comprehensive tutorial."
tags = ["python", "programming", "tutorial", "beginner"]

engagement = analyzer.predict_engagement(
    title=title,
    description=description,
    tags=tags,
    upload_hour=15,  # 3 PM
    day_of_week=2    # Wednesday
)

print("Engagement prediction:", engagement)
```

### 4. AI-Enhanced Processing
Combine AI analysis with video processing:

```python
from youtube_enhancement_tools import process_youtube_video, load_config
from ai_content_analysis import analyze_video_content
from advanced_video_processing import add_watermark_to_video
import os

# Load configuration
config = load_config()

# Process the video first
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
success = process_youtube_video(url, config)

if success:
    # Extract video info for AI analysis
    from youtube_enhancement_tools import extract_video_info
    video_info = extract_video_info(url)
    
    # Analyze content
    analysis = analyze_video_content(
        video_info.get('title', ''),
        video_info.get('description', ''),
        ""  # No transcript available
    )
    
    print("Content analysis completed!")
    print(f"Suggested tags: {analysis['recommended_tags'][:5]}")
    
    # Optionally add a watermark based on analysis
    # (This is just an example - you'd implement your own logic)
    if "tutorial" in [tag.lower() for tag in analysis['recommended_tags']]:
        print("Video identified as tutorial, applying tutorial branding...")
```

## Automation Workflows

### 1. Schedule Video Processing
Schedule video processing for a future time:

```python
from automation_scheduler import ContentAutomationPipeline
from datetime import datetime, timedelta

# Create pipeline
pipeline = ContentAutomationPipeline()

# Schedule a video to be processed tomorrow at 10 AM
future_time = datetime.now() + timedelta(days=1)
future_time = future_time.replace(hour=10, minute=0, second=0, microsecond=0)

workflow_id = pipeline.create_upload_workflow(
    video_path="/path/to/video.mp4",
    title="Scheduled Video",
    description="This video was scheduled for processing",
    tags=["scheduled", "automated"],
    publish_datetime=future_time
)

print(f"Workflow created with ID: {workflow_id}")
```

### 2. Recurring Automation Tasks
Set up recurring tasks:

```python
from automation_scheduler import ContentAutomationPipeline
import time

def daily_cleanup():
    """Function to clean up old temporary files"""
    import os
    import shutil
    from pathlib import Path
    
    temp_dir = Path("./temp/")
    for file_path in temp_dir.glob("*"):
        if file_path.is_file():
            # Delete files older than 7 days
            if time.time() - file_path.stat().st_mtime > 7 * 24 * 60 * 60:
                file_path.unlink()
                print(f"Deleted old temp file: {file_path}")

# Create pipeline
pipeline = ContentAutomationPipeline()

# Schedule daily cleanup every 1440 minutes (24 hours)
cleanup_workflow_id = pipeline.create_recurring_workflow(
    daily_cleanup,
    interval_minutes=1440,
    workflow_name="daily_cleanup"
)

print(f"Daily cleanup scheduled with ID: {cleanup_workflow_id}")
```

### 3. Social Media Promotion Automation
Automate social media promotion after video upload:

```python
from automation_scheduler import ContentAutomationPipeline
from datetime import datetime, timedelta

# Create pipeline
pipeline = ContentAutomationPipeline()

# Schedule a video upload with social media promotion
future_time = datetime.now() + timedelta(hours=1)

workflow_id = pipeline.create_upload_workflow(
    video_path="/path/to/video.mp4",
    title="New Video Release",
    description="Check out our latest video!",
    tags=["new", "release", "video"],
    publish_datetime=future_time,
    social_media_posts=[
        {
            'platform': 'twitter',
            'content': 'Just published a new video! Check it out: [VIDEO_URL]',
            'delay_after_upload': 15,  # Post 15 minutes after upload
            'include_video': False
        },
        {
            'platform': 'mastodon',
            'content': 'Fresh content alert! 📺 [VIDEO_URL]',
            'delay_after_upload': 30,  # Post 30 minutes after upload
            'include_video': False
        }
    ]
)

print(f"Upload workflow with social promotion created: {workflow_id}")
```

### 4. Start Automation System
Start the automation system to run scheduled tasks:

```python
from automation_scheduler import ContentAutomationPipeline

# Create and start pipeline
pipeline = ContentAutomationPipeline()
pipeline.start_automation()

try:
    # Keep the script running to allow scheduled tasks to execute
    while True:
        time.sleep(60)  # Check every minute
except KeyboardInterrupt:
    print("\nStopping automation...")
    pipeline.stop_automation()
```

## Performance Optimization Tips

### 1. Use Caching for Repeated Operations
Enable caching for functions that are called repeatedly:

```python
from performance_optimizer import cached_function

@cached_function(maxsize=64)
def process_video_metadata(url):
    """Process video metadata with caching"""
    # Expensive operation that benefits from caching
    from youtube_enhancement_tools import extract_video_info
    return extract_video_info(url)

# This will be cached after the first call with the same URL
metadata1 = process_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
metadata2 = process_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Cached!
```

### 2. Monitor Resource Usage
Monitor system resources during processing:

```python
from enhanced_logging_monitoring import performance_monitor

# Start monitoring
performance_monitor.start_monitoring()

# Do your processing work here
# ...

# Stop monitoring when done
performance_monitor.stop_monitoring()

# Get performance history
history = performance_monitor.get_performance_history(minutes=10)
print(f"Collected {len(history)} performance data points")
```

### 3. Track Operation Performance
Track how long operations take:

```python
from enhanced_logging_monitoring import operation_tracker

# Start tracking an operation
op_id = "video_processing_123"
operation_tracker.start_operation(op_id, "Video Processing", {"video_id": "abc123"})

# Do the actual work
# ... video processing code ...

# End tracking
duration = operation_tracker.end_operation(op_id, success=True, result="Success")
print(f"Operation completed in {duration:.2f} seconds")

# Get overall stats
stats = operation_tracker.get_operation_stats()
print(f"Success rate: {stats['success_rate']*100:.2f}%")
```

### 4. Batch Processing for Efficiency
Process multiple videos in batches to improve efficiency:

```python
from youtube_enhancement_tools import batch_process_urls, load_config

# Load configuration
config = load_config()

# Process videos in batches
video_urls = [
    "https://www.youtube.com/watch?v=video1",
    "https://www.youtube.com/watch?v=video2",
    # ... more URLs
]

# Process in smaller batches to manage resources
batch_size = 5
for i in range(0, len(video_urls), batch_size):
    batch = video_urls[i:i+batch_size]
    print(f"Processing batch {i//batch_size + 1}")
    batch_process_urls(batch, config)
    
    # Optional: Add delay between batches to prevent overloading
    import time
    if i + batch_size < len(video_urls):
        print("Waiting before next batch...")
        time.sleep(30)  # Wait 30 seconds between batches
```

### 5. Asynchronous Processing
Use the async batch processor for handling multiple operations efficiently:

```python
from performance_optimizer import AsyncBatchProcessor

# Create a batch processor with 4 worker threads
batch_processor = AsyncBatchProcessor(max_workers=4)
batch_processor.start_workers()

# Submit multiple tasks
def process_single_video(url):
    from youtube_enhancement_tools import process_youtube_video, load_config
    config = load_config()
    return process_youtube_video(url, config)

urls = [
    "https://www.youtube.com/watch?v=video1",
    "https://www.youtube.com/watch?v=video2",
    "https://www.youtube.com/watch?v=video3",
    "https://www.youtube.com/watch?v=video4",
]

for i, url in enumerate(urls):
    batch_processor.submit_task(process_single_video, url, task_id=f"task_{i}")

# Wait for all tasks to complete
import time
while True:
    results = batch_processor.get_results()
    if not results and all(batch_processor.task_queue.empty() for _ in range(4)):
        break
    for task_id, result, error in results:
        if error:
            print(f"{task_id}: Error - {error}")
        else:
            print(f"{task_id}: Completed - {result}")
    time.sleep(1)

# Stop the processor
batch_processor.stop_workers()
```

## Troubleshooting Common Issues

### 1. Handling Rate Limits
When processing many videos, you might hit rate limits:

```python
from youtube_enhancement_tools import YT_DL_RATE_LIMITER, YT_INFO_RATE_LIMITER
import time

def safe_download(url, output_path):
    """Download with rate limiting"""
    # Wait if rate limit is exceeded
    YT_DL_RATE_LIMITER.wait_if_needed()
    
    from youtube_enhancement_tools import download_youtube_video
    return download_youtube_video(url, output_path)

def safe_extract_info(url):
    """Extract info with rate limiting"""
    # Wait if rate limit is exceeded
    YT_INFO_RATE_LIMITER.wait_if_needed()
    
    from youtube_enhancement_tools import extract_video_info
    return extract_video_info(url)
```

### 2. Error Handling and Recovery
Implement robust error handling:

```python
from youtube_enhancement_tools import handle_graceful_error

def robust_video_processing(url, config):
    """Process video with error handling"""
    try:
        from youtube_enhancement_tools import process_youtube_video
        return process_youtube_video(url, config)
    except Exception as e:
        # Handle error gracefully
        fallback_result = handle_graceful_error(
            error=e,
            context="video_processing",
            fallback_action=lambda: print("Using fallback processing method")
        )
        return fallback_result
```

### 3. Memory Management
For processing large numbers of videos, manage memory effectively:

```python
import gc
from performance_optimizer import optimized_processor

def process_videos_with_memory_management(urls, config):
    """Process videos while managing memory"""
    for i, url in enumerate(urls):
        print(f"Processing video {i+1}/{len(urls)}")
        
        # Process the video
        success = process_youtube_video(url, config)
        
        # Trigger garbage collection periodically
        if i % 10 == 0:  # Every 10 videos
            gc.collect()
            print("Garbage collection triggered")
        
        # Use optimized processor when possible
        if hasattr(optimized_processor, 'process_with_resource_management'):
            # Use resource-managed processing
            result = optimized_processor.process_with_resource_management(
                process_youtube_video, url, config
            )
```

---

**Note**: These tutorials and examples are for version 1.0 of YouTube Enhancement Tools. For the latest usage examples, please check the official repository.