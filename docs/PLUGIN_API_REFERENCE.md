# YouTube Enhancement Tools - Plugin API Reference

## Overview

This document provides complete API reference for the YouTube Enhancement Tools Plugin System v3.3.0.

---

## Table of Contents

1. [Base Classes](#base-classes)
2. [Plugin Types](#plugin-types)
3. [Plugin Manager](#plugin-manager)
4. [Data Types](#data-types)
5. [Exceptions](#exceptions)
6. [Hooks Reference](#hooks-reference)

---

## Base Classes

### BasePlugin

Abstract base class for all plugins.

```python
class BasePlugin(ABC):
    """Base class for all plugins."""
    
    # Required class attributes
    name: str = "unnamed_plugin"
    version: str = "0.0.0"
    description: str = "No description provided"
    author: str = "Unknown"
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `state` | `PluginState` | Current plugin state |
| `config` | `Dict[str, Any]` | Plugin configuration |
| `metadata` | `PluginMetadata` | Plugin metadata |
| `logger` | `Logger` | Plugin logger instance |
| `is_initialized` | `bool` | Whether plugin is initialized |
| `is_running` | `bool` | Whether plugin is running |

#### Methods

##### `__init__()`

Initialize the base plugin.

```python
def __init__(self):
    """Initialize the base plugin."""
```

##### `initialize(config)`

Initialize the plugin with configuration.

```python
@abstractmethod
def initialize(self, config: Dict[str, Any]) -> bool:
    """
    Initialize the plugin with the given configuration.
    
    Args:
        config: Configuration dictionary for the plugin
        
    Returns:
        True if initialization succeeded, False otherwise
    """
```

##### `shutdown()`

Shutdown the plugin and cleanup resources.

```python
@abstractmethod
def shutdown(self) -> bool:
    """
    Shutdown the plugin and cleanup resources.
    
    Returns:
        True if shutdown succeeded, False otherwise
    """
```

##### `validate_config(config)`

Validate plugin configuration.

```python
def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate plugin configuration.
    
    Args:
        config: Configuration to validate
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
```

##### `get_capabilities()`

Get plugin capabilities.

```python
def get_capabilities(self) -> Dict[str, Any]:
    """
    Get plugin capabilities.
    
    Returns:
        Dictionary describing plugin capabilities
    """
```

---

### PluginMetadata

Metadata information for a plugin.

```python
@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    email: Optional[str] = None
    url: Optional[str] = None
    license: str = "MIT"
    min_yet_version: str = "3.0.0"
    max_yet_version: str = "4.0.0"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

#### Methods

##### `to_dict()`

Convert metadata to dictionary.

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert metadata to dictionary."""
```

##### `from_dict(data)`

Create metadata from dictionary.

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
    """Create metadata from dictionary."""
```

---

### PluginState

Plugin lifecycle states.

```python
class PluginState(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADING = "unloading"
```

---

## Plugin Types

### PluginType

Enumeration of supported plugin types.

```python
class PluginType(Enum):
    DOWNLOADER = "downloader"
    PROCESSOR = "processor"
    AI = "ai"
    OUTPUT = "output"
    HOOK = "hook"
```

#### Methods

##### `from_string(value)`

Create PluginType from string.

```python
@classmethod
def from_string(cls, value: str) -> "PluginType":
    """Create PluginType from string."""
```

---

### DownloaderPlugin

Plugin for downloading videos from various platforms.

```python
class DownloaderPlugin(BasePlugin):
    """Plugin for downloading videos from various platforms."""
```

#### Abstract Methods

##### `supports_url(url)`

Check if this downloader can handle the given URL.

```python
@abstractmethod
def supports_url(self, url: str) -> bool:
    """
    Check if this downloader can handle the given URL.
    
    Args:
        url: The URL to check
        
    Returns:
        True if this downloader can handle the URL
    """
```

##### `extract_info(url)`

Extract video information from URL.

```python
@abstractmethod
def extract_info(self, url: str) -> "VideoInfo":
    """
    Extract video information from URL without downloading.
    
    Args:
        url: Video URL
        
    Returns:
        VideoInfo object with metadata
    """
```

##### `download(url, output_path, options)`

Download video from URL.

```python
@abstractmethod
def download(
    self,
    url: str,
    output_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Download video from URL to output path.
    
    Args:
        url: Video URL to download
        output_path: Destination path for the video
        options: Download options
        
    Returns:
        Path to downloaded file
    """
```

#### Concrete Methods

##### `get_supported_formats()`

Get list of supported output formats.

```python
def get_supported_formats(self) -> List[str]:
    """Get list of supported output formats."""
```

##### `get_max_quality()`

Get maximum supported quality.

```python
def get_max_quality(self) -> str:
    """Get maximum supported quality."""
```

---

### ProcessorPlugin

Plugin for processing and transforming videos.

```python
class ProcessorPlugin(BasePlugin):
    """Plugin for processing and transforming videos."""
```

#### Abstract Methods

##### `process(video_path, options)`

Process the video file.

```python
@abstractmethod
def process(
    self,
    video_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Process the video file.
    
    Args:
        video_path: Path to input video
        options: Processing options
        
    Returns:
        Path to processed video
    """
```

#### Concrete Methods

##### `supports_format(format)`

Check if processor supports the given format.

```python
def supports_format(self, format: str) -> bool:
    """Check if processor supports the given format."""
```

##### `get_processing_options()`

Get available processing options.

```python
def get_processing_options(self) -> Dict[str, Any]:
    """Get available processing options."""
```

---

### AIPlugin

Plugin for AI-powered analysis and enhancement.

```python
class AIPlugin(BasePlugin):
    """Plugin for AI-powered analysis and enhancement."""
```

#### Abstract Methods

##### `analyze(video_path, options)`

Analyze video content using AI.

```python
@abstractmethod
def analyze(
    self,
    video_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> "AnalysisResult":
    """
    Analyze video content using AI.
    
    Args:
        video_path: Path to video file
        options: Analysis options
        
    Returns:
        AnalysisResult with findings
    """
```

#### Concrete Methods

##### `get_model_info()`

Get information about the AI model used.

```python
def get_model_info(self) -> Dict[str, Any]:
    """Get information about the AI model used."""
```

##### `supports_task(task)`

Check if plugin supports the given AI task.

```python
def supports_task(self, task: str) -> bool:
    """Check if plugin supports the given AI task."""
```

---

### OutputPlugin

Plugin for exporting content to various destinations.

```python
class OutputPlugin(BasePlugin):
    """Plugin for exporting content to various destinations."""
```

#### Abstract Methods

##### `upload(content_path, options)`

Upload/export content to destination.

```python
@abstractmethod
def upload(
    self,
    content_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> "UploadResult":
    """
    Upload/export content to destination.
    
    Args:
        content_path: Path to content file
        options: Upload options
        
    Returns:
        UploadResult with outcome
    """
```

#### Concrete Methods

##### `get_destination_info()`

Get information about the output destination.

```python
def get_destination_info(self) -> Dict[str, Any]:
    """Get information about the output destination."""
```

##### `supports_content_type(content_type)`

Check if destination supports the content type.

```python
def supports_content_type(self, content_type: str) -> bool:
    """Check if destination supports the content type."""
```

---

### HookPlugin

Plugin for registering custom hooks in the pipeline.

```python
class HookPlugin(BasePlugin):
    """Plugin for registering custom hooks in the pipeline."""
```

#### Abstract Methods

##### `get_hooks()`

Get dictionary of hook points and their callbacks.

```python
@abstractmethod
def get_hooks(self) -> Dict[PluginHook, HookCallback]:
    """
    Get dictionary of hook points and their callbacks.
    
    Returns:
        Dictionary mapping PluginHook to callback function
    """
```

#### Concrete Methods

##### `get_hook_priority(hook)`

Get priority for hook execution.

```python
def get_hook_priority(self, hook: PluginHook) -> int:
    """
    Get priority for hook execution (lower = earlier).
    
    Args:
        hook: The hook to get priority for
        
    Returns:
        Priority value (default 100)
    """
```

---

## Plugin Manager

### PluginManager

Plugin discovery and management system.

```python
class PluginManager:
    """Plugin discovery and management system."""
    
    DEFAULT_SEARCH_PATHS = [
        Path("./plugins"),
        Path.home() / ".youtube_enhancement_tools" / "plugins",
    ]
```

#### Constructor

```python
def __init__(
    self,
    search_paths: Optional[List[Union[str, Path]]] = None,
    auto_discover: bool = False,
    config_path: Optional[Path] = None,
):
    """
    Initialize the plugin manager.
    
    Args:
        search_paths: Additional paths to search for plugins
        auto_discover: Whether to discover plugins on init
        config_path: Path to plugin configuration file
    """
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `registry` | `PluginRegistry` | The plugin registry |

#### Discovery Methods

##### `discover()`

Discover plugins in all search locations.

```python
def discover(self) -> List[Path]:
    """
    Discover plugins in all search locations.
    
    Returns:
        List of paths to discovered plugin modules
    """
```

##### `load_plugin(plugin_path)`

Load a plugin from a file path.

```python
def load_plugin(self, plugin_path: Path) -> Optional[PluginInfo]:
    """
    Load a plugin from a file path.
    
    Args:
        plugin_path: Path to the plugin file or package
        
    Returns:
        PluginInfo if loaded successfully, None otherwise
    """
```

##### `load_all()`

Load all discovered plugins.

```python
def load_all(self) -> List[PluginInfo]:
    """
    Load all discovered plugins.
    
    Returns:
        List of successfully loaded plugin info
    """
```

#### Lifecycle Methods

##### `initialize_plugin(plugin_name, config)`

Initialize a specific plugin.

```python
def initialize_plugin(
    self,
    plugin_name: str,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Initialize a specific plugin.
    
    Args:
        plugin_name: Name of the plugin to initialize
        config: Optional configuration override
        
    Returns:
        True if initialization succeeded
    """
```

##### `initialize_all()`

Initialize all loaded plugins.

```python
def initialize_all(self) -> Dict[str, bool]:
    """
    Initialize all loaded plugins.
    
    Returns:
        Dictionary mapping plugin names to success status
    """
```

##### `shutdown_plugin(plugin_name)`

Shutdown a specific plugin.

```python
def shutdown_plugin(self, plugin_name: str) -> bool:
    """
    Shutdown a specific plugin.
    
    Args:
        plugin_name: Name of the plugin to shutdown
        
    Returns:
        True if shutdown succeeded
    """
```

##### `shutdown()`

Shutdown all plugins.

```python
def shutdown(self) -> Dict[str, bool]:
    """
    Shutdown all plugins.
    
    Returns:
        Dictionary mapping plugin names to success status
    """
```

#### Hook Methods

##### `execute_hook(hook, *args, **kwargs)`

Execute all registered callbacks for a hook.

```python
def execute_hook(
    self,
    hook: PluginHook,
    *args,
    **kwargs
) -> List[HookResult]:
    """
    Execute all registered callbacks for a hook.
    
    Args:
        hook: The hook to execute
        *args: Positional arguments to pass to callbacks
        **kwargs: Keyword arguments to pass to callbacks
        
    Returns:
        List of HookResult from each callback
    """
```

##### `execute_hook_with_data(hook, data, **kwargs)`

Execute hook and return modified data.

```python
def execute_hook_with_data(
    self,
    hook: PluginHook,
    data: Any,
    **kwargs
) -> Any:
    """
    Execute hook and return modified data.
    
    Args:
        hook: The hook to execute
        data: Data to pass through hooks
        **kwargs: Additional arguments for callbacks
        
    Returns:
        Final modified data
    """
```

#### Configuration Methods

##### `get_plugin_config(plugin_name)`

Get configuration for a specific plugin.

```python
def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
    """Get configuration for a specific plugin."""
```

##### `set_plugin_config(plugin_name, config)`

Set configuration for a specific plugin.

```python
def set_plugin_config(
    self,
    plugin_name: str,
    config: Dict[str, Any]
) -> None:
    """Set configuration for a specific plugin."""
```

#### Management Methods

##### `get_plugin(name)`

Get a plugin instance by name.

```python
def get_plugin(self, name: str) -> Optional[BasePlugin]:
    """Get a plugin instance by name."""
```

##### `get_all_plugins()`

Get information about all plugins.

```python
def get_all_plugins(self) -> List[Dict[str, Any]]:
    """Get information about all plugins."""
```

##### `get_stats()`

Get plugin system statistics.

```python
def get_stats(self) -> Dict[str, Any]:
    """Get plugin system statistics."""
```

##### `enable_plugin(plugin_name)`

Enable a disabled plugin.

```python
def enable_plugin(self, plugin_name: str) -> bool:
    """Enable a disabled plugin."""
```

##### `disable_plugin(plugin_name)`

Disable a plugin.

```python
def disable_plugin(self, plugin_name: str) -> bool:
    """Disable a plugin."""
```

##### `reload_plugin(plugin_name)`

Reload a plugin.

```python
def reload_plugin(self, plugin_name: str) -> bool:
    """Reload a plugin."""
```

##### `check_compatibility(plugin_info)`

Check plugin compatibility.

```python
def check_compatibility(
    self,
    plugin_info: PluginInfo
) -> tuple[bool, List[str]]:
    """
    Check if a plugin is compatible with the current application version.
    
    Args:
        plugin_info: Plugin info to check
        
    Returns:
        Tuple of (is_compatible, list of issues)
    """
```

---

### PluginRegistry

Central registry for all plugins and hooks.

```python
class PluginRegistry:
    """Central registry for all plugins and hooks."""
```

#### Methods

##### `register_plugin(info)`

Register a plugin.

```python
def register_plugin(self, info: PluginInfo) -> None:
    """Register a plugin."""
```

##### `unregister_plugin(name)`

Unregister a plugin.

```python
def unregister_plugin(self, name: str) -> Optional[PluginInfo]:
    """Unregister a plugin."""
```

##### `get_plugin(name)`

Get plugin info by name.

```python
def get_plugin(self, name: str) -> Optional[PluginInfo]:
    """Get plugin info by name."""
```

##### `get_all_plugins()`

Get all registered plugins.

```python
def get_all_plugins(self) -> List[PluginInfo]:
    """Get all registered plugins."""
```

##### `get_plugins_by_type(plugin_type)`

Get plugins of a specific type.

```python
def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
    """Get plugins of a specific type."""
```

##### `register_hook(registration)`

Register a hook callback.

```python
def register_hook(self, registration: HookRegistration) -> None:
    """Register a hook callback."""
```

##### `get_hooks(hook)`

Get all registrations for a hook.

```python
def get_hooks(self, hook: PluginHook) -> List[HookRegistration]:
    """Get all registrations for a hook."""
```

##### `disable_plugin(name)`

Mark a plugin as disabled.

```python
def disable_plugin(self, name: str) -> None:
    """Mark a plugin as disabled."""
```

##### `is_plugin_disabled(name)`

Check if a plugin is disabled.

```python
def is_plugin_disabled(self, name: str) -> bool:
    """Check if a plugin is disabled."""
```

##### `get_stats()`

Get registry statistics.

```python
def get_stats(self) -> Dict[str, Any]:
    """Get registry statistics."""
```

---

## Data Types

### VideoInfo

Information about a video.

```python
@dataclass
class VideoInfo:
    url: str
    title: str
    duration: int  # seconds
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    formats: List[Dict[str, Any]] = None
```

#### Methods

##### `to_dict()`

Convert to dictionary.

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
```

---

### AnalysisResult

Result from AI analysis.

```python
@dataclass
class AnalysisResult:
    success: bool
    findings: Dict[str, Any]
    confidence: float = 1.0
    processing_time: float = 0.0
    model_version: Optional[str] = None
```

#### Methods

##### `to_dict()`

Convert to dictionary.

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
```

---

### UploadResult

Result from upload operation.

```python
@dataclass
class UploadResult:
    success: bool
    destination: str
    url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
```

#### Methods

##### `to_dict()`

Convert to dictionary.

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
```

---

### HookResult

Result returned by a hook execution.

```python
@dataclass
class HookResult:
    success: bool = True
    data: Optional[Any] = None
    errors: List[str] = None
    skip_remaining: bool = False
```

#### Class Methods

##### `ok(data)`

Create successful result.

```python
@classmethod
def ok(cls, data: Any = None) -> "HookResult":
    """Create successful result."""
```

##### `error(message, skip_remaining)`

Create error result.

```python
@classmethod
def error(cls, message: str, skip_remaining: bool = False) -> "HookResult":
    """Create error result."""
```

##### `skip()`

Create result that skips remaining hooks.

```python
@classmethod
def skip(cls) -> "HookResult":
    """Create result that skips remaining hooks."""
```

---

### PluginInfo

Information about a loaded plugin.

```python
@dataclass
class PluginInfo:
    name: str
    module_path: Path
    plugin_class: Type[BasePlugin]
    instance: Optional[BasePlugin] = None
    plugin_type: Optional[PluginType] = None
    state: PluginState = PluginState.UNLOADED
    config: Dict[str, Any] = field(default_factory=dict)
    load_time: Optional[datetime] = None
    error: Optional[str] = None
```

#### Methods

##### `to_dict()`

Convert to dictionary.

```python
def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
```

---

### HookRegistration

Registration information for a hook.

```python
@dataclass
class HookRegistration:
    plugin_name: str
    hook: PluginHook
    callback: HookCallback
    priority: int = 100
```

---

## Exceptions

### PluginError

Base exception for plugin-related errors.

```python
class PluginError(Exception):
    """Base exception for plugin-related errors."""
```

### PluginInitializationError

Raised when plugin initialization fails.

```python
class PluginInitializationError(PluginError):
    """Raised when plugin initialization fails."""
```

### PluginNotFoundError

Raised when a plugin cannot be found.

```python
class PluginNotFoundError(PluginError):
    """Raised when a plugin cannot be found."""
```

### PluginCompatibilityError

Raised when plugin is incompatible with the host application.

```python
class PluginCompatibilityError(PluginError):
    """Raised when plugin is incompatible with the host application."""
```

### PluginDependencyError

Raised when plugin dependencies are not satisfied.

```python
class PluginDependencyError(PluginError):
    """Raised when plugin dependencies are not satisfied."""
```

### PluginHookError

Raised when a plugin hook fails.

```python
class PluginHookError(PluginError):
    """Raised when a plugin hook fails."""
```

### DownloadError

Raised when download fails.

```python
class DownloadError(Exception):
    """Raised when download fails."""
```

### ProcessingError

Raised when processing fails.

```python
class ProcessingError(Exception):
    """Raised when processing fails."""
```

### AnalysisError

Raised when AI analysis fails.

```python
class AnalysisError(Exception):
    """Raised when AI analysis fails."""
```

### UploadError

Raised when upload fails.

```python
class UploadError(Exception):
    """Raised when upload fails."""
```

---

## Hooks Reference

### PluginHook Enum

All available hook points:

```python
class PluginHook(Enum):
    # Download hooks
    BEFORE_DOWNLOAD = "before_download"
    AFTER_DOWNLOAD = "after_download"
    
    # Processing hooks
    BEFORE_PROCESS = "before_process"
    AFTER_PROCESS = "after_process"
    
    # AI/Analysis hooks
    BEFORE_ANALYSIS = "before_analysis"
    AFTER_ANALYSIS = "after_analysis"
    
    # Output hooks
    BEFORE_EXPORT = "before_export"
    AFTER_EXPORT = "after_export"
    
    # Upload hooks
    BEFORE_UPLOAD = "before_upload"
    AFTER_UPLOAD = "after_upload"
    
    # General hooks
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"
    ON_ERROR = "on_error"
```

### Hook Callbacks Signature

```python
# Type alias for hook callbacks
HookCallback = Callable[..., HookResult]
```

### Hook Arguments Reference

| Hook | Arguments | Return |
|------|-----------|--------|
| `BEFORE_DOWNLOAD` | `url: str`, `config: Dict` | `HookResult` |
| `AFTER_DOWNLOAD` | `video_path: Path`, `info: VideoInfo` | `HookResult` |
| `BEFORE_PROCESS` | `video_path: Path`, `config: Dict` | `HookResult` |
| `AFTER_PROCESS` | `output_path: Path`, `config: Dict` | `HookResult` |
| `BEFORE_ANALYSIS` | `video_path: Path`, `options: Dict` | `HookResult` |
| `AFTER_ANALYSIS` | `result: AnalysisResult`, `options: Dict` | `HookResult` |
| `BEFORE_UPLOAD` | `platform: str`, `content_path: Path` | `HookResult` |
| `AFTER_UPLOAD` | `platform: str`, `result: UploadResult` | `HookResult` |
| `ON_ERROR` | `error: Exception`, `context: Dict` | `HookResult` |

---

## Module-Level Functions

Convenience functions for quick access:

```python
def get_plugin_manager() -> PluginManager:
    """Get the default plugin manager instance."""

def discover_plugins() -> List[Path]:
    """Discover plugins using the default manager."""

def load_plugins() -> List[PluginInfo]:
    """Load all plugins using the default manager."""

def execute_hook(hook: PluginHook, *args, **kwargs) -> List[HookResult]:
    """Execute a hook using the default manager."""
```

---

*API Version: 3.3.0*
*Last Updated: March 2026*
