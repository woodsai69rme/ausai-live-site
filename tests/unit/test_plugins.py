"""
Unit Tests for YouTube Enhancement Tools Plugin System

This module contains comprehensive unit tests for the plugin system,
covering plugin discovery, lifecycle management, hooks, and all plugin types.

Test Coverage:
- Base plugin classes
- Plugin types (Downloader, Processor, AI, Output, Hook)
- Plugin manager (discovery, loading, initialization)
- Hook execution system
- Plugin registry
- Example plugins
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import plugin system modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from plugins.base import (
    BasePlugin,
    PluginMetadata,
    PluginState,
    PluginError,
    PluginInitializationError,
    PluginNotFoundError,
    PluginCompatibilityError,
)
from plugins.types import (
    PluginType,
    PluginHook,
    HookResult,
    DownloaderPlugin,
    ProcessorPlugin,
    AIPlugin,
    OutputPlugin,
    HookPlugin,
    VideoInfo,
    AnalysisResult,
    UploadResult,
    DownloadError,
    ProcessingError,
    AnalysisError,
    UploadError,
)
from plugins.plugin_manager import (
    PluginManager,
    PluginRegistry,
    PluginInfo,
    HookRegistration,
    YET_VERSION,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def plugin_config():
    """Sample plugin configuration."""
    return {
        "enabled": True,
        "debug": False,
        "max_retries": 3,
    }


@pytest.fixture
def sample_video_info():
    """Sample video info for testing."""
    return VideoInfo(
        url="https://example.com/video/123",
        title="Test Video",
        duration=300,
        thumbnail="https://example.com/thumb.jpg",
        description="A test video",
        uploader="Test User",
        upload_date="2024-01-01",
        view_count=1000,
        like_count=100,
    )


# =============================================================================
# Base Plugin Tests
# =============================================================================

class TestPluginMetadata:
    """Tests for PluginMetadata class."""
    
    def test_create_metadata(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin description",
            author="Test Author",
        )
        
        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin description"
        assert metadata.author == "Test Author"
        assert metadata.license == "MIT"
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            author="Author",
            email="test@example.com",
            tags=["test", "demo"],
        )
        
        data = metadata.to_dict()
        
        assert data["name"] == "test_plugin"
        assert data["version"] == "1.0.0"
        assert data["email"] == "test@example.com"
        assert data["tags"] == ["test", "demo"]
    
    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "name": "test_plugin",
            "version": "2.0.0",
            "description": "Updated test",
            "author": "New Author",
        }
        
        metadata = PluginMetadata.from_dict(data)
        
        assert metadata.name == "test_plugin"
        assert metadata.version == "2.0.0"
        assert metadata.description == "Updated test"


class TestBasePlugin:
    """Tests for BasePlugin class."""
    
    def test_create_concrete_plugin(self):
        """Test creating a concrete plugin implementation."""
        class TestPlugin(BasePlugin):
            name = "test_plugin"
            version = "1.0.0"
            description = "Test plugin"
            author = "Tester"
            
            def initialize(self, config):
                return super().initialize(config)
            
            def shutdown(self):
                return super().shutdown()
        
        plugin = TestPlugin()
        
        assert plugin.name == "test_plugin"
        assert plugin.version == "1.0.0"
        assert plugin.state == PluginState.UNLOADED
    
    def test_plugin_initialization(self):
        """Test plugin initialization lifecycle."""
        class TestPlugin(BasePlugin):
            name = "test"
            version = "1.0.0"
            description = "Test"
            author = "Test"
            
            def initialize(self, config):
                return super().initialize(config)
            
            def shutdown(self):
                return super().shutdown()
        
        plugin = TestPlugin()
        config = {"key": "value"}
        
        assert plugin.state == PluginState.UNLOADED
        
        result = plugin.initialize(config)
        
        assert result is True
        assert plugin.state == PluginState.INITIALIZED
        assert plugin.config == config
    
    def test_plugin_shutdown(self):
        """Test plugin shutdown."""
        class TestPlugin(BasePlugin):
            name = "test"
            version = "1.0.0"
            description = "Test"
            author = "Test"
            
            def initialize(self, config):
                return super().initialize(config)
            
            def shutdown(self):
                return super().shutdown()
        
        plugin = TestPlugin()
        plugin.initialize({})
        
        assert plugin.state == PluginState.INITIALIZED
        
        result = plugin.shutdown()
        
        assert result is True
        assert plugin.state == PluginState.UNLOADED
    
    def test_plugin_validate_config(self):
        """Test configuration validation."""
        class TestPlugin(BasePlugin):
            name = "test"
            version = "1.0.0"
            description = "Test"
            author = "Test"
            
            def initialize(self, config):
                return True
            
            def shutdown(self):
                return True
        
        plugin = TestPlugin()
        
        # Valid config
        is_valid, errors = plugin.validate_config({"key": "value"})
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid config (not a dict)
        is_valid, errors = plugin.validate_config("not a dict")
        assert is_valid is False
        assert len(errors) > 0
    
    def test_plugin_state_transitions(self):
        """Test plugin state transitions."""
        class TestPlugin(BasePlugin):
            name = "test"
            version = "1.0.0"
            description = "Test"
            author = "Test"
            
            def initialize(self, config):
                return super().initialize(config)
            
            def shutdown(self):
                return super().shutdown()
        
        plugin = TestPlugin()
        
        assert plugin.state == PluginState.UNLOADED
        
        plugin.initialize({})
        assert plugin.state == PluginState.INITIALIZED
        
        plugin.shutdown()
        assert plugin.state == PluginState.UNLOADED
    
    def test_plugin_is_initialized(self):
        """Test is_initialized property."""
        class TestPlugin(BasePlugin):
            name = "test"
            version = "1.0.0"
            description = "Test"
            author = "Test"
            
            def initialize(self, config):
                return super().initialize(config)
            
            def shutdown(self):
                return True
        
        plugin = TestPlugin()
        
        assert plugin.is_initialized is False
        
        plugin.initialize({})
        assert plugin.is_initialized is True


# =============================================================================
# Plugin Types Tests
# =============================================================================

class TestPluginType:
    """Tests for PluginType enum."""
    
    def test_plugin_type_values(self):
        """Test plugin type enum values."""
        assert PluginType.DOWNLOADER.value == "downloader"
        assert PluginType.PROCESSOR.value == "processor"
        assert PluginType.AI.value == "ai"
        assert PluginType.OUTPUT.value == "output"
        assert PluginType.HOOK.value == "hook"
    
    def test_plugin_type_from_string(self):
        """Test creating PluginType from string."""
        assert PluginType.from_string("downloader") == PluginType.DOWNLOADER
        assert PluginType.from_string("PROCESSOR") == PluginType.PROCESSOR
        assert PluginType.from_string("ai") == PluginType.AI
        
        with pytest.raises(ValueError):
            PluginType.from_string("invalid")


class TestPluginHook:
    """Tests for PluginHook enum."""
    
    def test_hook_descriptions(self):
        """Test hook descriptions."""
        assert "download" in PluginHook.BEFORE_DOWNLOAD.description.lower()
        assert "process" in PluginHook.BEFORE_PROCESS.description.lower()
        assert "upload" in PluginHook.BEFORE_UPLOAD.description.lower()
    
    def test_all_hooks_defined(self):
        """Test that all expected hooks are defined."""
        expected_hooks = [
            "before_download",
            "after_download",
            "before_process",
            "after_process",
            "before_upload",
            "after_upload",
            "on_startup",
            "on_shutdown",
            "on_error",
        ]
        
        for hook_name in expected_hooks:
            assert hasattr(PluginHook, hook_name.upper())


class TestHookResult:
    """Tests for HookResult class."""
    
    def test_create_success_result(self):
        """Test creating successful hook result."""
        result = HookResult.ok(data={"key": "value"})
        
        assert result.success is True
        assert result.data == {"key": "value"}
        assert len(result.errors) == 0
    
    def test_create_error_result(self):
        """Test creating error hook result."""
        result = HookResult.error("Something went wrong")
        
        assert result.success is False
        assert "Something went wrong" in result.errors
        assert result.skip_remaining is False
    
    def test_create_skip_result(self):
        """Test creating skip result."""
        result = HookResult.skip()
        
        assert result.success is True
        assert result.skip_remaining is True


class TestVideoInfo:
    """Tests for VideoInfo dataclass."""
    
    def test_create_video_info(self):
        """Test creating VideoInfo."""
        info = VideoInfo(
            url="https://example.com/video",
            title="Test Video",
            duration=120,
        )
        
        assert info.url == "https://example.com/video"
        assert info.title == "Test Video"
        assert info.duration == 120
    
    def test_video_info_to_dict(self):
        """Test converting VideoInfo to dictionary."""
        info = VideoInfo(
            url="https://example.com/video",
            title="Test",
            duration=60,
            thumbnail="thumb.jpg",
        )
        
        data = info.to_dict()
        
        assert data["url"] == "https://example.com/video"
        assert data["thumbnail"] == "thumb.jpg"


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""
    
    def test_create_analysis_result(self):
        """Test creating AnalysisResult."""
        result = AnalysisResult(
            success=True,
            findings={"quality": "high"},
            confidence=0.95,
        )
        
        assert result.success is True
        assert result.findings == {"quality": "high"}
        assert result.confidence == 0.95


class TestUploadResult:
    """Tests for UploadResult dataclass."""
    
    def test_create_upload_result(self):
        """Test creating UploadResult."""
        result = UploadResult(
            success=True,
            destination="youtube",
            url="https://youtube.com/watch?v=123",
        )
        
        assert result.success is True
        assert result.destination == "youtube"
        assert "youtube.com" in result.url


# =============================================================================
# Plugin Manager Tests
# =============================================================================

class TestPluginRegistry:
    """Tests for PluginRegistry class."""
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        
        info = PluginInfo(
            name="test_plugin",
            module_path=Path("/test/plugin.py"),
            plugin_class=BasePlugin,
        )
        
        registry.register_plugin(info)
        
        assert registry.get_plugin("test_plugin") == info
        assert len(registry.get_all_plugins()) == 1
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        
        info = PluginInfo(
            name="test_plugin",
            module_path=Path("/test/plugin.py"),
            plugin_class=BasePlugin,
        )
        
        registry.register_plugin(info)
        result = registry.unregister_plugin("test_plugin")
        
        assert result == info
        assert registry.get_plugin("test_plugin") is None
    
    def test_get_plugins_by_type(self):
        """Test getting plugins by type."""
        registry = PluginRegistry()
        
        info1 = PluginInfo(
            name="downloader_plugin",
            module_path=Path("/test/dl.py"),
            plugin_class=BasePlugin,
            plugin_type=PluginType.DOWNLOADER,
        )
        
        info2 = PluginInfo(
            name="processor_plugin",
            module_path=Path("/test/proc.py"),
            plugin_class=BasePlugin,
            plugin_type=PluginType.PROCESSOR,
        )
        
        registry.register_plugin(info1)
        registry.register_plugin(info2)
        
        downloaders = registry.get_plugins_by_type(PluginType.DOWNLOADER)
        assert len(downloaders) == 1
        assert downloaders[0].name == "downloader_plugin"
    
    def test_register_hook(self):
        """Test registering a hook."""
        registry = PluginRegistry()
        
        callback = Mock()
        registration = HookRegistration(
            plugin_name="test_plugin",
            hook=PluginHook.BEFORE_DOWNLOAD,
            callback=callback,
            priority=50,
        )
        
        registry.register_hook(registration)
        
        hooks = registry.get_hooks(PluginHook.BEFORE_DOWNLOAD)
        assert len(hooks) == 1
        assert hooks[0].plugin_name == "test_plugin"
    
    def test_disable_plugin(self):
        """Test disabling a plugin."""
        registry = PluginRegistry()
        
        info = PluginInfo(
            name="test_plugin",
            module_path=Path("/test/plugin.py"),
            plugin_class=BasePlugin,
        )
        
        registry.register_plugin(info)
        registry.disable_plugin("test_plugin")
        
        assert registry.is_plugin_disabled("test_plugin") is True
    
    def test_get_stats(self):
        """Test getting registry statistics."""
        registry = PluginRegistry()
        
        info = PluginInfo(
            name="test_plugin",
            module_path=Path("/test/plugin.py"),
            plugin_class=BasePlugin,
            plugin_type=PluginType.DOWNLOADER,
        )
        
        registry.register_plugin(info)
        stats = registry.get_stats()
        
        assert stats["total_plugins"] == 1
        assert stats["plugins_by_type"]["downloader"] == 1


class TestPluginManager:
    """Tests for PluginManager class."""
    
    def test_create_manager(self):
        """Test creating a PluginManager."""
        manager = PluginManager()
        
        assert manager is not None
        assert len(manager._search_paths) > 0
    
    def test_manager_with_custom_paths(self):
        """Test creating manager with custom search paths."""
        custom_paths = ["/custom/path1", "/custom/path2"]
        manager = PluginManager(search_paths=custom_paths)
        
        assert len(manager._search_paths) >= 2
    
    def test_manager_config_loading(self, temp_dir):
        """Test loading plugin configuration."""
        config_file = temp_dir / "plugins_config.json"
        config = {
            "test_plugin": {"enabled": True, "option": "value"},
        }
        config_file.write_text(json.dumps(config))
        
        manager = PluginManager(config_path=config_file)
        
        plugin_config = manager.get_plugin_config("test_plugin")
        assert plugin_config.get("enabled") is True
        assert plugin_config.get("option") == "value"
    
    def test_manager_config_saving(self, temp_dir):
        """Test saving plugin configuration."""
        config_file = temp_dir / "plugins_config.json"
        
        manager = PluginManager(config_path=config_file)
        manager.set_plugin_config("new_plugin", {"key": "value"})
        
        assert config_file.exists()
        saved_config = json.loads(config_file.read_text())
        assert saved_config.get("new_plugin") == {"key": "value"}
    
    def test_discover_empty_directory(self, temp_dir):
        """Test discovery in empty directory."""
        manager = PluginManager(search_paths=[temp_dir])
        
        discovered = manager.discover()
        
        assert len(discovered) == 0
    
    def test_discover_plugin_files(self, temp_dir):
        """Test discovering plugin files."""
        # Create a plugin file
        plugin_file = temp_dir / "test_plugin.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class TestPlugin(BasePlugin):
    name = "test_plugin"
    version = "1.0.0"
    description = "Test plugin"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        discovered = manager.discover()
        
        assert len(discovered) > 0
    
    def test_load_plugin(self, temp_dir):
        """Test loading a plugin."""
        plugin_file = temp_dir / "load_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class LoadTestPlugin(BasePlugin):
    name = "load_test_plugin"
    version = "1.0.0"
    description = "Load test plugin"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        info = manager.load_plugin(plugin_file)
        
        assert info is not None
        assert info.name == "load_test_plugin"
    
    def test_initialize_plugin(self, temp_dir):
        """Test initializing a loaded plugin."""
        plugin_file = temp_dir / "init_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class InitTestPlugin(BasePlugin):
    name = "init_test_plugin"
    version = "1.0.0"
    description = "Init test"
    author = "Tester"
    
    def initialize(self, config):
        return super().initialize(config)
    
    def shutdown(self):
        return True
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        
        result = manager.initialize_plugin("init_test_plugin", {"test": True})
        
        assert result is True
    
    def test_execute_hook(self, temp_dir):
        """Test executing hooks."""
        plugin_file = temp_dir / "hook_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin
from plugins.types import HookPlugin, PluginHook, HookResult

class HookTestPlugin(HookPlugin):
    name = "hook_test_plugin"
    version = "1.0.0"
    description = "Hook test"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
    
    def get_hooks(self):
        return {
            PluginHook.BEFORE_DOWNLOAD: self.before_download,
        }
    
    def before_download(self, url, config):
        return HookResult.ok(data={"modified": url})
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        manager.initialize_plugin("hook_test_plugin")
        
        results = manager.execute_hook(
            PluginHook.BEFORE_DOWNLOAD,
            url="https://example.com",
            config={},
        )
        
        assert len(results) > 0
    
    def test_shutdown_plugin(self, temp_dir):
        """Test shutting down a plugin."""
        plugin_file = temp_dir / "shutdown_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class ShutdownTestPlugin(BasePlugin):
    name = "shutdown_test_plugin"
    version = "1.0.0"
    description = "Shutdown test"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        manager.initialize_plugin("shutdown_test_plugin")
        
        result = manager.shutdown_plugin("shutdown_test_plugin")
        
        assert result is True
    
    def test_manager_get_stats(self):
        """Test getting manager statistics."""
        manager = PluginManager()
        stats = manager.get_stats()
        
        assert "total_plugins" in stats
        assert "loaded_plugins" in stats
        assert "registered_hooks" in stats
    
    def test_enable_disable_plugin(self, temp_dir):
        """Test enabling and disabling plugins."""
        plugin_file = temp_dir / "enable_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class EnableTestPlugin(BasePlugin):
    name = "enable_test_plugin"
    version = "1.0.0"
    description = "Enable test"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        
        # Disable
        result = manager.disable_plugin("enable_test_plugin")
        assert result is True
        assert manager.registry.is_plugin_disabled("enable_test_plugin")
        
        # Enable
        result = manager.enable_plugin("enable_test_plugin")
        assert result is True


# =============================================================================
# Example Plugin Tests
# =============================================================================

class TestExamplePlugins:
    """Tests for example plugins."""
    
    def test_vimeo_downloader_creation(self):
        """Test creating Vimeo downloader."""
        from plugins.examples.vimeo_downloader import VimeoDownloader
        
        plugin = VimeoDownloader()
        
        assert plugin.name == "vimeo_downloader"
        assert plugin.version == "1.0.0"
    
    def test_vimeo_url_support(self):
        """Test Vimeo URL detection."""
        from plugins.examples.vimeo_downloader import VimeoDownloader
        
        plugin = VimeoDownloader()
        
        assert plugin.supports_url("https://vimeo.com/123456789") is True
        assert plugin.supports_url("https://player.vimeo.com/video/123456") is True
        assert plugin.supports_url("https://youtube.com/watch?v=abc") is False
    
    def test_twitch_downloader_creation(self):
        """Test creating Twitch downloader."""
        from plugins.examples.twitch_downloader import TwitchDownloader
        
        plugin = TwitchDownloader()
        
        assert plugin.name == "twitch_downloader"
        assert plugin.version == "1.0.0"
    
    def test_twitch_url_support(self):
        """Test Twitch URL detection."""
        from plugins.examples.twitch_downloader import TwitchDownloader
        
        plugin = TwitchDownloader()
        
        assert plugin.supports_url("https://www.twitch.tv/videos/123456") is True
        assert plugin.supports_url("https://www.twitch.tv/channel/clip/abc123") is True
        assert plugin.supports_url("https://youtube.com") is False
    
    def test_silence_remover_creation(self):
        """Test creating silence remover."""
        from plugins.examples.silence_remover import SilenceRemoverProcessor
        
        plugin = SilenceRemoverProcessor()
        
        assert plugin.name == "silence_remover"
        assert plugin.version == "1.0.0"
    
    def test_watermark_processor_creation(self):
        """Test creating watermark processor."""
        from plugins.examples.watermark_adder import WatermarkProcessor
        
        plugin = WatermarkProcessor()
        
        assert plugin.name == "watermark_processor"
        assert plugin.version == "1.0.0"
    
    def test_discord_notifier_creation(self):
        """Test creating Discord notifier."""
        from plugins.examples.discord_notifier import DiscordNotifierHook
        
        plugin = DiscordNotifierHook()
        
        assert plugin.name == "discord_notifier"
        assert plugin.version == "1.0.0"
    
    def test_discord_notifier_hooks(self):
        """Test Discord notifier hook registration."""
        from plugins.examples.discord_notifier import DiscordNotifierHook
        
        plugin = DiscordNotifierHook()
        plugin.initialize({"webhook_url": "https://discord.com/api/webhooks/test"})
        
        hooks = plugin.get_hooks()
        
        assert len(hooks) > 0
        assert PluginHook.AFTER_DOWNLOAD in hooks
    
    def test_quality_enhancer_creation(self):
        """Test creating quality enhancer."""
        from plugins.examples.quality_enhancer import QualityEnhancerAI
        
        plugin = QualityEnhancerAI()
        
        assert plugin.name == "quality_enhancer"
        assert plugin.version == "1.0.0"
    
    def test_cloud_exporter_creation(self):
        """Test creating cloud exporter."""
        from plugins.examples.cloud_exporter import CloudExporter
        
        plugin = CloudExporter()
        
        assert plugin.name == "cloud_exporter"
        assert plugin.version == "1.0.0"


# =============================================================================
# Integration Tests
# =============================================================================

class TestPluginIntegration:
    """Integration tests for the plugin system."""
    
    def test_full_plugin_lifecycle(self, temp_dir):
        """Test complete plugin lifecycle."""
        # Create plugin file
        plugin_file = temp_dir / "lifecycle_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class LifecycleTestPlugin(BasePlugin):
    name = "lifecycle_test"
    version = "1.0.0"
    description = "Lifecycle test"
    author = "Tester"
    
    def initialize(self, config):
        return super().initialize(config)
    
    def shutdown(self):
        return super().shutdown()
""")
        
        # Create manager and run lifecycle
        manager = PluginManager(search_paths=[temp_dir])
        
        # Discover
        discovered = manager.discover()
        assert len(discovered) > 0
        
        # Load
        info = manager.load_plugin(plugin_file)
        assert info is not None
        
        # Initialize
        result = manager.initialize_plugin("lifecycle_test", {})
        assert result is True
        
        # Shutdown
        result = manager.shutdown_plugin("lifecycle_test")
        assert result is True
    
    def test_hook_chain_execution(self, temp_dir):
        """Test executing multiple hooks in chain."""
        # Create hook plugin
        plugin_file = temp_dir / "chain_hook.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin
