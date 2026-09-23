# YouTube Enhancement Tools v3.2.0 - Plugin Developer Guide

## Table of Contents

1. [Plugin Architecture Overview](#plugin-architecture-overview)
2. [Plugin Types](#plugin-types)
3. [Hook System](#hook-system)
4. [Creating Plugins Tutorial](#creating-plugins-tutorial)
5. [Plugin API Reference](#plugin-api-reference)
6. [Publishing Plugins](#publishing-plugins)
7. [Example Plugins](#example-plugins)

---

## Plugin Architecture Overview

### Design Philosophy

YouTube Enhancement Tools v3.2.0 uses a modular plugin architecture that allows developers to extend functionality without modifying core code. The plugin system is built on the following principles:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         PLUGIN ARCHITECTURE                               │
└──────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                        Core Application                              │
  │  ┌─────────────────────────────────────────────────────────────────┐│
  │  │                    Plugin Manager                                ││
  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             ││
  │  │  │  Discovery  │  │   Loader    │  │  Lifecycle  │             ││
  │  │  │  Engine     │  │   Service   │  │  Manager    │             ││
  │  │  └─────────────┘  └─────────────┘  └─────────────┘             ││
  │  └─────────────────────────────────────────────────────────────────┘│
  │  ┌─────────────────────────────────────────────────────────────────┐│
  │  │                      Hook System                                 ││
  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             ││
  │  │  │   Hook      │  │   Filter    │  │   Event     │             ││
  │  │  │  Registry   │  │   Chain     │  │   Bus       │             ││
  │  │  └─────────────┘  └─────────────┘  └─────────────┘             ││
  │  └─────────────────────────────────────────────────────────────────┘│
  └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                         Plugin Layer                                 │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
  │  │  Processor  │  │  Analyzer   │  │  Exporter   │  │  Notifier   ││
  │  │   Plugin    │  │   Plugin    │  │   Plugin    │  │   Plugin    ││
  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
  │  │  Storage    │  │   Auth      │  │   UI        │  │  Custom     ││
  │  │   Plugin    │  │   Plugin    │  │   Plugin    │  │   Plugin    ││
  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│
  └─────────────────────────────────────────────────────────────────────┘
```

### Plugin Lifecycle

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         PLUGIN LIFECYCLE                                  │
└──────────────────────────────────────────────────────────────────────────┘

    DISCOVERY          LOADING          INITIALIZATION       RUNNING
        │                 │                  │                  │
        ▼                 ▼                  ▼                  │
  ┌──────────┐      ┌──────────┐      ┌──────────┐            │
  │  Scan    │─────▶│  Load    │─────▶│Initialize│────────────┤
  │  Plugins │      │  Module  │      │  Plugin  │            │
  └──────────┘      └──────────┘      └──────────┘            │
        ▲                 │                  │                  │
        │                 ▼                  ▼                  ▼
        │           ┌──────────┐      ┌──────────┐      ┌──────────┐
        └───────────│  Unload  │◀─────│Shutdown  │◀─────│  Error   │
                    │  Plugin  │      │  Plugin  │      │  State   │
                    └──────────┘      └──────────┘      └──────────┘

States:
├── unloaded: Plugin discovered but not loaded
├── loaded: Plugin module loaded, not initialized
├── initialized: Plugin ready and active
├── running: Plugin processing events/hooks
├── error: Plugin encountered an error
└── disabled: Plugin manually disabled
```

### Plugin Directory Structure

```
my_plugin/
├── __init__.py              # Plugin entry point
├── plugin.py                # Main plugin class
├── hooks.py                 # Hook implementations
├── config.py                # Plugin configuration
├── utils.py                 # Utility functions
├── templates/               # Template files (if needed)
└── tests/                   # Plugin tests
    ├── __init__.py
    └── test_plugin.py
```

---

## Plugin Types

### 1. Processor Plugins

Processor plugins modify or enhance video processing pipelines.

```python
from youtube_enhancement_tools.plugins import BasePlugin, ProcessContext

class VideoWatermarkPlugin(BasePlugin):
    """Add watermarks to processed videos."""
    
    name = "video_watermark"
    version = "1.0.0"
    description = "Adds customizable watermarks to videos"
    author = "Your Name"
    
    def __init__(self):
        super().__init__()
        self.watermark_path = None
    
    async def on_initialize(self):
        """Load watermark configuration."""
        self.watermark_path = self.get_config("watermark_path")
        self.position = self.get_config("position", "bottom-right")
        self.opacity = self.get_config("opacity", 0.8)
    
    def register_hooks(self):
        """Register processing hooks."""
        self.register_hook(
            "video.post_process",
            self.add_watermark,
            priority=10
        )
    
    async def add_watermark(self, context: ProcessContext):
        """Add watermark to processed video."""
        if not self.watermark_path:
            return
        
        video_path = context.output_path
        watermarked_path = video_path.with_name(
            f"{video_path.stem}_watermarked{video_path.suffix}"
        )
        
        await self.context.processor.add_watermark(
            video_path,
            self.watermark_path,
            watermarked_path,
            position=self.position,
            opacity=self.opacity
        )
        
        context.output_path = watermarked_path
        self.log("info", f"Added watermark to {video_path}")
```

### 2. Analyzer Plugins

Analyzer plugins provide additional analytics and insights.

```python
from youtube_enhancement_tools.plugins import BasePlugin
from youtube_enhancement_tools.analytics import MetricsData

class SentimentAnalyzerPlugin(BasePlugin):
    """Analyze comment sentiment for videos."""
    
    name = "sentiment_analyzer"
    version = "1.0.0"
    description = "Performs sentiment analysis on video comments"
    author = "Your Name"
    
    def __init__(self):
        super().__init__()
        self.model = None
    
    async def on_initialize(self):
        """Initialize sentiment analysis model."""
        from transformers import pipeline
        self.model = pipeline("sentiment-analysis")
    
    def register_hooks(self):
        """Register analysis hooks."""
        self.register_hook(
            "analytics.post_fetch",
            self.analyze_sentiment,
            priority=5
        )
    
    async def analyze_sentiment(self, context: AnalysisContext):
        """Analyze sentiment of comments."""
        comments = context.comments
        
        sentiments = []
        for comment in comments[:100]:  # Limit for performance
            result = self.model(comment.text)[0]
            sentiments.append({
                "comment_id": comment.id,
                "label": result["label"],
                "score": result["score"]
            })
        
        # Calculate overall sentiment
        positive = sum(1 for s in sentiments if s["label"] == "POSITIVE")
        negative = sum(1 for s in sentiments if s["label"] == "NEGATIVE")
        
        context.extra_data["sentiment"] = {
            "positive_ratio": positive / len(sentiments) if sentiments else 0,
            "negative_ratio": negative / len(sentiments) if sentiments else 0,
            "total_analyzed": len(sentiments)
        }
        
        self.log("info", f"Analyzed sentiment for {len(sentiments)} comments")
```

### 3. Exporter Plugins

Exporter plugins handle output to various formats and destinations.

```python
from youtube_enhancement_tools.plugins import BasePlugin

class S3ExporterPlugin(BasePlugin):
    """Export processed videos to Amazon S3."""
    
    name = "s3_exporter"
    version = "1.0.0"
    description = "Exports videos to Amazon S3 bucket"
    author = "Your Name"
    
    def __init__(self):
        super().__init__()
        self.s3_client = None
        self.bucket = None
    
    async def on_initialize(self):
        """Initialize S3 client."""
        import aioboto3
        
        self.bucket = self.get_config("bucket")
        session = aioboto3.Session(
            aws_access_key_id=self.get_config("aws_access_key"),
            aws_secret_access_key=self.get_config("aws_secret_key"),
            region_name=self.get_config("region", "us-east-1")
        )
        self.s3_client = session.client("s3")
    
    def register_hooks(self):
        """Register export hooks."""
        self.register_hook(
            "video.post_upload",
            self.export_to_s3,
            priority=1
        )
    
    async def export_to_s3(self, context: ProcessContext):
        """Export video to S3."""
        if not context.output_path:
            return
        
        key = f"videos/{context.video.id}/{context.output_path.name}"
        
        async with self.s3_client:
            await self.s3_client.upload_file(
                str(context.output_path),
                self.bucket,
                key,
                ExtraArgs={
                    "ContentType": "video/mp4",
                    "ACL": "public-read"
                }
            )
        
        context.extra_data["s3_url"] = f"s3://{self.bucket}/{key}"
        self.log("info", f"Exported to s3://{self.bucket}/{key}")
```

### 4. Notifier Plugins

Notifier plugins send notifications about events.

```python
from youtube_enhancement_tools.plugins import BasePlugin

class DiscordNotifierPlugin(BasePlugin):
    """Send notifications to Discord webhook."""
    
    name = "discord_notifier"
    version = "1.0.0"
    description = "Sends processing notifications to Discord"
    author = "Your Name"
    
    def __init__(self):
        super().__init__()
        self.webhook_url = None
    
    async def on_initialize(self):
        """Initialize Discord webhook."""
        self.webhook_url = self.get_config("webhook_url")
    
    def register_hooks(self):
        """Register notification hooks."""
        self.register_hook("video.processing_complete", self.notify_complete)
        self.register_hook("video.processing_failed", self.notify_failed)
        self.register_hook("video.uploaded", self.notify_uploaded)
    
    async def notify_complete(self, context: ProcessContext):
        """Notify when processing completes."""
        embed = {
            "title": "✅ Video Processing Complete",
            "color": 0x00ff00,
            "fields": [
                {"name": "Video", "value": context.video.title, "inline": False},
                {"name": "Output", "value": str(context.output_path), "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._send_webhook(embed)
    
    async def notify_failed(self, context: ProcessContext):
        """Notify when processing fails."""
        embed = {
            "title": "❌ Video Processing Failed",
            "color": 0xff0000,
            "fields": [
                {"name": "Video", "value": context.video.title, "inline": False},
                {"name": "Error", "value": str(context.error), "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._send_webhook(embed)
    
    async def _send_webhook(self, embed: dict):
        """Send embed to Discord webhook."""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                self.webhook_url,
                json={"embeds": [embed]}
            )
```

### 5. Filter Plugins

Filter plugins modify data flowing through the system.

```python
from youtube_enhancement_tools.plugins import BasePlugin

class ContentFilterPlugin(BasePlugin):
    """Filter videos based on content criteria."""
    
    name = "content_filter"
    version = "1.0.0"
    description = "Filters videos based on title, tags, and duration"
    author = "Your Name"
    
    def __init__(self):
        super().__init__()
        self.filters = {}
    
    async def on_initialize(self):
        """Load filter configuration."""
        self.filters = self.get_config("filters", {})
    
    def register_hooks(self):
        """Register filter hooks."""
        self.add_filter(
            "video.pre_process",
            self.filter_video,
            priority=100  # High priority to filter early
        )
    
    def filter_video(self, video: VideoData) -> Optional[VideoData]:
        """Filter video based on criteria."""
        # Check minimum duration
        min_duration = self.filters.get("min_duration_seconds")
        if min_duration and video.duration.total_seconds() < min_duration:
            self.log("info", f"Filtered {video.id}: too short")
            return None
        
        # Check required tags
        required_tags = self.filters.get("required_tags", [])
        if required_tags:
            if not any(tag in video.tags for tag in required_tags):
                self.log("info", f"Filtered {video.id}: missing tags")
                return None
        
        # Check title keywords
        blocked_keywords = self.filters.get("blocked_keywords", [])
        if any(kw.lower() in video.title.lower() for kw in blocked_keywords):
            self.log("info", f"Filtered {video.id}: blocked keyword")
            return None
        
        return video
```

### Plugin Type Comparison

| Type | Use Case | Key Hooks | Example |
|------|----------|-----------|---------|
| Processor | Modify videos | `video.pre_process`, `video.post_process` | Watermark, trim, transcode |
| Analyzer | Extract insights | `analytics.post_fetch` | Sentiment, trends, demographics |
| Exporter | Output data | `video.post_upload` | S3, GCS, FTP export |
| Notifier | Send alerts | `*.complete`, `*.failed` | Discord, Slack, Email |
| Filter | Filter data | `video.pre_process` | Content filtering, validation |

---

## Hook System

### Available Hook Points

```python
# Video Processing Hooks
HOOK_VIDEO_PRE_DOWNLOAD = "video.pre_download"
HOOK_VIDEO_POST_DOWNLOAD = "video.post_download"
HOOK_VIDEO_PRE_PROCESS = "video.pre_process"
HOOK_VIDEO_POST_PROCESS = "video.post_process"
HOOK_VIDEO_PRE_UPLOAD = "video.pre_upload"
HOOK_VIDEO_POST_UPLOAD = "video.post_upload"
HOOK_VIDEO_PROCESSING_COMPLETE = "video.processing_complete"
HOOK_VIDEO_PROCESSING_FAILED = "video.processing_failed"

# Analytics Hooks
HOOK_ANALYTICS_PRE_FETCH = "analytics.pre_fetch"
HOOK_ANALYTICS_POST_FETCH = "analytics.post_fetch"
HOOK_ANALYTICS_POST_PROCESS = "analytics.post_process"

# Channel Hooks
HOOK_CHANNEL_UPDATE = "channel.on_update"
HOOK_CHANNEL_SUBSCRIBER_CHANGE = "channel.subscriber_change"

# System Hooks
HOOK_SYSTEM_STARTUP = "system.on_startup"
HOOK_SYSTEM_SHUTDOWN = "system.on_shutdown"
HOOK_SYSTEM_ERROR = "system.on_error"
HOOK_SYSTEM_QUOTA_WARNING = "system.quota_warning"
```

### Hook Registration

```python
from youtube_enhancement_tools.plugins import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"
    
    def register_hooks(self):
        """Register all plugin hooks."""
        
        # Simple hook registration
        self.register_hook(
            "video.post_process",
            self.handle_post_process
        )
        
        # Hook with priority (higher = executes first)
        self.register_hook(
            "video.pre_process",
            self.handle_pre_process,
            priority=50
        )
        
        # Hook with condition
        self.register_hook(
            "video.post_upload",
            self.handle_upload,
            condition=lambda ctx: ctx.video.duration.total_seconds() > 60
        )
    
    async def handle_post_process(self, context: ProcessContext):
        """Handle post-process event."""
        pass
```

### Hook Context Objects

```python
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class ProcessContext:
    """Context for video processing hooks."""
    video: VideoData
    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    options: Optional[ProcessOptions] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None
    
    @property
    def success(self) -> bool:
        return self.error is None

@dataclass
class AnalysisContext:
    """Context for analytics hooks."""
    channel_id: str
    metrics: MetricsData
    comments: List[CommentData] = field(default_factory=list)
    extra_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventContext:
    """Context for system event hooks."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
```

### Filter Chain

```python
from youtube_enhancement_tools.plugins import BasePlugin

class FilterChainPlugin(BasePlugin):
    """Demonstrates filter chain usage."""
    
    name = "filter_chain"
    version = "1.0.0"
    
    def register_hooks(self):
        """Register filters in chain."""
        # Filters are applied in priority order (highest first)
        self.add_filter("video.data", self.filter_step1, priority=100)
        self.add_filter("video.data", self.filter_step2, priority=50)
        self.add_filter("video.data", self.filter_step3, priority=10)
    
    def filter_step1(self, data: Dict) -> Dict:
        """First filter in chain."""
        data["processed_by_step1"] = True
        return data
    
    def filter_step2(self, data: Dict) -> Dict:
        """Second filter in chain."""
        if data.get("processed_by_step1"):
            data["processed_by_step2"] = True
        return data
    
    def filter_step3(self, data: Dict) -> Dict:
        """Third filter in chain."""
        data["final"] = True
        return data
```

---

## Creating Plugins Tutorial

### Step 1: Set Up Plugin Project

```bash
# Create plugin directory
mkdir my_youtube_plugin
cd my_youtube_plugin

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install plugin SDK
pip install youtube-enhancement-tools-plugin-sdk

# Create project structure
mkdir -p my_youtube_plugin tests
touch my_youtube_plugin/__init__.py
touch my_youtube_plugin/plugin.py
touch tests/__init__.py
```

### Step 2: Create Plugin Entry Point

```python
# my_youtube_plugin/__init__.py
"""My YouTube Plugin - A sample plugin for YouTube Enhancement Tools."""

from .plugin import MyYouTubePlugin

__version__ = "1.0.0"
__all__ = ["MyYouTubePlugin"]

# Plugin metadata for discovery
PLUGIN_ENTRY_POINT = "my_youtube_plugin:MyYouTubePlugin"
```

### Step 3: Implement Plugin Class

```python
# my_youtube_plugin/plugin.py
"""Main plugin implementation."""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from youtube_enhancement_tools.plugins import (
    BasePlugin,
    PluginContext,
    ProcessContext,
    register_plugin
)
from youtube_enhancement_tools.core.types import VideoData


@register_plugin
class MyYouTubePlugin(BasePlugin):
    """
    A sample plugin that demonstrates core plugin functionality.
    
    This plugin adds custom metadata to processed videos and
    sends notifications when processing completes.
    """
    
    # Required plugin metadata
    name = "my_youtube_plugin"
    version = "1.0.0"
    description = "Custom metadata and notifications for videos"
    author = "Your Name"
    website = "https://github.com/yourusername/my_youtube_plugin"
    
    # Optional: Plugin dependencies
    dependencies = ["video_processor>=3.0.0"]
    
    # Optional: Required configuration
    config_schema = {
        "type": "object",
        "properties": {
            "notification_enabled": {
                "type": "boolean",
                "default": True
            },
            "metadata_prefix": {
                "type": "string",
                "default": "[Processed]"
            },
            "webhook_url": {
                "type": "string",
                "format": "uri"
            }
        },
        "required": ["webhook_url"]
    }
    
    def __init__(self):
        """Initialize plugin state."""
        super().__init__()
        self._initialized = False
        self._processed_count = 0
    
    async def on_initialize(self) -> None:
        """
        Called when plugin is initialized.
        
        Use this for async setup like connecting to services.
        """
        self._config = {
            "notification_enabled": self.get_config("notification_enabled", True),
            "metadata_prefix": self.get_config("metadata_prefix", "[Processed]"),
            "webhook_url": self.get_config("webhook_url")
        }
        self._initialized = True
        self.log("info", f"Plugin {self.name} v{self.version} initialized")
    
    async def shutdown(self) -> None:
        """
        Called when plugin is being unloaded.
        
        Use this for cleanup like closing connections.
        """
        self.log("info", f"Plugin {self.name} shutting down")
        self._initialized = False
    
    def register_hooks(self) -> None:
        """
        Register all plugin hooks.
        
        Called during plugin initialization.
        """
        # Register video processing hook
        self.register_hook(
            hook_name="video.post_process",
            callback=self.on_video_processed,
            priority=10
        )
        
        # Register system startup hook
        self.register_hook(
            hook_name="system.on_startup",
            callback=self.on_system_startup,
            priority=0
        )
    
    async def on_video_processed(self, context: ProcessContext) -> None:
        """
        Handle video processing completion.
        
        Args:
            context: Processing context with video and output info
        """
        if not self._initialized:
            return
        
        self._processed_count += 1
        
        # Add custom metadata
        metadata_file = context.output_path.with_suffix(".meta.json")
        metadata = {
            "processed_by": self.name,
            "processed_at": datetime.utcnow().isoformat(),
            "video_id": context.video.id,
            "original_title": context.video.title,
            "metadata_prefix": self._config["metadata_prefix"]
        }
        
        # Write metadata file
        import json
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.log(
            "info",
            f"Processed video: {context.video.title}",
            extra={"video_id": context.video.id}
        )
        
        # Send notification if enabled
        if self._config["notification_enabled"] and self._config["webhook_url"]:
            await self._send_notification(context)
    
    async def on_system_startup(self, event_data: Dict[str, Any]) -> None:
        """Handle system startup event."""
        self.log("info", "System startup detected, plugin ready")
    
    async def _send_notification(self, context: ProcessContext) -> None:
        """Send notification to webhook."""
        import aiohttp
        
        payload = {
            "text": f"✅ Video processed: {context.video.title}",
            "attachments": [{
                "fields": [
                    {"title": "Video ID", "value": context.video.id},
                    {"title": "Output", "value": str(context.output_path)}
                ]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self._config["webhook_url"], json=payload)
        except Exception as e:
            self.log("error", f"Failed to send notification: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get plugin statistics.
        
        Returns:
            Dict with plugin statistics
        """
        return {
            "name": self.name,
            "version": self.version,
            "processed_count": self._processed_count,
            "initialized": self._initialized
        }
```

### Step 4: Create Plugin Configuration

```python
# my_youtube_plugin/config.py
"""Plugin configuration handling."""

from typing import Any, Dict
from pathlib import Path

DEFAULT_CONFIG: Dict[str, Any] = {
    "notification_enabled": True,
    "metadata_prefix": "[Processed]",
    "webhook_url": None,
    "log_level": "INFO"
}

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from file."""
    import json
    
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    
    with open(config_path) as f:
        user_config = json.load(f)
    
    # Merge with defaults
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    
    return config

def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
```

### Step 5: Write Plugin Tests

```python
# tests/test_plugin.py
"""Tests for MyYouTubePlugin."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from my_youtube_plugin import MyYouTubePlugin
from youtube_enhancement_tools.plugins import ProcessContext
from youtube_enhancement_tools.core.types import VideoData


class TestMyYouTubePlugin:
    """Test cases for MyYouTubePlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return MyYouTubePlugin()
    
    @pytest.fixture
    def sample_video(self):
        """Create sample video data."""
        return VideoData(
            id="test_video_id",
            title="Test Video",
            description="Test description",
            channel_id="UC_test",
            channel_title="Test Channel",
            published_at=datetime(2026, 1, 1),
            duration=timedelta(minutes=5)
        )
    
    @pytest.fixture
    def process_context(self, sample_video, tmp_path):
        """Create process context."""
        output_path = tmp_path / "output.mp4"
        output_path.write_bytes(b"fake video")
        
        return ProcessContext(
            video=sample_video,
            output_path=output_path
        )
    
    @pytest.mark.asyncio
    async def test_plugin_initialization(self, plugin):
        """Test plugin initializes correctly."""
        # Mock config
        with patch.object(plugin, 'get_config') as mock_config:
            mock_config.side_effect = lambda key, default=None: default
            await plugin.on_initialize()
            
            assert plugin._initialized is True
    
    @pytest.mark.asyncio
    async def test_video_processed_creates_metadata(
        self,
        plugin,
        process_context,
        tmp_path
    ):
        """Test that processing creates metadata file."""
        plugin._initialized = True
        plugin._config = {
            "notification_enabled": False,
            "metadata_prefix": "[Test]",
            "webhook_url": None
        }
        
        await plugin.on_video_processed(process_context)
        
        # Check metadata file was created
        metadata_file = process_context.output_path.with_suffix(".meta.json")
        assert metadata_file.exists()
    
    @pytest.mark.asyncio
    async def test_plugin_stats(self, plugin):
        """Test plugin statistics."""
        plugin._processed_count = 5
        plugin._initialized = True
        
        stats = plugin.get_stats()
        
        assert stats["processed_count"] == 5
        assert stats["initialized"] is True
        assert stats["name"] == "my_youtube_plugin"
```

### Step 6: Create Plugin Package

```python
# setup.py
"""Setup script for my_youtube_plugin."""

from setuptools import setup, find_packages

setup(
    name="my-youtube-plugin",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Custom metadata and notifications for YouTube videos",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_youtube_plugin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.10",
    install_requires=[
        "youtube-enhancement-tools>=3.2.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
    entry_points={
        "youtube_enhancement_tools.plugins": [
            "my_youtube_plugin = my_youtube_plugin:MyYouTubePlugin",
        ],
    },
)
```

---

## Plugin API Reference

### BasePlugin Class

```python
class BasePlugin(ABC):
    """
    Abstract base class for all plugins.
    
    All plugins must inherit from this class and implement
    required attributes and methods.
    """
    
    # Required class attributes
    name: str = ""           # Unique plugin identifier
    version: str = ""        # Plugin version (semver)
    description: str = ""    # Plugin description
    author: str = ""         # Plugin author
    
    # Optional class attributes
    website: str = ""        # Plugin website/documentation
    license: str = ""        # Plugin license
    dependencies: List[str] = []  # Plugin dependencies
    
    def __init__(self):
        """Initialize plugin."""
        self._context: Optional[PluginContext] = None
        self._hooks: List[Hook] = []
        self._filters: List[Filter] = []
    
    @property
    def context(self) -> Optional[PluginContext]:
        """Get the plugin context."""
        return self._context
    
    async def initialize(self, context: PluginContext) -> None:
        """
        Initialize the plugin.
        
        Called by the plugin manager when loading the plugin.
        
        Args:
            context: Plugin context with APIs and configuration
        """
        self._context = context
        await self.on_initialize()
        self.register_hooks()
    
    async def on_initialize(self) -> None:
        """
        Plugin initialization hook.
        
        Override this method for custom initialization logic.
        This is called after the context is set.
        """
        pass
    
    async def shutdown(self) -> None:
        """
        Shutdown the plugin.
        
        Override this method for cleanup logic.
        Called when the plugin is being unloaded.
        """
        pass
    
    def register_hook(
        self,
        hook_name: str,
        callback: Callable,
        priority: int = 0,
        condition: Optional[Callable[[Any], bool]] = None
    ) -> None:
        """
        Register a hook callback.
        
        Args:
            hook_name: Name of the hook point
            callback: Async function to call when hook is triggered
            priority: Execution priority (higher = earlier)
            condition: Optional condition function that must return True
        """
        hook = Hook(
            name=hook_name,
            callback=callback,
            priority=priority,
            condition=condition,
            plugin=self.name
        )
        self._hooks.append(hook)
        self.context.hook_system.register(hook)
    
    def add_filter(
        self,
        filter_name: str,
        callback: Callable,
        priority: int = 0
    ) -> None:
        """
        Add a data filter.
        
        Args:
            filter_name: Name of the filter point
            callback: Function that transforms data
            priority: Filter priority (higher = earlier)
        """
        filter_obj = Filter(
            name=filter_name,
            callback=callback,
            priority=priority,
            plugin=self.name
        )
        self._filters.append(filter_obj)
        self.context.hook_system.add_filter(filter_obj)
    
    def log(
        self,
        level: str,
        message: str,
        **kwargs
    ) -> None:
        """
        Log a message.
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            **kwargs: Additional context for structured logging
        """
        self.context.logger.log(
            level,
            f"[{self.name}] {message}",
            **kwargs
        )
    
    def get_config(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get plugin configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        plugin_config = self.context.config.get("plugins", {}).get(self.name, {})
        return plugin_config.get(key, default)
    
    def emit_event(
        self,
        event_name: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Emit a custom event.
        
        Args:
            event_name: Event name
            data: Event data payload
        """
        self.context.event_bus.emit(
            f"plugin.{self.name}.{event_name}",
            data
        )
```

### PluginContext Class

```python
@dataclass
class PluginContext:
    """
    Context object provided to plugins.
    
    Provides access to core services and configuration.
    """
    
    # Core services
    client: YouTubeClient           # YouTube API client
    processor: VideoProcessor       # Video processor
    storage: StorageService         # Storage service
    cache: CacheService             # Cache service
    database: DatabaseService       # Database service
    
    # Plugin system
    hook_system: HookSystem         # Hook registration system
    event_bus: EventBus             # Event bus
    plugin_manager: PluginManager   # Plugin manager reference
    
    # Configuration
    config: Dict[str, Any]          # Full configuration
    logger: Logger                  # Logger instance
    
    # Runtime info
    version: str                    # Application version
    python_version: str             # Python version
    platform: str                   # Platform info
    
    def get_service(self, name: str) -> Any:
        """Get a service by name."""
        services = {
            "client": self.client,
            "processor": self.processor,
            "storage": self.storage,
            "cache": self.cache,
            "database": self.database
        }
        return services.get(name)
```

### Hook Registration Decorator

```python
def register_plugin(cls):
    """
    Decorator to register a plugin class.
    
    Usage:
        @register_plugin
        class MyPlugin(BasePlugin):
            pass
    """
    if not hasattr(cls, 'name') or not cls.name:
        raise ValueError("Plugin must have a 'name' attribute")
    
    # Register in plugin registry
    PluginRegistry.register(cls.name, cls)
    
    return cls


def hook(hook_name: str, priority: int = 0):
    """
    Decorator to register a method as a hook.
    
    Usage:
        @hook("video.post_process", priority=10)
        async def on_video_processed(self, context):
            pass
    """
    def decorator(func):
        func._hook_info = {
            "name": hook_name,
            "priority": priority
        }
        return func
    return decorator
```

---

## Publishing Plugins

### Plugin Distribution

#### 1. Package Your Plugin

```bash
# Ensure you have build tools
pip install build twine

# Build distribution packages
python -m build

# This creates:
# dist/my_youtube_plugin-1.0.0.tar.gz
# dist/my_youtube_plugin-1.0.0-py3-none-any.whl
```

#### 2. Test Locally

```bash
# Install in test environment
pip install dist/my_youtube_plugin-1.0.0-py3-none-any.whl

# Verify plugin is discoverable
python -c "from youtube_enhancement_tools.plugins import PluginManager; print(PluginManager().discover())"
```

#### 3. Publish to PyPI

```bash
# Test PyPI first
python -m twine upload --repository testpypi dist/*

# Verify installation from test PyPI
pip install --index-url https://test.pypi.org/simple/ my-youtube-plugin

# Publish to real PyPI
python -m twine upload dist/*
```

### Plugin Registry

Submit your plugin to the official registry:

1. Fork the plugin registry repository
2. Add your plugin to `plugins.json`:

```json
{
  "plugins": [
    {
      "name": "my_youtube_plugin",
      "version": "1.0.0",
      "description": "Custom metadata and notifications",
      "author": "Your Name",
      "package": "my-youtube-plugin",
      "repository": "https://github.com/yourusername/my_youtube_plugin",
      "tags": ["metadata", "notifications", "webhook"]
    }
  ]
}
```

3. Submit a pull request

### Plugin Badge

Add this badge to your README:

```markdown
[![YouTube Enhancement Tools Plugin](https://img.shields.io/badge/YT_Enhancement-Plugin-blue)](https://github.com/your-org/youtube-enhancement-tools)
```

---

## Example Plugins

### Example 1: Auto-Thumbnail Generator

```python
"""Auto-thumbnail generator plugin."""

from youtube_enhancement_tools.plugins import BasePlugin, ProcessContext
from pathlib import Path


class AutoThumbnailPlugin(BasePlugin):
    """Automatically generates thumbnails from videos."""
    
    name = "auto_thumbnail"
    version = "1.0.0"
    description = "Generates thumbnails at optimal timestamps"
    
    async def on_initialize(self):
        self.quality = self.get_config("quality", "high")
        self.timestamp_strategy = self.get_config("timestamp_strategy", "auto")
    
    def register_hooks(self):
        self.register_hook(
            "video.post_process",
            self.generate_thumbnail,
            priority=5
        )
    
    async def generate_thumbnail(self, context: ProcessContext):
        """Generate thumbnail from video."""
        video_path = context.output_path
        
        # Calculate optimal timestamp
        if self.timestamp_strategy == "auto":
            # Use 25% into the video
            timestamp = context.video.duration.total_seconds() * 0.25
        else:
            timestamp = float(self.timestamp_strategy)
        
        # Generate thumbnail
        thumbnail_path = video_path.with_name(
            f"{video_path.stem}_thumbnail.jpg"
        )
        
        await self.context.processor.generate_thumbnail(
            video_path,
            thumbnail_path,
            timestamp=timestamp
        )
        
        context.extra_data["thumbnail_path"] = str(thumbnail_path)
        self.log("info", f"Generated thumbnail: {thumbnail_path}")
```

### Example 2: Title Optimizer

```python
"""Video title optimizer plugin."""

from youtube_enhancement_tools.plugins import BasePlugin
from youtube_enhancement_tools.core.types import VideoData


class TitleOptimizerPlugin(BasePlugin):
    """Optimizes video titles for SEO."""
    
    name = "title_optimizer"
    version = "1.0.0"
    description = "Optimizes video titles with keywords and formatting"
    
    async def on_initialize(self):
        self.keywords = self.get_config("keywords", [])
        self.max_length = self.get_config("max_length", 60)
        self.prefix = self.get_config("prefix", "")
        self.suffix = self.get_config("suffix", "")
    
    def register_hooks(self):
        self.add_filter(
            "video.metadata",
            self.optimize_title,
            priority=50
        )
    
    def optimize_title(self, video: VideoData) -> VideoData:
        """Optimize video title."""
        title = video.title
        
        # Add prefix
        if self.prefix:
            title = f"{self.prefix} {title}"
        
        # Add keywords if not present
        for keyword in self.keywords:
            if keyword.lower() not in title.lower():
                title = f"{title} - {keyword}"
                break
        
        # Add suffix
        if self.suffix:
            title = f"{title} {self.suffix}"
        
        # Truncate if too long
        if len(title) > self.max_length:
            title = title[:self.max_length - 3] + "..."
        
        video.title = title
        return video
```

### Example 3: Batch Processor

```python
"""Batch video processor plugin."""

import asyncio
from youtube_enhancement_tools.plugins import BasePlugin


class BatchProcessorPlugin(BasePlugin):
    """Processes videos in batches for efficiency."""
    
    name = "batch_processor"
    version = "1.0.0"
    description = "Efficient batch processing of multiple videos"
    
    async def on_initialize(self):
        self.batch_size = self.get_config("batch_size", 5)
        self.max_concurrent = self.get_config("max_concurrent", 2)
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
    
    def register_hooks(self):
        self.register_hook(
            "system.on_startup",
            self.on_startup
        )
    
    async def on_startup(self, event_data: dict):
        """Process pending videos in batches."""
        pending_videos = await self._get_pending_videos()
        
        batches = [
            pending_videos[i:i + self.batch_size]
            for i in range(0, len(pending_videos), self.batch_size)
        ]
        
        for batch in batches:
            await self._process_batch(batch)
    
    async def _process_batch(self, videos: list):
        """Process a batch of videos."""
        tasks = [
            self._process_single(video)
            for video in videos
        ]
        await asyncio.gather(*tasks)
    
    async def _process_single(self, video):
        """Process a single video with concurrency control."""
        async with self.semaphore:
            try:
                await self.context.processor.process(video)
                self.log("info", f"Processed: {video.title}")
            except Exception as e:
                self.log("error", f"Failed: {video.title} - {e}")
```

---

*Documentation generated for YouTube Enhancement Tools v3.2.0*
*Last updated: March 4, 2026*
