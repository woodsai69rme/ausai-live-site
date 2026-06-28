# YouTube Enhancement Tools - API Reference Documentation

## Table of Contents
1. [Core Functions](#core-functions)
2. [Advanced Video Processing](#advanced-video-processing)
3. [AI Content Analysis](#ai-content-analysis)
4. [Multi-Platform Support](#multi-platform-support)
5. [Automation & Scheduling](#automation--scheduling)
6. [Performance Optimization](#performance-optimization)
7. [Enhanced Logging & Monitoring](#enhanced-logging--monitoring)

## Core Functions

### `validate_youtube_url(url)`
Validates a YouTube URL against supported patterns with comprehensive security checks.

**Parameters:**
- `url` (str): The YouTube URL to validate

**Returns:**
- `bool`: True if the URL is valid, False otherwise

**Example:**
```python
is_valid = validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(is_valid)  # True
```

### `extract_video_id_from_url(url)`
Extracts the video ID from a YouTube URL.

**Parameters:**
- `url` (str): The YouTube URL to extract ID from

**Returns:**
- `str` or `None`: The extracted video ID or None if not found

**Example:**
```python
video_id = extract_video_id_from_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(video_id)  # dQw4w9WgXcQ
```

### `extract_video_info(url, max_retries=None)`
Extracts video information using yt-dlp with rate limiting and retry mechanism.

**Parameters:**
- `url` (str): The YouTube URL to extract info from
- `max_retries` (int, optional): Maximum number of retry attempts

**Returns:**
- `dict`: Dictionary containing video information (title, description, uploader, duration, view_count)

**Example:**
```python
info = extract_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(info['title'])  # Video title
```

### `download_youtube_video(url, output_path, quality="720p", max_retries=None)`
Downloads a YouTube video using yt-dlp with improved error handling, rate limiting, and retry mechanism.

**Parameters:**
- `url` (str): The YouTube URL to download
- `output_path` (str): Path to save the downloaded video
- `quality` (str): Video quality ("480p", "720p", "1080p")
- `max_retries` (int, optional): Maximum number of retry attempts

**Returns:**
- `bool`: True if download was successful, False otherwise

**Example:**
```python
success = download_youtube_video(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "./downloads/video.mp4",
    quality="720p"
)
```

### `auto_edit_video(input_path, output_path, config=None)`
Automatically edits a video to remove silence using auto-editor.

**Parameters:**
- `input_path` (str): Path to the input video
- `output_path` (str): Path to save the edited video
- `config` (dict, optional): Configuration for auto-editing

**Returns:**
- `bool`: True if editing was successful, False otherwise

**Example:**
```python
success = auto_edit_video("./input/video.mp4", "./output/edited_video.mp4")
```

### `process_youtube_video(url, config)`
Complete workflow to process a YouTube video with proper resource management and compliance checks.

**Parameters:**
- `url` (str): The YouTube URL to process
- `config` (dict): Configuration settings

**Returns:**
- `bool`: True if processing was successful, False otherwise

**Example:**
```python
config = load_config()
success = process_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", config)
```

### `batch_process_urls(urls, config)`
Processes multiple YouTube URLs in batch.

**Parameters:**
- `urls` (list): List of YouTube URLs to process
- `config` (dict): Configuration settings

**Example:**
```python
urls = [
    "https://www.youtube.com/watch?v=video1",
    "https://www.youtube.com/watch?v=video2"
]
config = load_config()
batch_process_urls(urls, config)
```

### `load_config()`
Loads configuration from file or creates default if not exists.

**Returns:**
- `dict`: Configuration dictionary

**Example:**
```python
config = load_config()
print(config['settings']['download_dir'])
```

### `save_config(config)`
Saves configuration to file.

**Parameters:**
- `config` (dict): Configuration dictionary to save

**Example:**
```python
config = load_config()
config['settings']['default_quality'] = '1080p'
save_config(config)
```

### `acknowledge_tos()`
Prompts user to acknowledge terms of service with enhanced compliance checks.

**Returns:**
- `bool`: True if user acknowledges, False otherwise

**Example:**
```python
if acknowledge_tos():
    print("User agreed to terms of service")
else:
    print("User did not agree to terms of service")
```

## Advanced Video Processing

### `add_watermark_to_video(input_path, output_path, watermark_image_path, position="bottom-right", opacity=0.7)`
Adds a watermark to a video.

**Parameters:**
- `input_path` (str): Path to the input video
- `output_path` (str): Path to save the watermarked video
- `watermark_image_path` (str): Path to the watermark image
- `position` (str): Position of the watermark ("top-left", "top-right", "bottom-left", "bottom-right")
- `opacity` (float): Opacity of the watermark (0.0 to 1.0)

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = add_watermark_to_video(
    "./input/video.mp4",
    "./output/watermarked_video.mp4",
    "./watermarks/logo.png",
    position="bottom-right",
    opacity=0.6
)
```

### `add_intro_outro_to_video(input_path, output_path, intro_path=None, outro_path=None)`
Adds custom intro and/or outro to a video.

**Parameters:**
- `input_path` (str): Path to the input video
- `output_path` (str): Path to save the video with intro/outro
- `intro_path` (str, optional): Path to intro video
- `outro_path` (str, optional): Path to outro video

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = add_intro_outro_to_video(
    "./input/video.mp4",
    "./output/video_with_intro_outro.mp4",
    intro_path="./intros/intro.mp4",
    outro_path="./outros/outro.mp4"
)
```

### `generate_thumbnail_from_video(input_path, output_path, timestamp="00:00:05", size=(1280, 720))`
Generates a thumbnail from a video at a specific timestamp.

**Parameters:**
- `input_path` (str): Path to the input video
- `output_path` (str): Path to save the thumbnail
- `timestamp` (str): Timestamp in HH:MM:SS format
- `size` (tuple): Size of the thumbnail (width, height)

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = generate_thumbnail_from_video(
    "./input/video.mp4",
    "./thumbnails/thumb.jpg",
    timestamp="00:00:10",
    size=(1920, 1080)
)
```

### `add_subtitles_to_video(input_path, output_path, subtitles_path)`
Adds subtitles to a video from an SRT file.

**Parameters:**
- `input_path` (str): Path to the input video
- `output_path` (str): Path to save the video with subtitles
- `subtitles_path` (str): Path to SRT subtitle file

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = add_subtitles_to_video(
    "./input/video.mp4",
    "./output/video_with_subtitles.mp4",
    "./subtitles/subs.srt"
)
```

### `create_custom_intro(title, creator_name, duration=5, output_path="intro.mp4")`
Creates a custom intro video with title and creator name.

**Parameters:**
- `title` (str): Title for the intro
- `creator_name` (str): Creator name for the intro
- `duration` (int): Duration of the intro in seconds
- `output_path` (str): Path for output intro video

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = create_custom_intro(
    "Amazing Tutorial",
    "John Doe",
    duration=7,
    output_path="./intros/my_intro.mp4"
)
```

### `create_custom_outro(message, duration=5, output_path="outro.mp4")`
Creates a custom outro video with a message.

**Parameters:**
- `message` (str): Message for the outro
- `duration` (int): Duration of the outro in seconds
- `output_path` (str): Path for output outro video

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = create_custom_outro(
    "Thanks for watching!",
    duration=5,
    output_path="./outros/thanks_outro.mp4"
)
```

### `enhance_video_quality(input_path, output_path, brightness=1.0, contrast=1.0, saturation=1.0)`
Enhances video quality by adjusting brightness, contrast, and saturation.

**Parameters:**
- `input_path` (str): Path to the input video
- `output_path` (str): Path for output enhanced video
- `brightness` (float): Brightness multiplier (1.0 = no change)
- `contrast` (float): Contrast multiplier (1.0 = no change)
- `saturation` (float): Saturation multiplier (1.0 = no change)

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = enhance_video_quality(
    "./input/video.mp4",
    "./output/enhanced_video.mp4",
    brightness=1.1,
    contrast=1.2,
    saturation=1.1
)
```

## AI Content Analysis

### `AIContentAnalyzer`
A class to perform AI-powered content analysis on video titles, descriptions, and transcripts.

#### `__init__(self, openai_api_key=None)`
Initializes the AI Content Analyzer.

**Parameters:**
- `openai_api_key` (str, optional): OpenAI API key for GPT-based analysis

**Example:**
```python
analyzer = AIContentAnalyzer(openai_api_key="your-api-key")
```

#### `analyze_sentiment(self, text)`
Analyzes sentiment of the given text using multiple approaches.

**Parameters:**
- `text` (str): Text to analyze

**Returns:**
- `dict`: Sentiment scores from different analyzers

**Example:**
```python
analyzer = AIContentAnalyzer()
sentiment = analyzer.analyze_sentiment("This is an amazing video!")
print(sentiment)
```

#### `generate_content_suggestions(self, title, description, transcript="")`
Generates content optimization suggestions using AI.

**Parameters:**
- `title` (str): Video title
- `description` (str): Video description
- `transcript` (str, optional): Video transcript

**Returns:**
- `list`: Content optimization suggestions

**Example:**
```python
analyzer = AIContentAnalyzer()
suggestions = analyzer.generate_content_suggestions(
    "My Video Title",
    "This is my video description"
)
print(suggestions)
```

#### `generate_tags(self, title, description, transcript="")`
Generates relevant tags for the video content.

**Parameters:**
- `title` (str): Video title
- `description` (str): Video description
- `transcript` (str, optional): Video transcript

**Returns:**
- `list`: Relevant tags for the video

**Example:**
```python
analyzer = AIContentAnalyzer()
tags = analyzer.generate_tags(
    "My Video Title",
    "This is my video description"
)
print(tags)
```

#### `predict_engagement(self, title, description, tags, upload_hour, day_of_week)`
Predicts potential engagement metrics for the video.

**Parameters:**
- `title` (str): Video title
- `description` (str): Video description
- `tags` (list): Video tags
- `upload_hour` (int): Hour of day to upload (0-23)
- `day_of_week` (int): Day of week to upload (0=Monday, 6=Sunday)

**Returns:**
- `dict`: Predicted engagement metrics

**Example:**
```python
analyzer = AIContentAnalyzer()
engagement = analyzer.predict_engagement(
    "My Video Title",
    "This is my video description",
    ["tag1", "tag2", "tag3"],
    upload_hour=15,
    day_of_week=2
)
print(engagement)
```

#### `analyze_keywords(self, text, top_n=10)`
Analyzes and ranks keywords in the text by importance.

**Parameters:**
- `text` (str): Text to analyze
- `top_n` (int): Number of top keywords to return

**Returns:**
- `list`: Top keywords with their importance scores

**Example:**
```python
analyzer = AIContentAnalyzer()
keywords = analyzer.analyze_keywords("This is a sample text for keyword analysis", top_n=5)
print(keywords)
```

### `analyze_video_content(title, description, transcript="")`
Comprehensive AI analysis of video content.

**Parameters:**
- `title` (str): Video title
- `description` (str): Video description
- `transcript` (str, optional): Video transcript

**Returns:**
- `dict`: Comprehensive analysis results

**Example:**
```python
analysis = analyze_video_content(
    "My Video Title",
    "This is my video description",
    "This is the video transcript..."
)
print(analysis)
```

## Multi-Platform Support

### `MultiPlatformProcessor`
Processor that handles multiple platforms.

#### `__init__(self)`
Initializes the MultiPlatformProcessor.

**Example:**
```python
processor = MultiPlatformProcessor()
```

#### `detect_platform(self, url)`
Detects which platform a URL belongs to.

**Parameters:**
- `url` (str): URL to analyze

**Returns:**
- `str` or `None`: Platform name or None if not recognized

**Example:**
```python
processor = MultiPlatformProcessor()
platform = processor.detect_platform("https://vimeo.com/123456789")
print(platform)  # vimeo
```

#### `download_video(self, url, output_path)`
Downloads a video from any supported platform.

**Parameters:**
- `url` (str): URL of the video to download
- `output_path` (str): Path to save the downloaded video

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
processor = MultiPlatformProcessor()
success = processor.download_video(
    "https://vimeo.com/123456789",
    "./downloads/vimeo_video.mp4"
)
```

#### `get_video_info(self, url)`
Gets information about a video from any supported platform.

**Parameters:**
- `url` (str): URL of the video

**Returns:**
- `dict` or `None`: Video information or None if failed

**Example:**
```python
processor = MultiPlatformProcessor()
info = processor.get_video_info("https://tiktok.com/@user/video/123456789")
print(info)
```

#### `validate_url(self, url)`
Validates if the URL is valid for any supported platform.

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `bool`: True if valid, False otherwise

**Example:**
```python
processor = MultiPlatformProcessor()
is_valid = processor.validate_url("https://instagram.com/p/abcdefg/")
print(is_valid)
```

#### `get_supported_platforms(self)`
Gets list of supported platforms.

**Returns:**
- `list`: List of supported platform names

**Example:**
```python
processor = MultiPlatformProcessor()
platforms = processor.get_supported_platforms()
print(platforms)  # ['vimeo', 'tiktok', 'instagram']
```

### `process_cross_platform_video(url, config)`
Processes a video from any supported platform with the same workflow as YouTube videos.

**Parameters:**
- `url` (str): URL of the video to process
- `config` (dict): Configuration settings

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
config = load_config()
success = process_cross_platform_video("https://vimeo.com/123456789", config)
```

## Automation & Scheduling

### `ContentAutomationPipeline`
Class to manage content automation workflows.

#### `__init__(self)`
Initializes the ContentAutomationPipeline.

**Example:**
```python
pipeline = ContentAutomationPipeline()
```

#### `create_upload_workflow(self, video_path, title, description, tags, publish_datetime, social_media_posts=None)`
Creates a workflow for uploading and promoting content.

**Parameters:**
- `video_path` (str): Path to the video file
- `title` (str): Title of the video
- `description` (str): Description of the video
- `tags` (list): Tags for the video
- `publish_datetime` (datetime): When to publish the video
- `social_media_posts` (list, optional): Social media posts to schedule

**Returns:**
- `str`: Workflow ID

**Example:**
```python
from datetime import datetime, timedelta

pipeline = ContentAutomationPipeline()
future_time = datetime.now() + timedelta(days=1)

workflow_id = pipeline.create_upload_workflow(
    video_path="/path/to/video.mp4",
    title="My Awesome Video",
    description="Check out this awesome video!",
    tags=["awesome", "video", "tutorial"],
    publish_datetime=future_time,
    social_media_posts=[
        {
            'platform': 'twitter',
            'content': 'Just published a new video!',
            'delay_after_upload': 15,
            'include_video': False
        }
    ]
)
```

#### `create_recurring_workflow(self, workflow_func, interval_minutes, workflow_name, *args, **kwargs)`
Creates a recurring workflow.

**Parameters:**
- `workflow_func` (callable): Function to execute
- `interval_minutes` (int): Interval in minutes for recurring tasks
- `workflow_name` (str): Name of the workflow
- `*args`: Arguments to pass to the function
- `**kwargs`: Keyword arguments to pass to the function

**Returns:**
- `str`: Workflow ID

**Example:**
```python
def check_new_videos():
    print("Checking for new videos...")

pipeline = ContentAutomationPipeline()
workflow_id = pipeline.create_recurring_workflow(
    check_new_videos,
    interval_minutes=60,
    workflow_name="check_new_videos"
)
```

#### `start_automation(self)`
Starts the automation system.

**Example:**
```python
pipeline = ContentAutomationPipeline()
pipeline.start_automation()
```

#### `stop_automation(self)`
Stops the automation system.

**Example:**
```python
pipeline = ContentAutomationPipeline()
pipeline.stop_automation()
```

### `TaskScheduler`
Class to manage scheduled tasks.

#### `add_task(self, task_id, name, func, args=(), kwargs=None, run_at=None, interval_minutes=None)`
Adds a task to be scheduled.

**Parameters:**
- `task_id` (str): Unique identifier for the task
- `name` (str): Name of the task
- `func` (callable): Function to execute
- `args` (tuple): Arguments to pass to the function
- `kwargs` (dict): Keyword arguments to pass to the function
- `run_at` (datetime, optional): Specific time to run the task
- `interval_minutes` (int, optional): Interval in minutes for recurring tasks

**Returns:**
- `ScheduledTask`: The created task object

**Example:**
```python
scheduler = TaskScheduler()
task = scheduler.add_task(
    task_id="daily_backup",
    name="Daily Backup",
    func=backup_function,
    run_at=datetime.now() + timedelta(hours=1)
)
```

## Performance Optimization

### `cached_function(maxsize=128)`
Decorator to cache function results using LRU cache.

**Parameters:**
- `maxsize` (int): Maximum size of the cache

**Example:**
```python
@cached_function(maxsize=64)
def expensive_function(param):
    # Expensive computation
    return result
```

### `time_it(func)`
Decorator to time function execution.

**Parameters:**
- `func` (callable): Function to time

**Example:**
```python
@time_it
def my_function():
    # Some code
    pass
```

### `profile_function(func)`
Decorator to profile function execution with cProfile.

**Parameters:**
- `func` (callable): Function to profile

**Example:**
```python
@profile_function
def my_function():
    # Some code
    pass
```

### `ResourceManager`
Class to manage system resources efficiently.

#### `get_current_usage(self)`
Gets current resource usage.

**Returns:**
- `dict` or `None`: Current resource usage or None if error

**Example:**
```python
rm = ResourceManager()
usage = rm.get_current_usage()
if usage:
    print(f"CPU: {usage['cpu_percent']}%")
    print(f"Memory: {usage['memory_mb']:.2f} MB")
```

#### `is_within_limits(self)`
Checks if current resource usage is within limits.

**Returns:**
- `bool`: True if within limits, False otherwise

**Example:**
```python
rm = ResourceManager()
if rm.is_within_limits():
    print("Resources are within limits")
else:
    print("Resources are over limits")
```

## Enhanced Logging & Monitoring

### `AdvancedLogger`
Advanced logging class with multiple handlers and performance tracking.

#### `__init__(self, log_file="youtube_enhancement_tools_advanced.log", max_file_size=10485760, backup_count=5)`
Initializes the AdvancedLogger.

**Parameters:**
- `log_file` (str): Path to the log file
- `max_file_size` (int): Maximum size of log file before rotation (bytes)
- `backup_count` (int): Number of backup files to keep

**Example:**
```python
logger = AdvancedLogger(log_file="my_app.log")
```

#### `info(self, module, message, extra_data=None)`
Logs an info message.

**Parameters:**
- `module` (str): Module name
- `message` (str): Log message
- `extra_data` (dict, optional): Extra data to log

**Example:**
```python
logger = AdvancedLogger()
logger.info("MyModule", "Processing started", {"video_id": "abc123"})
```

### `PerformanceMonitor`
Class to monitor system and application performance.

#### `start_monitoring(self)`
Starts performance monitoring in a separate thread.

**Example:**
```python
pm = PerformanceMonitor()
pm.start_monitoring()
```

#### `get_current_metrics(self)`
Gets current performance metrics.

**Returns:**
- `dict`: Current performance metrics

**Example:**
```python
pm = PerformanceMonitor()
pm.start_monitoring()
metrics = pm.get_current_metrics()
print(metrics)
```

### `OperationTracker`
Tracks operations and their performance.

#### `start_operation(self, op_id, op_name, metadata=None)`
Starts tracking an operation.

**Parameters:**
- `op_id` (str): Operation ID
- `op_name` (str): Operation name
- `metadata` (dict, optional): Additional metadata

**Example:**
```python
tracker = OperationTracker()
tracker.start_operation("op_123", "Video Processing", {"video_id": "abc123"})
```

#### `end_operation(self, op_id, success=True, result=None)`
Ends tracking an operation.

**Parameters:**
- `op_id` (str): Operation ID
- `success` (bool): Whether the operation was successful
- `result` (any, optional): Result of the operation

**Returns:**
- `float` or `None`: Duration of the operation in seconds, or None if not found

**Example:**
```python
tracker = OperationTracker()
tracker.start_operation("op_123", "Video Processing")
# ... do work ...
duration = tracker.end_operation("op_123", success=True, result="Success")
```

---

**Note**: This API reference documentation is for version 1.0 of YouTube Enhancement Tools. For the latest API documentation, please check the official repository.