from plugins.types import HookPlugin, PluginHook, HookResult

class ChainHookPlugin(HookPlugin):
    name = "chain_hook"
    version = "1.0.0"
    description = "Chain hook test"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
    
    def get_hooks(self):
        return {
            PluginHook.BEFORE_DOWNLOAD: self.modify_url,
        }
    
    def modify_url(self, url, **kwargs):
        return HookResult.ok(data=url + "?modified=true")
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        manager.initialize_plugin("chain_hook")
        
        # Execute hook with data modification
        result = manager.execute_hook_with_data(
            PluginHook.BEFORE_DOWNLOAD,
            data="https://example.com",
        )
        
        assert "modified=true" in result
    
    def test_plugin_error_handling(self, temp_dir):
        """Test plugin error handling."""
        plugin_file = temp_dir / "error_test.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin

class ErrorTestPlugin(BasePlugin):
    name = "error_test"
    version = "1.0.0"
    description = "Error test"
    author = "Tester"
    
    def initialize(self, config):
        raise ValueError("Intentional error")
    
    def shutdown(self):
        return True
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        
        result = manager.initialize_plugin("error_test", {})
        
        assert result is False
        
        # Check plugin state is error
        info = manager.registry.get_plugin("error_test")
        assert info.state == PluginState.ERROR


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_plugin_with_no_name(self):
        """Test plugin without proper name."""
        class NoNamePlugin(BasePlugin):
            version = "1.0.0"
            description = "No name"
            author = "Test"
            
            def initialize(self, config):
                return True
            
            def shutdown(self):
                return True
        
        plugin = NoNamePlugin()
        assert plugin.name == "unnamed_plugin"  # Default value
    
    def test_plugin_config_none(self):
        """Test plugin with None config."""
        class TestPlugin(BasePlugin):
            name = "test"
            version = "1.0.0"
            description = "Test"
            author = "Test"
            
            def initialize(self, config):
                return True
            
            def shutdown(self):
                return True
        
        plugin = TestPlugin()
        is_valid, errors = plugin.validate_config(None)
        
        assert is_valid is False
    
    def test_manager_nonexistent_plugin(self):
        """Test manager operations on nonexistent plugin."""
        manager = PluginManager()
        
        result = manager.initialize_plugin("nonexistent_plugin", {})
        assert result is False
        
        result = manager.shutdown_plugin("nonexistent_plugin")
        assert result is False
        
        result = manager.get_plugin("nonexistent_plugin")
        assert result is None
    
    def test_hook_with_exception(self, temp_dir):
        """Test hook execution when callback raises exception."""
        plugin_file = temp_dir / "exception_hook.py"
        plugin_file.write_text("""
from plugins.base import BasePlugin
from plugins.types import HookPlugin, PluginHook, HookResult

class ExceptionHookPlugin(HookPlugin):
    name = "exception_hook"
    version = "1.0.0"
    description = "Exception test"
    author = "Tester"
    
    def initialize(self, config):
        return True
    
    def shutdown(self):
        return True
    
    def get_hooks(self):
        return {
            PluginHook.BEFORE_DOWNLOAD: self.failing_hook,
        }
    
    def failing_hook(self, url, **kwargs):
        raise RuntimeError("Hook failed!")
""")
        
        manager = PluginManager(search_paths=[temp_dir])
        manager.load_plugin(plugin_file)
        manager.initialize_plugin("exception_hook")
        
        # Should not raise, but return error result
        results = manager.execute_hook(
            PluginHook.BEFORE_DOWNLOAD,
            url="https://example.com",
        )
        
        assert len(results) > 0
        assert results[0].success is False


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
