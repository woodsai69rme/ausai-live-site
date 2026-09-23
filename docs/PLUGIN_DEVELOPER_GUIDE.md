# YouTube Enhancement Tools - Plugin Developer Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Plugin Architecture Overview](#plugin-architecture-overview)
4. [Creating Your First Plugin](#creating-your-first-plugin)
5. [Plugin Types](#plugin-types)
6. [Plugin Hooks](#plugin-hooks)
7. [Plugin Configuration](#plugin-configuration)
8. [Plugin Discovery](#plugin-discovery)
9. [Testing Plugins](#testing-plugins)
10. [Publishing Plugins](#publishing-plugins)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

The YouTube Enhancement Tools (YET) Plugin System allows developers to extend the functionality of YET without modifying the core application. This guide will help you create, test, and distribute plugins.

### What Can Plugins Do?

- **Download videos** from new platforms (Vimeo, Twitch, etc.)
- **Process videos** with custom effects and filters
- **Enhance quality** using AI models
- **Export content** to various platforms and cloud services
- **Add custom hooks** for notifications, logging, and more

### Plugin System Features

- Automatic plugin discovery
- Version compatibility checking
- Dependency management
- Hook-based extensibility
- Configuration management
- Error isolation

---

## Getting Started

### Prerequisites

- Python 3.9+
- YouTube Enhancement Tools v3.0.0+
- Basic Python programming knowledge

### Installation

1. Create a plugins directory:
```bash
mkdir -p ~/.youtube_enhancement_tools/plugins
```

2. Create your plugin file:
```bash
touch ~/.youtube_enhancement_tools/plugins/my_plugin.py
```

3. Start coding!

### Quick Start Example

```python
from plugins.base import BasePlugin

class MyFirstPlugin(BasePlugin):
    name = "my_first_plugin"
    version = "1.0.0"
    description = "My first YET plugin"
    author = "Your Name"
    
    def initialize(self, config):
        self.logger.info("Plugin initialized!")
        return True
    
    def shutdown(self):
        self.logger.info("Plugin shutting down")
        return True
```

---

## Plugin Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    YouTube Enhancement Tools                 │
├─────────────────────────────────────────────────────────────┤
│                      Plugin Manager                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Discovery  │  │  Lifecycle  │  │    Hook System      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                        Plugin Types                          │
│  ┌──────────┐ ┌───────────┐ ┌─────┐ ┌────────┐ ┌──────────┐ │
│  │Downloader│ │ Processor │ │  AI │ │ Output │ │   Hook   │ │
│  └──────────┘ └───────────┘ └─────┘ └────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Plugin Lifecycle

1. **Discovery**: Plugin files are found in search locations
2. **Loading**: Plugin classes are imported
3. **Initialization**: `initialize()` is called with configuration
4. **Running**: Plugin responds to hooks and events
5. **Shutdown**: `shutdown()` is called for cleanup

---

## Creating Your First Plugin

### Step 1: Define Plugin Metadata

Every plugin must define these class attributes:

```python
class MyPlugin(BasePlugin):
    name = "my_plugin"           # Unique identifier
    version = "1.0.0"            # Semantic versioning
    description = "What it does" # Brief description
    author = "Your Name"         # Author name
```

### Step 2: Implement Required Methods

```python
def initialize(self, config: Dict[str, Any]) -> bool:
    """Called when plugin is loaded."""
    # Validate and store configuration
    self._config = config
    # Initialize resources
    return True

def shutdown(self) -> bool:
    """Called when plugin is unloaded."""
    # Cleanup resources
    return True
```

### Step 3: Add Custom Functionality

```python
def do_something(self, data):
    """Your custom method."""
    self.logger.info("Processing: %s", data)
    return processed_data
```

### Complete Example

```python
from plugins.base import BasePlugin
from typing import Dict, Any

class HelloPlugin(BasePlugin):
    name = "hello_plugin"
    version = "1.0.0"
    description = "A simple greeting plugin"
    author = "Developer"
    
    def __init__(self):
        super().__init__()
        self._greeting = "Hello"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self._greeting = config.get("greeting", "Hello")
        self.logger.info("HelloPlugin initialized with greeting: %s", self._greeting)
        return True
    
    def shutdown(self) -> bool:
        self.logger.info("Goodbye from HelloPlugin!")
        return True
    
    def greet(self, name: str) -> str:
        return f"{self._greeting}, {name}!"
```

---

## Plugin Types

### 1. DownloaderPlugin

Add support for new video platforms.

```python
from plugins.types import DownloaderPlugin, VideoInfo, DownloadError
from pathlib import Path

class CustomDownloader(DownloaderPlugin):
    name = "custom_downloader"
    version = "1.0.0"
    description = "Download from custom platform"
    author = "Developer"
    
    def supports_url(self, url: str) -> bool:
        return "customsite.com" in url
    
    def extract_info(self, url: str) -> VideoInfo:
        # Extract metadata without downloading
        return VideoInfo(
            url=url,
            title="Video Title",
            duration=300,
        )
    
    def download(self, url: str, output_path: Path, options: Dict = None) -> Path:
        # Download the video
        return output_path
```

### 2. ProcessorPlugin

Apply effects and transformations to videos.

```python
from plugins.types import ProcessorPlugin, ProcessingError
from pathlib import Path

class BlurProcessor(ProcessorPlugin):
    name = "blur_processor"
    version = "1.0.0"
    description = "Apply blur effect"
    author = "Developer"
    
    def process(self, video_path: Path, options: Dict = None) -> Path:
        # Apply blur effect
        output_path = video_path.parent / f"{video_path.stem}_blurred{video_path.suffix}"
        # Processing logic here
        return output_path
```

### 3. AIPlugin

Add AI-powered analysis and enhancement.

```python
from plugins.types import AIPlugin, AnalysisResult, AnalysisError
from pathlib import Path

class SceneDetector(AIPlugin):
    name = "scene_detector"
    version = "1.0.0"
    description = "Detect scene changes using AI"
    author = "Developer"
    
    def analyze(self, video_path: Path, options: Dict = None) -> AnalysisResult:
        # Analyze video for scene changes
        return AnalysisResult(
            success=True,
            findings={"scenes": 42, "transitions": ["cut", "fade"]},
            confidence=0.95,
        )
```

### 4. OutputPlugin

Export content to platforms or storage.

```python
from plugins.types import OutputPlugin, UploadResult, UploadError
from pathlib import Path

class FTPUploader(OutputPlugin):
    name = "ftp_uploader"
    version = "1.0.0"
    description = "Upload via FTP"
    author = "Developer"
    
    def upload(self, content_path: Path, options: Dict = None) -> UploadResult:
        # Upload to FTP server
        return UploadResult(
            success=True,
            destination="ftp://server.com/video.mp4",
            url="http://server.com/video.mp4",
        )
```

### 5. HookPlugin

Register callbacks at specific pipeline points.

```python
from plugins.types import HookPlugin, PluginHook, HookResult
from pathlib import Path

class LogHook(HookPlugin):
    name = "log_hook"
    version = "1.0.0"
    description = "Log all events"
    author = "Developer"
    
    def get_hooks(self) -> Dict[PluginHook, Callable]:
        return {
            PluginHook.BEFORE_DOWNLOAD: self.log_download,
            PluginHook.AFTER_DOWNLOAD: self.log_complete,
            PluginHook.ON_ERROR: self.log_error,
        }
    
    def log_download(self, url: str, **kwargs) -> HookResult:
        self.logger.info("Downloading: %s", url)
        return HookResult.ok()
    
    def log_complete(self, video_path: Path, info: VideoInfo) -> HookResult:
        self.logger.info("Downloaded: %s", video_path)
        return HookResult.ok()
    
    def log_error(self, error: Exception, context: Dict) -> HookResult:
        self.logger.error("Error: %s in context %s", error, context)
        return HookResult.ok()
```

---

## Plugin Hooks

### Available Hook Points

| Hook | When Called | Arguments |
|------|-------------|-----------|
| `BEFORE_DOWNLOAD` | Before video download | `url`, `config` |
| `AFTER_DOWNLOAD` | After download completes | `video_path`, `info` |
| `BEFORE_PROCESS` | Before processing | `video_path`, `config` |
| `AFTER_PROCESS` | After processing | `output_path`, `config` |
| `BEFORE_ANALYSIS` | Before AI analysis | `video_path`, `options` |
| `AFTER_ANALYSIS` | After analysis | `result`, `options` |
| `BEFORE_UPLOAD` | Before platform upload | `platform`, `content_path` |
| `AFTER_UPLOAD` | After upload | `platform`, `result` |
| `ON_STARTUP` | Application startup | - |
| `ON_SHUTDOWN` | Application shutdown | - |
| `ON_ERROR` | When error occurs | `error`, `context` |

### Hook Result Types

```python
# Success with data
return HookResult.ok(data=modified_data)

# Error
return HookResult.error("Something went wrong")

# Skip remaining hooks
return HookResult.skip()
```

### Hook Priority

Lower priority numbers execute first:

```python
def get_hook_priority(self, hook: PluginHook) -> int:
    if hook == PluginHook.BEFORE_DOWNLOAD:
        return 10  # Early execution
    return 100  # Default
```

---

## Plugin Configuration

### Configuration File

Plugins can be configured in `plugins_config.json`:

```json
{
  "my_plugin": {
    "enabled": true,
    "option1": "value1",
    "option2": 42
  },
  "another_plugin": {
    "setting": "custom"
  }
}
```

### Accessing Configuration

```python
def initialize(self, config: Dict[str, Any]) -> bool:
    # Get configuration values with defaults
    self._api_key = config.get("api_key", "")
    self._timeout = config.get("timeout", 30)
    self._enabled = config.get("enabled", True)
    
    # Validate configuration
    if not self._api_key:
        self.logger.error("API key is required")
        return False
    
    return True
```

### Configuration Validation

```python
def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
    errors = []
    
    if not isinstance(config, dict):
        errors.append("Configuration must be a dictionary")
        return False, errors
    
    if "api_key" in config and not isinstance(config["api_key"], str):
        errors.append("api_key must be a string")
    
    if "timeout" in config:
        if not isinstance(config["timeout"], int) or config["timeout"] < 1:
            errors.append("timeout must be a positive integer")
    
    return len(errors) == 0, errors
```

---

## Plugin Discovery

### Search Locations

Plugins are automatically discovered in:

1. `./plugins/` - Local plugins directory
2. `~/.youtube_enhancement_tools/plugins/` - User plugins
3. Site-packages - Installed plugin packages

### Plugin File Structure

```
plugins/
├── my_plugin.py           # Single file plugin
├── another_plugin.py
└── my_package/            # Package plugin
    ├── __init__.py
    ├── plugin.py
    └── utils.py
```

### Plugin Naming

- File names should be lowercase with underscores
- Class names should be PascalCase
- Plugin names should be lowercase with underscores

---

## Testing Plugins

### Unit Testing

```python
import pytest
from my_plugin import MyPlugin

class TestMyPlugin:
    @pytest.fixture
    def plugin(self):
        p = MyPlugin()
        p.initialize({})
        return p
    
    def test_plugin_name(self, plugin):
        assert plugin.name == "my_plugin"
    
    def test_plugin_functionality(self, plugin):
        result = plugin.do_something("input")
        assert result == "expected"
```

### Integration Testing

```python
from plugins.plugin_manager import PluginManager

def test_plugin_integration(temp_dir):
    # Create test plugin
    plugin_file = temp_dir / "test.py"
    plugin_file.write_text("...plugin code...")
    
    # Test with manager
    manager = PluginManager(search_paths=[temp_dir])
    manager.load_plugin(plugin_file)
    manager.initialize_plugin("test_plugin")
    
    # Verify functionality
    assert manager.get_plugin("test_plugin") is not None
```

---

## Publishing Plugins

### Package Structure

```
yet_my_plugin/
├── pyproject.toml
├── README.md
├── yet_my_plugin/
│   ├── __init__.py
│   └── plugin.py
└── tests/
    └── test_plugin.py
```

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "yet-my-plugin"
version = "1.0.0"
description = "My YET plugin"
authors = [{name = "Developer", email = "dev@example.com"}]
dependencies = ["youtube-enhancement-tools>=3.0.0"]

[project.entry-points."yet.plugins"]
my_plugin = "yet_my_plugin.plugin:MyPlugin"
```

### Distribution

1. Build package: `python -m build`
2. Upload to PyPI: `twine upload dist/*`
3. Users install: `pip install yet-my-plugin`

---

## Best Practices

### Code Quality

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for all public methods
- Keep plugins focused and single-purpose

### Error Handling

```python
def process(self, video_path: Path, options: Dict = None) -> Path:
    try:
        # Processing logic
        pass
    except FileNotFoundError:
        raise ProcessingError(f"File not found: {video_path}")
    except Exception as e:
        self.logger.error("Processing failed: %s", e)
        raise ProcessingError(f"Processing failed: {e}")
```

### Logging

```python
# Use the plugin logger
self.logger.debug("Debug information")
self.logger.info("Normal operation")
self.logger.warning("Warning condition")
self.logger.error("Error occurred")
```

### Resource Management

```python
def shutdown(self) -> bool:
    try:
        # Close connections
        if self._connection:
            self._connection.close()
        
        # Save state
        self._save_state()
        
        return True
    except Exception as e:
        self.logger.error("Shutdown failed: %s", e)
        return False
```

### Security

- Never store secrets in code
- Use environment variables for sensitive data
- Validate all user inputs
- Handle errors without exposing internals

---

## Troubleshooting

### Plugin Not Loading

1. Check file location is in search path
2. Verify plugin inherits from correct base class
3. Ensure all required attributes are defined
4. Check for import errors in logs

### Hook Not Executing

1. Verify hook is registered in `get_hooks()`
2. Check plugin is initialized
3. Ensure hook name matches exactly
4. Check plugin is not disabled

### Configuration Not Applied

1. Verify config file is valid JSON
2. Check plugin name matches config key
3. Ensure `initialize()` uses the config
4. Check for validation errors

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `PluginNotFoundError` | Plugin not found | Check search paths |
| `PluginInitializationError` | Init failed | Check config and logs |
| `PluginCompatibilityError` | Version mismatch | Update plugin or YET |

---

## Support

- Documentation: [Link to docs]
- Issues: [Link to issue tracker]
- Discussions: [Link to forum]

---

*Last updated: March 2026*
*Version: 3.3.0*
