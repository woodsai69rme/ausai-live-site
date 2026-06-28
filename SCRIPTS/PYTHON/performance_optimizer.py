"""
Performance Optimization Module for YouTube Enhancement Tools
This module implements performance optimizations including profiling, caching, 
resource optimization, and enhanced error handling.
"""

import functools
import time
import cProfile
import pstats
import io
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional
import threading
import queue
import psutil
import gc
from pathlib import Path
import os
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class LRUCache:
    """
    A simple Least Recently Used (LRU) cache implementation
    """
    
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.lock = threading.RLock()  # Thread-safe operations
    
    def get(self, key: Any) -> Optional[Any]:
        """Get a value from the cache"""
        with self.lock:
            if key in self.cache:
                # Move to end to show it's recently used
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            else:
                self.misses += 1
                return None
    
    def put(self, key: Any, value: Any) -> None:
        """Put a value in the cache"""
        with self.lock:
            if key in self.cache:
                # Update existing key
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.maxsize:
                # Remove oldest item
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def clear(self) -> None:
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


def cached_function(maxsize: int = 128):
    """
    Decorator to cache function results using LRU cache
    """
    cache = LRUCache(maxsize)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute and store in cache
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result
        
        # Attach cache to function for inspection
        wrapper.cache = cache
        return wrapper
    
    return decorator


def time_it(func: Callable) -> Callable:
    """
    Decorator to time function execution
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
    
    return wrapper


def profile_function(func: Callable) -> Callable:
    """
    Decorator to profile function execution with cProfile
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            pr.disable()
            
            # Create a string stream to hold profile results
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats()
            
            logger.debug(f"Profiling results for {func.__name__}:\n{s.getvalue()}")
    
    return wrapper


class ResourceManager:
    """
    Class to manage system resources efficiently
    """
    
    def __init__(self):
        self.process = psutil.Process()
        self.resource_limits = {
            'cpu_percent': 80,  # Max CPU usage percent
            'memory_mb': 1024,  # Max memory usage in MB
            'disk_percent': 90  # Max disk usage percent
        }
        self.active_operations = 0
        self.operation_lock = threading.Lock()
    
    def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            cpu_percent = self.process.cpu_percent()
            memory_mb = self.process.memory_info().rss / 1024 / 1024  # MB
            disk_usage = psutil.disk_usage('.').percent
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'disk_percent': disk_usage,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return None
    
    def is_within_limits(self) -> bool:
        """Check if current resource usage is within limits"""
        usage = self.get_current_usage()
        if not usage:
            return True  # If we can't measure, assume it's OK
        
        return (
            usage['cpu_percent'] <= self.resource_limits['cpu_percent'] and
            usage['memory_mb'] <= self.resource_limits['memory_mb'] and
            usage['disk_percent'] <= self.resource_limits['disk_percent']
        )
    
    def wait_if_over_limit(self, timeout: float = 5.0) -> bool:
        """Wait if resource usage is over limits"""
        start_time = time.time()
        
        while not self.is_within_limits() and (time.time() - start_time) < timeout:
            time.sleep(0.1)  # Wait 100ms before checking again
        
        return self.is_within_limits()
    
    def register_operation(self) -> bool:
        """Register an operation, respecting resource limits"""
        with self.operation_lock:
            if not self.is_within_limits():
                return False  # Too busy to start another operation
            
            self.active_operations += 1
            return True
    
    def unregister_operation(self):
        """Unregister an operation"""
        with self.operation_lock:
            self.active_operations = max(0, self.active_operations - 1)


class OptimizedVideoProcessor:
    """
    Optimized video processing with caching and resource management
    """
    
    def __init__(self):
        self.cache = LRUCache(maxsize=64)
        self.resource_manager = ResourceManager()
        self.processing_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
    
    @cached_function(maxsize=32)
    @time_it
    def validate_youtube_url_optimized(self, url: str) -> bool:
        """
        Optimized URL validation with caching
        """
        import re
        from urllib.parse import urlparse
        
        # Basic format validation
        if not isinstance(url, str) or len(url) > 2048:
            return False
        
        # Sanitize the URL
        sanitized_url = url.strip()
        
        # Parse the URL
        try:
            parsed = urlparse(sanitized_url)
        except Exception:
            return False
        
        # Check if the hostname is a valid YouTube domain
        valid_domains = [
            'youtube.com', 'www.youtube.com', 'youtu.be',
            'youtube-nocookie.com', 'www.youtube-nocookie.com'
        ]
        
        if parsed.hostname not in valid_domains:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.\./',  # Path traversal
            r'%00',     # Null byte
            r'<script', # Potential XSS
            r'javascript:', # JavaScript injection
            r'data:', # Data URI schemes
            r'vbscript:', # VB Script
            r'file://', # Local file access
            r'ftp://', # FTP access
            r'\\', # Windows path separator
            r'%2e%2e', # URL encoded traversal
            r'\.\.%2f', # Mixed encoding traversal
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sanitized_url, re.IGNORECASE):
                return False
        
        # Validate against known YouTube patterns
        youtube_patterns = [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://youtu\.be/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/v/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, sanitized_url):
                return True
        
        return False
    
    @cached_function(maxsize=16)
    @time_it
    def extract_video_info_optimized(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Optimized video info extraction with caching
        """
        import subprocess
        import json
        
        try:
            cmd = ["yt-dlp", "--dump-json", url]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
            video_info = json.loads(result.stdout)
            
            return {
                "title": video_info.get("title", ""),
                "description": video_info.get("description", ""),
                "uploader": video_info.get("uploader", ""),
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0)
            }
        except Exception as e:
            logger.error(f"Error extracting video info from {url}: {e}")
            return {}
    
    def optimize_memory_usage(self):
        """
        Optimize memory usage by triggering garbage collection
        """
        gc.collect()
        logger.debug("Garbage collection triggered for memory optimization")
    
    def process_with_resource_management(self, func: Callable, *args, **kwargs) -> Any:
        """
        Process a function with resource management
        """
        if not self.resource_manager.register_operation():
            logger.warning("Resource limits exceeded, waiting...")
            if not self.resource_manager.wait_if_over_limit():
                raise RuntimeError("System resources are over limits and did not recover")
        
        try:
            return func(*args, **kwargs)
        finally:
            self.resource_manager.unregister_operation()


class AsyncBatchProcessor:
    """
    Asynchronous batch processor for handling multiple operations efficiently
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def start_workers(self):
        """Start worker threads"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"BatchWorker-{i}")
            worker.start()
            self.workers.append(worker)
    
    def stop_workers(self):
        """Stop worker threads"""
        self.running = False
        # Add sentinel values to stop workers
        for _ in range(self.max_workers):
            self.task_queue.put(None)
        
        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()
        
        self.workers = []
    
    def _worker(self):
        """Worker function that processes tasks"""
        while self.running:
            task = self.task_queue.get()
            if task is None:  # Sentinel value to stop worker
                break
            
            func, args, kwargs, task_id = task
            try:
                result = func(*args, **kwargs)
                self.result_queue.put((task_id, result, None))
            except Exception as e:
                self.result_queue.put((task_id, None, str(e)))
            finally:
                self.task_queue.task_done()
    
    def submit_task(self, func: Callable, *args, task_id: str = None, **kwargs):
        """Submit a task for asynchronous processing"""
        if task_id is None:
            task_id = f"task_{time.time_ns()}"
        
        self.task_queue.put((func, args, kwargs, task_id))
        return task_id
    
    def get_results(self, timeout: float = None) -> list:
        """Get all available results"""
        results = []
        try:
            while True:
                result = self.result_queue.get_nowait()
                results.append(result)
        except queue.Empty:
            pass
        
        return results


def optimize_config_loading():
    """
    Optimize configuration loading with caching
    """
    config_cache = LRUCache(maxsize=4)  # Small cache for config files
    
    def cached_load_config(config_file: str = "youtube_tools_config.json"):
        cached_config = config_cache.get(config_file)
        if cached_config is not None:
            logger.debug(f"Loaded config from cache: {config_file}")
            return cached_config
        
        # Load from file
        import json
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # Return default config
            config = {
                "settings": {
                    "download_dir": "./downloads/",
                    "output_dir": "./output/",
                    "temp_dir": "./temp/",
                    "default_quality": "720p",
                    "batch_size": 5,
                    "max_retries": 3,
                    "timeout_seconds": 300,
                    "auto_edit_settings": {
                        "silent_threshold": 0.04,
                        "video_speed": 1.25
                    }
                }
            }
            # Save default config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        config_cache.put(config_file, config)
        logger.debug(f"Loaded and cached config: {config_file}")
        return config
    
    return cached_load_config


# Create global instances for reuse
optimized_processor = OptimizedVideoProcessor()
batch_processor = AsyncBatchProcessor(max_workers=4)
cached_load_config = optimize_config_loading()


def enhance_performance_in_main_module():
    """
    Apply performance enhancements to the main module functions
    This function would be called to monkey-patch or enhance the original functions
    """
    # This would enhance the original functions in youtube_enhancement_tools.py
    # For example, replacing the original validate_youtube_url with the optimized version
    pass


if __name__ == "__main__":
    # Example usage of performance optimization features
    print("YouTube Enhancement Tools - Performance Optimization Module")
    print("=" * 60)
    
    # Example of using the cache
    cache = LRUCache(maxsize=10)
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    
    print(f"Cache hit rate: {cache.hit_rate:.2%}")
    print(f"Retrieved value: {cache.get('key1')}")
    print(f"Cache hit rate after retrieval: {cache.hit_rate:.2%}")
    
    # Example of using the decorated functions
    @cached_function(maxsize=5)
    @time_it
    def slow_function(n):
        # Simulate a slow computation
        time.sleep(0.1)
        return n * n
    
    print("\nTesting cached and timed function:")
    for i in range(3):
        result = slow_function(i)
        print(f"slow_function({i}) = {result}")
    
    # Run twice to show caching effect
    print("\nRunning again to demonstrate caching:")
    for i in range(3):
        result = slow_function(i)
        print(f"slow_function({i}) = {result}")
    
    # Example of resource management
    print("\nTesting resource management:")
    rm = ResourceManager()
    usage = rm.get_current_usage()
    if usage:
        print(f"Current CPU usage: {usage['cpu_percent']:.1f}%")
        print(f"Current memory usage: {usage['memory_mb']:.1f} MB")
    
    # Example of batch processing
    print("\nTesting batch processing:")
    batch_processor.start_workers()
    
    # Submit some tasks
    for i in range(5):
        batch_processor.submit_task(slow_function, i, task_id=f"task_{i}")
    
    # Wait a bit for tasks to complete
    time.sleep(1)
    
    # Get results
    results = batch_processor.get_results()
    for task_id, result, error in results:
        if error:
            print(f"{task_id}: Error - {error}")
        else:
            print(f"{task_id}: Result - {result}")
    
    batch_processor.stop_workers()
    
    print("\nPerformance optimization module initialized successfully!")