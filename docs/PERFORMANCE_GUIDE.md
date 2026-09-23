# YouTube Enhancement Tools v3.2.0 - Performance Guide

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Optimization Techniques](#optimization-techniques)
3. [Caching Strategies](#caching-strategies)
4. [Concurrency Best Practices](#concurrency-best-practices)
5. [Resource Management](#resource-management)
6. [Benchmarking Guide](#benchmarking-guide)
7. [Monitoring and Profiling](#monitoring-and-profiling)
8. [Performance Tuning Checklist](#performance-tuning-checklist)

---

## Performance Overview

### Performance Goals

YouTube Enhancement Tools v3.2.0 is designed for high-performance video processing with the following targets:

| Metric | Target | Description |
|--------|--------|-------------|
| API Response Time | < 200ms | YouTube API calls (cached) |
| Video Processing | < 1x realtime | Process faster than video duration |
| Concurrent Tasks | 100+ | Simultaneous processing tasks |
| Memory Usage | < 2GB | Per worker process |
| Throughput | 1000+ videos/hour | Batch processing capacity |
| Cache Hit Rate | > 80% | For repeated API calls |

### Architecture Performance Characteristics

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      PERFORMANCE ARCHITECTURE                             │
└──────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                      Request Layer                                   │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │   Rate      │  │   Load      │  │   Request   │                 │
  │  │   Limiter   │  │  Balancer   │  │   Queue     │                 │
  │  │  (10k/s)    │  │  (1M/s)     │  │  (100k/s)   │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      Processing Layer                                │
  │  ┌─────────────────────────────────────────────────────────────────┐│
  │  │                    Worker Pool                                   ││
  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            ││
  │  │  │Worker 1 │  │Worker 2 │  │Worker 3 │  │Worker N │            ││
  │  │  │(async)  │  │(async)  │  │(async)  │  │(async)  │            ││
  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘            ││
  │  │                                                                 ││
  │  │  Throughput: 100 tasks/second per worker                        ││
  │  │  Latency: < 50ms task scheduling                                ││
  │  └─────────────────────────────────────────────────────────────────┘│
  └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                       Data Layer                                     │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │    Redis    │  │  PostgreSQL │  │     S3      │                 │
  │  │   Cache     │  │   Database  │  │   Storage   │                 │
  │  │  < 1ms      │  │  < 10ms     │  │  < 100ms    │                 │
  │  │  (p99)      │  │  (p99)      │  │  (p99)      │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## Optimization Techniques

### Async I/O Optimization

#### Connection Pooling

```python
import aiohttp
import asyncio

class OptimizedHTTPClient:
    """Optimized HTTP client with connection pooling."""
    
    def __init__(self, max_connections: int = 100):
        self._connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True,
        )
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "YouTube-Enhancement-Tools/3.2.0"}
            )
        return self._session
    
    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make optimized request."""
        session = await self.get_session()
        return await session.request(method, url, **kwargs)
    
    async def close(self):
        """Close session and connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        await self._connector.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Usage
async def fetch_multiple_urls(urls: List[str]) -> List[bytes]:
    async with OptimizedHTTPClient() as client:
        tasks = [client.request("GET", url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.read() for r in responses]
```

#### Batch Operations

```python
class BatchProcessor:
    """Process items in optimized batches."""
    
    def __init__(
        self,
        batch_size: int = 50,
        max_concurrent: int = 10
    ):
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(
        self,
        items: List[Any],
        processor: Callable
    ) -> List[Any]:
        """Process items in batches."""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await self._process_batch(batch, processor)
            results.extend(batch_results)
        
        return results
    
    async def _process_batch(
        self,
        batch: List[Any],
        processor: Callable
    ) -> List[Any]:
        """Process single batch with concurrency control."""
        async def process_with_semaphore(item):
            async with self.semaphore:
                return await processor(item)
        
        tasks = [process_with_semaphore(item) for item in batch]
        return await asyncio.gather(*tasks)


# Usage
async def process_videos(video_ids: List[str]):
    processor = BatchProcessor(batch_size=50, max_concurrent=10)
    
    async def fetch_video(video_id: str):
        return await client.get_video(video_id)
    
    videos = await processor.process_batch(video_ids, fetch_video)
    return videos
```

### Memory Optimization

#### Streaming Large Files

```python
from typing import AsyncGenerator

class StreamingDownloader:
    """Download large files with minimal memory usage."""
    
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
    
    async def download_stream(
        self,
        url: str,
        output_path: Path
    ) -> AsyncGenerator[int, None]:
        """Download file in chunks, yielding progress."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(self.chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        yield downloaded  # Progress update
        
        yield total_size  # Final size
    
    async def download_to_memory(
        self,
        url: str,
        max_size: int = 100 * 1024 * 1024  # 100MB limit
    ) -> bytes:
        """Download to memory with size limit."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                
                content_length = int(response.headers.get('content-length', 0))
                if content_length > max_size:
                    raise ValueError(f"File too large: {content_length} bytes")
                
                chunks = []
                total = 0
                
                async for chunk in response.content.iter_chunked(self.chunk_size):
                    total += len(chunk)
                    if total > max_size:
                        raise ValueError("File exceeds size limit")
                    chunks.append(chunk)
                
                return b''.join(chunks)
```

#### Object Pooling

```python
import asyncio
from collections import deque
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class AsyncObjectPool(Generic[T]):
    """Async object pool for reusable resources."""
    
    def __init__(
        self,
        factory: Callable[[], T],
        cleanup: Callable[[T], None],
        max_size: int = 10
    ):
        self._factory = factory
        self._cleanup = cleanup
        self._max_size = max_size
        self._pool: deque = deque()
        self._lock = asyncio.Lock()
        self._created = 0
    
    async def acquire(self) -> T:
        """Acquire object from pool."""
        async with self._lock:
            if self._pool:
                return self._pool.popleft()
            
            if self._created < self._max_size:
                self._created += 1
                return self._factory()
        
        # Wait for available object
        while True:
            async with self._lock:
                if self._pool:
                    return self._pool.popleft()
            await asyncio.sleep(0.01)
    
    async def release(self, obj: T) -> None:
        """Release object back to pool."""
        async with self._lock:
            if len(self._pool) < self._max_size:
                self._pool.append(obj)
            else:
                self._cleanup(obj)
                self._created -= 1
    
    async def close(self) -> None:
        """Close pool and cleanup all objects."""
        async with self._lock:
            while self._pool:
                obj = self._pool.popleft()
                self._cleanup(obj)
            self._pool.clear()


# Usage: Database connection pool
class ConnectionPool:
    def __init__(self, db_url: str, max_connections: int = 10):
        def factory():
            return create_database_connection(db_url)
        
        def cleanup(conn):
            conn.close()
        
        self._pool = AsyncObjectPool(factory, cleanup, max_connections)
    
    async def get_connection(self):
        return await self._pool.acquire()
    
    async def return_connection(self, conn):
        await self._pool.release(conn)
    
    async def execute_query(self, query: str, params: tuple = None):
        conn = await self.get_connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
        finally:
            await self.return_connection(conn)
```

### CPU Optimization

#### Using Process Pool for CPU-Bound Tasks

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

class CPUIntensiveProcessor:
    """Process CPU-intensive tasks in separate processes."""
    
    def __init__(self, max_workers: int = 4):
        self._executor = ProcessPoolExecutor(max_workers=max_workers)
        self._loop = asyncio.get_event_loop()
    
    async def process_video_frame(
        self,
        frame_data: bytes,
        operation: str
    ) -> bytes:
        """Process video frame in separate process."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._process_frame_sync,
            frame_data,
            operation
        )
    
    def _process_frame_sync(self, frame_data: bytes, operation: str) -> bytes:
        """Synchronous frame processing (runs in process pool)."""
        import cv2
        import numpy as np
        
        # Decode frame
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Apply operation
        if operation == "resize":
            frame = cv2.resize(frame, (1920, 1080))
        elif operation == "grayscale":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif operation == "enhance":
            # Apply CLAHE for contrast enhancement
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            frame = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        
        # Encode back
        _, encoded = cv2.imencode('.jpg', frame)
        return encoded.tobytes()
    
    async def close(self):
        """Shutdown executor."""
        self._executor.shutdown(wait=True)
```

#### Vectorized Operations with NumPy

```python
import numpy as np
from typing import List

class VideoAnalyticsOptimizer:
    """Optimized video analytics using NumPy."""
    
    @staticmethod
    def calculate_engagement_metrics(
        views: np.ndarray,
        likes: np.ndarray,
        comments: np.ndarray,
        watch_time: np.ndarray
    ) -> dict:
        """Calculate engagement metrics using vectorized operations."""
        
        # Vectorized calculations (much faster than loops)
        like_rates = np.divide(likes, views, out=np.zeros_like(likes), where=views!=0)
        comment_rates = np.divide(comments, views, out=np.zeros_like(comments), where=views!=0)
        avg_watch_time = np.mean(watch_time)
        
        # Engagement score (weighted combination)
        engagement_scores = (
            like_rates * 0.4 +
            comment_rates * 0.3 +
            np.clip(watch_time / 300, 0, 1) * 0.3  # Normalize to 5 minutes
        )
        
        return {
            "avg_like_rate": float(np.mean(like_rates)),
            "avg_comment_rate": float(np.mean(comment_rates)),
            "avg_watch_time": float(avg_watch_time),
            "avg_engagement_score": float(np.mean(engagement_scores)),
            "top_videos": np.argsort(engagement_scores)[-10:][::-1].tolist()
        }
    
    @staticmethod
    def detect_trends(
        daily_views: np.ndarray,
        window_size: int = 7
    ) -> dict:
        """Detect viewing trends using rolling windows."""
        
        # Calculate rolling average
        rolling_avg = np.convolve(
            daily_views,
            np.ones(window_size)/window_size,
            mode='valid'
        )
        
        # Calculate trend direction
        if len(rolling_avg) >= 2:
            trend = rolling_avg[-1] - rolling_avg[-2]
            trend_direction = "up" if trend > 0 else "down"
            trend_percent = (trend / rolling_avg[-2]) * 100 if rolling_avg[-2] > 0 else 0
        else:
            trend_direction = "stable"
            trend_percent = 0
        
        return {
            "rolling_average": float(rolling_avg[-1]) if len(rolling_avg) > 0 else 0,
            "trend_direction": trend_direction,
            "trend_percent": float(trend_percent),
            "volatility": float(np.std(daily_views) / np.mean(daily_views)) if np.mean(daily_views) > 0 else 0
        }
```

---

## Caching Strategies

### Multi-Level Caching

```python
from typing import Optional, Any
from enum import Enum
import asyncio

class CacheLevel(Enum):
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"


class MultiLevelCache:
    """Multi-level caching with automatic promotion."""
    
    def __init__(
        self,
        memory_cache: Any,
        redis_cache: Any,
        hit_threshold: int = 3
    ):
        self._memory = memory_cache
        self._redis = redis_cache
        self._hit_counts: dict = {}
        self._hit_threshold = hit_threshold
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache hierarchy."""
        # Try memory first (fastest)
        value = await self._memory.get(key)
        if value is not None:
            await self._record_hit(key)
            return value
        
        # Try Redis (fast)
        value = await self._redis.get(key)
        if value is not None:
            await self._record_hit(key)
            # Promote to memory cache
            await self._memory.set(key, value)
            return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """Set value in all cache levels."""
        await self._memory.set(key, value, ttl=min(ttl or 300, 60))
        await self._redis.set(key, value, ttl)
    
    async def _record_hit(self, key: str) -> None:
        """Record cache hit for promotion tracking."""
        async with self._lock:
            self._hit_counts[key] = self._hit_counts.get(key, 0) + 1
    
    async def delete(self, key: str) -> None:
        """Delete from all cache levels."""
        await self._memory.delete(key)
        await self._redis.delete(key)
        self._hit_counts.pop(key, None)
```

### Cache-Aside Pattern

```python
from functools import wraps
from typing import Callable, Any
import hashlib
import json

def cache_aside(
    cache: Any,
    ttl: int = 3600,
    key_prefix: str = "",
    serialize: bool = True
):
    """Cache-aside pattern decorator."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key_data = {
                "function": func.__qualname__,
                "args": args,
                "kwargs": kwargs
            }
            key_hash = hashlib.md5(
                json.dumps(key_data, default=str).encode()
            ).hexdigest()
            cache_key = f"{key_prefix}:{key_hash}"
            
            # Try cache first
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Usage
@cache_aside(cache=redis_cache, ttl=3600, key_prefix="video")
async def get_video_data(video_id: str) -> VideoData:
    """Fetch video data with automatic caching."""
    return await youtube_client.get_video(video_id)
```

### Write-Through Cache

```python
class WriteThroughCache:
    """Write-through cache for consistent reads and writes."""
    
    def __init__(self, cache: Any, database: Any):
        self._cache = cache
        self._database = database
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value (always consistent with database)."""
        # Try cache first
        value = await self._cache.get(key)
        if value is not None:
            return value
        
        # Cache miss - read from database
        async with self._lock:
            # Double-check after acquiring lock
            value = await self._cache.get(key)
            if value is not None:
                return value
            
            value = await self._database.get(key)
            if value is not None:
                await self._cache.set(key, value)
            
            return value
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Write to both cache and database."""
        async with self._lock:
            # Write to database first
            await self._database.set(key, value)
            # Then update cache
            await self._cache.set(key, value, ttl=ttl)
    
    async def delete(self, key: str) -> None:
        """Delete from both cache and database."""
        async with self._lock:
            await self._database.delete(key)
            await self._cache.delete(key)
```

### Cache Invalidation Strategies

```python
class CacheInvalidationManager:
    """Manage cache invalidation strategies."""
    
    def __init__(self, cache: Any):
        self._cache = cache
        self._invalidation_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start invalidation worker."""
        self._worker_task = asyncio.create_task(self._invalidation_worker())
    
    async def stop(self):
        """Stop invalidation worker."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    async def invalidate_pattern(self, pattern: str, delay: float = 0):
        """Schedule pattern-based invalidation."""
        await self._invalidation_queue.put({
            "type": "pattern",
            "pattern": pattern,
            "delay": delay
        })
    
    async def invalidate_key(self, key: str, delay: float = 0):
        """Schedule key invalidation."""
        await self._invalidation_queue.put({
            "type": "key",
            "key": key,
            "delay": delay
        })
    
    async def _invalidation_worker(self):
        """Process invalidation queue."""
        while True:
            try:
                task = await self._invalidation_queue.get()
                
                if task["delay"] > 0:
                    await asyncio.sleep(task["delay"])
                
                if task["type"] == "pattern":
                    await self._cache.clear(task["pattern"])
                elif task["type"] == "key":
                    await self._cache.delete(task["key"])
                
                self._invalidation_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Invalidation error: {e}")


# Usage examples
async def on_video_update(video_id: str):
    """Invalidate cache when video is updated."""
    invalidation = CacheInvalidationManager(redis_cache)
    
    # Immediate invalidation
    await invalidation.invalidate_key(f"video:{video_id}")
    
    # Delayed invalidation for related caches
    await invalidation.invalidate_pattern(f"channel:*:videos", delay=1.0)
    await invalidation.invalidate_pattern(f"analytics:{video_id}:*", delay=2.0)
```

### Cache Warming

```python
class CacheWarmer:
    """Proactively warm cache with predicted data."""
    
    def __init__(
        self,
        cache: Any,
        client: YouTubeClient,
        warm_keys: List[str]
    ):
        self._cache = cache
        self._client = client
        self._warm_keys = warm_keys
        self._warm_task: Optional[asyncio.Task] = None
    
    async def start_warming(self, interval: int = 300):
        """Start periodic cache warming."""
        self._warm_task = asyncio.create_task(
            self._warming_loop(interval)
        )
    
    async def stop_warming(self):
        """Stop cache warming."""
        if self._warm_task:
            self._warm_task.cancel()
            try:
                await self._warm_task
            except asyncio.CancelledError:
                pass
    
    async def _warming_loop(self, interval: int):
        """Periodic warming loop."""
        while True:
            try:
                await self._warm_cache()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Cache warming error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _warm_cache(self):
        """Warm cache with predicted hot data."""
        tasks = []
        
        for key in self._warm_keys:
            # Check if already cached
            if await self._cache.exists(key):
                continue
            
            # Fetch and cache
            if key.startswith("video:"):
                video_id = key.split(":")[1]
                tasks.append(self._warm_video(video_id))
            elif key.startswith("channel:"):
                channel_id = key.split(":")[1]
                tasks.append(self._warm_channel(channel_id))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _warm_video(self, video_id: str):
        """Warm video data."""
        video = await self._client.get_video(video_id)
        await self._cache.set(f"video:{video_id}", video, ttl=3600)
    
    async def _warm_channel(self, channel_id: str):
        """Warm channel data."""
        channel = await self._client.get_channel(channel_id=channel_id)
        await self._cache.set(f"channel:{channel_id}", channel, ttl=7200)
```

---

## Concurrency Best Practices

### Semaphore-Based Concurrency Control

```python
import asyncio
from typing import List, Any, Callable

class ConcurrencyController:
    """Control concurrency with semaphores."""
    
    def __init__(self, max_concurrent: int = 10):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_tasks = 0
        self._lock = asyncio.Lock()
    
    async def execute(
        self,
        coro: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute coroutine with concurrency control."""
        async with self._semaphore:
            async with self._lock:
                self._active_tasks += 1
            
            try:
                return await coro(*args, **kwargs)
            finally:
                async with self._lock:
                    self._active_tasks -= 1
    
    async def execute_all(
        self,
        coros: List[Callable],
        return_exceptions: bool = False
    ) -> List[Any]:
        """Execute multiple coroutines with concurrency control."""
        tasks = [
            self.execute(coro) if asyncio.iscoroutinefunction(coro) else self.execute(lambda: coro)
            for coro in coros
        ]
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)
    
    @property
    def active_tasks(self) -> int:
        """Get number of active tasks."""
        return self._active_tasks
    
    @property
    def available_slots(self) -> int:
        """Get available concurrency slots."""
        return self._semaphore._value


# Usage
async def process_videos_concurrent(video_ids: List[str]):
    controller = ConcurrencyController(max_concurrent=5)
    
    async def process_single(video_id: str):
        video = await client.get_video(video_id)
        return await processor.process(video)
    
    coros = [process_single(vid) for vid in video_ids]
    results = await controller.execute_all(coros, return_exceptions=True)
    
    return results
```

### Task Group Pattern

```python
import asyncio
from contextlib import asynccontextmanager
from typing import List, Any

class TaskGroup:
    """Manage group of related tasks."""
    
    def __init__(self, timeout: float = None):
        self._tasks: List[asyncio.Task] = []
        self._timeout = timeout
        self._errors: List[Exception] = []
    
    def create_task(self, coro) -> asyncio.Task:
        """Create task in group."""
        task = asyncio.create_task(coro)
        task.add_done_callback(self._handle_done)
        self._tasks.append(task)
        return task
    
    def _handle_done(self, task: asyncio.Task):
        """Handle task completion."""
        if task.exception() and not task.cancelled():
            self._errors.append(task.exception())
    
    async def wait(self, return_exceptions: bool = False) -> List[Any]:
        """Wait for all tasks to complete."""
        if self._timeout:
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*self._tasks, return_exceptions=return_exceptions),
                    timeout=self._timeout
                )
            except asyncio.TimeoutError:
                self.cancel()
                raise
        else:
            results = await asyncio.gather(*self._tasks, return_exceptions=return_exceptions)
        
        if self._errors and not return_exceptions:
            raise self._errors[0]
        
        return results
    
    def cancel(self):
        """Cancel all tasks."""
        for task in self._tasks:
            if not task.done():
                task.cancel()
    
    @property
    def errors(self) -> List[Exception]:
        """Get collected errors."""
        return self._errors


# Usage
async def process_with_task_group():
    group = TaskGroup(timeout=60)
    
    # Create tasks
    task1 = group.create_task(fetch_video("id1"))
    task2 = group.create_task(fetch_video("id2"))
    task3 = group.create_task(fetch_video("id3"))
    
    # Wait for completion
    try:
        results = await group.wait()
        return results
    except asyncio.TimeoutError:
        print("Processing timed out")
        return None
```

### Producer-Consumer Pattern

```python
import asyncio
from typing import Any, Optional

class ProducerConsumerQueue:
    """Async producer-consumer queue with backpressure."""
    
    def __init__(
        self,
        max_size: int = 100,
        num_consumers: int = 4
    ):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._num_consumers = num_consumers
        self._consumers: List[asyncio.Task] = []
        self._producer_done = asyncio.Event()
        self._results: List[Any] = []
        self._results_lock = asyncio.Lock()
    
    async def produce(self, item: Any) -> None:
        """Add item to queue (blocks if full)."""
        await self._queue.put(item)
    
    async def consume(
        self,
        processor: Callable[[Any], Any]
    ) -> None:
        """Consumer worker."""
        while True:
            try:
                item = await self._queue.get()
                
                if item is None:  # Poison pill
                    self._queue.task_done()
                    break
                
                try:
                    result = await processor(item)
                    async with self._results_lock:
                        self._results.append(result)
                except Exception as e:
                    logging.error(f"Processing error: {e}")
                finally:
                    self._queue.task_done()
                    
            except asyncio.CancelledError:
                break
    
    async def start_consumers(self, processor: Callable[[Any], Any]):
        """Start consumer workers."""
        self._consumers = [
            asyncio.create_task(self.consume(processor))
            for _ in range(self._num_consumers)
        ]
    
    def producer_finished(self) -> None:
        """Signal producer is done."""
        self._producer_done.set()
    
    async def wait_completion(self) -> List[Any]:
        """Wait for all items to be processed."""
        # Send poison pills
        for _ in range(self._num_consumers):
            await self._queue.put(None)
        
        # Wait for consumers
        await asyncio.gather(*self._consumers)
        
        return self._results
    
    @property
    def queue_size(self) -> int:
        """Get current queue size."""
        return self._queue.qsize()


# Usage
async def process_video_pipeline(video_ids: List[str]):
    pc_queue = ProducerConsumerQueue(max_size=50, num_consumers=4)
    
    async def processor(video_id: str):
        video = await client.get_video(video_id)
        return await video_processor.process(video)
    
    # Start consumers
    await pc_queue.start_consumers(processor)
    
    # Produce items
    for video_id in video_ids:
        await pc_queue.produce(video_id)
    
    # Signal done and wait
    pc_queue.producer_finished()
    results = await pc_queue.wait_completion()
    
    return results
```

### Rate Limiting

```python
import asyncio
import time
from typing import Optional

class TokenBucketRateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        rate: float,  # Tokens per second
        capacity: int  # Maximum tokens
    ):
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens (blocks if unavailable)."""
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._last_update
                
                # Refill tokens
                self._tokens = min(
                    self._capacity,
                    self._tokens + elapsed * self._rate
                )
                self._last_update = now
                
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                
                # Calculate wait time
                wait_time = (tokens - self._tokens) / self._rate
            
            await asyncio.sleep(wait_time)
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens without blocking."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            
            self._tokens = min(
                self._capacity,
                self._tokens + elapsed * self._rate
            )
            self._last_update = now
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            
            return False
    
    @property
    def available_tokens(self) -> float:
        """Get available tokens."""
        return self._tokens


class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""
    
    def __init__(
        self,
        max_requests: int,
        window_seconds: float
    ):
        self._max_requests = max_requests
        self._window = window_seconds
        self._requests: deque = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire request slot."""
        while True:
            async with self._lock:
                now = time.monotonic()
                
                # Remove old requests
                while self._requests and self._requests[0] <= now - self._window:
                    self._requests.popleft()
                
                if len(self._requests) < self._max_requests:
                    self._requests.append(now)
                    return
                
                # Calculate wait time
                wait_time = self._requests[0] + self._window - now
            
            await asyncio.sleep(max(0, wait_time))


# Usage
async def rate_limited_api_calls():
    # 10 requests per second
    limiter = TokenBucketRateLimiter(rate=10, capacity=20)
    
    async def fetch_with_rate_limit(video_id: str):
        await limiter.acquire()
        return await client.get_video(video_id)
    
    # Process with rate limiting
    video_ids = ["id1", "id2", "id3", ...]
    results = await asyncio.gather(*[
        fetch_with_rate_limit(vid) for vid in video_ids
    ])
    
    return results
```

---

## Resource Management

### Connection Pool Management

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

class ResourceManager:
    """Manage pooled resources."""
    
    def __init__(
        self,
        max_connections: int = 20,
        max_idle_time: float = 300
    ):
        self._max_connections = max_connections
        self._max_idle_time = max_idle_time
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
        self._in_use: set = set()
        self._created: int = 0
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start resource manager."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop resource manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        while not self._pool.empty():
            conn = await self._pool.get()
            await self._close_connection(conn)
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[Any, None]:
        """Acquire connection from pool."""
        conn = await self._get_connection()
        self._in_use.add(id(conn))
        
        try:
            yield conn
        finally:
            self._in_use.discard(id(conn))
            await self._return_connection(conn)
    
    async def _get_connection(self):
        """Get or create connection."""
        # Try to get from pool
        try:
            conn = self._pool.get_nowait()
            # Verify connection is still valid
            if await self._is_valid(conn):
                return conn
            else:
                await self._close_connection(conn)
                self._created -= 1
        except asyncio.QueueEmpty:
            pass
        
        # Create new connection if under limit
        async with self._lock:
            if self._created < self._max_connections:
                conn = await self._create_connection()
                self._created += 1
                return conn
        
        # Wait for available connection
        return await self._pool.get()
    
    async def _return_connection(self, conn):
        """Return connection to pool."""
        try:
            self._pool.put_nowait(conn)
        except asyncio.QueueFull:
            await self._close_connection(conn)
            self._created -= 1
    
    async def _cleanup_loop(self):
        """Periodically cleanup idle connections."""
        while True:
            await asyncio.sleep(60)
            
            # Cleanup connections idle too long
            temp_pool = asyncio.Queue()
            while not self._pool.empty():
                conn = await self._pool.get()
                if id(conn) not in self._in_use:
                    # Check idle time (implementation dependent)
                    if self._is_idle_too_long(conn):
                        await self._close_connection(conn)
                        self._created -= 1
                    else:
                        temp_pool.put_nowait(conn)
            
            # Restore valid connections
            while not temp_pool.empty():
                self._pool.put_nowait(await temp_pool.get())
    
    async def _create_connection(self):
        """Create new connection (override in subclass)."""
        raise NotImplementedError
    
    async def _close_connection(self, conn):
        """Close connection (override in subclass)."""
        raise NotImplementedError
    
    async def _is_valid(self, conn) -> bool:
        """Check if connection is valid (override in subclass)."""
        raise NotImplementedError
    
    def _is_idle_too_long(self, conn) -> bool:
        """Check if connection is idle too long."""
        # Implementation depends on tracking idle time
        return False
```

### Memory Limiting

```python
import asyncio
import tracemalloc
from typing import Optional

class MemoryLimiter:
    """Limit memory usage with automatic cleanup."""
    
    def __init__(
        self,
        max_memory_mb: int = 2048,
        warning_threshold: float = 0.8
    ):
        self._max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self._warning_threshold = warning_threshold
        self._warning_callback: Optional[Callable] = None
        self._critical_callback: Optional[Callable] = None
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    def start_monitoring(self):
        """Start memory monitoring."""
        tracemalloc.start()
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
        tracemalloc.stop()
    
    def set_warning_callback(self, callback: Callable[[float], None]):
        """Set callback for memory warnings."""
        self._warning_callback = callback
    
    def set_critical_callback(self, callback: Callable[[], None]):
        """Set callback for critical memory."""
        self._critical_callback = callback
    
    async def _monitor_loop(self):
        """Monitor memory usage."""
        while self._monitoring:
            try:
                current, peak = tracemalloc.get_traced_memory()
                usage_percent = current / self._max_memory
                
                if usage_percent >= 1.0:
                    # Critical - trigger cleanup
                    if self._critical_callback:
                        await self._critical_callback()
                elif usage_percent >= self._warning_threshold:
                    # Warning
                    if self._warning_callback:
                        await self._warning_callback(usage_percent)
                
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Memory monitoring error: {e}")
    
    def get_memory_stats(self) -> dict:
        """Get current memory statistics."""
        current, peak = tracemalloc.get_traced_memory()
        return {
            "current_mb": current / 1024 / 1024,
            "peak_mb": peak / 1024 / 1024,
            "max_mb": self._max_memory / 1024 / 1024,
            "usage_percent": (current / self._max_memory) * 100
        }


# Usage
async def memory_aware_processing():
    limiter = MemoryLimiter(max_memory_mb=1024)
    
    async def on_warning(usage: float):
        print(f"Memory warning: {usage*100:.1f}% used")
        # Trigger garbage collection
        import gc
        gc.collect()
    
    async def on_critical():
        print("Critical memory usage!")
        # Aggressive cleanup
        import gc
        gc.collect()
        # Maybe pause processing
        await asyncio.sleep(10)
    
    limiter.set_warning_callback(on_warning)
    limiter.set_critical_callback(on_critical)
    limiter.start_monitoring()
    
    try:
        # Process videos
        await process_all_videos()
    finally:
        limiter.stop_monitoring()
        print(f"Memory stats: {limiter.get_memory_stats()}")
```

### File Descriptor Management

```python
import asyncio
import os
from contextlib import asynccontextmanager

class FileDescriptorLimiter:
    """Limit open file descriptors."""
    
    def __init__(self, max_fds: int = 1000):
        self._max_fds = max_fds
        self._semaphore = asyncio.Semaphore(max_fds)
        self._open_files: set = set()
        self._lock = asyncio.Lock()
    
    @asynccontextmanager
    async def open_file(self, path: str, mode: str = 'r'):
        """Open file with FD limiting."""
        async with self._semaphore:
            f = open(path, mode)
            
            async with self._lock:
                self._open_files.add(f)
            
            try:
                yield f
            finally:
                f.close()
                
                async with self._lock:
                    self._open_files.discard(f)
    
    @asynccontextmanager
    async def open_files(self, paths: List[str], mode: str = 'r'):
        """Open multiple files with FD limiting."""
        files = []
        try:
            for path in paths:
                async with self.open_file(path, mode) as f:
                    files.append(f)
            yield files
        finally:
            for f in files:
                if not f.closed:
                    f.close()
    
    @property
    def open_count(self) -> int:
        """Get number of open files."""
        return len(self._open_files)
    
    @property
    def available_fds(self) -> int:
        """Get available file descriptors."""
        return self._semaphore._value


# Usage
async def process_many_files(file_paths: List[str]):
    fd_limiter = FileDescriptorLimiter(max_fds=100)
    
    results = []
    for path in file_paths:
        async with fd_limiter.open_file(path, 'r') as f:
            content = f.read()
            results.append(process_content(content))
    
    return results
```

---

## Benchmarking Guide

### Performance Benchmarking Framework

```python
import asyncio
import time
import statistics
from dataclasses import dataclass
from typing import List, Callable, Any
import json

@dataclass
class BenchmarkResult:
    """Benchmark result data."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    p50: float
    p95: float
    p99: float
    throughput: float  # Operations per second


class Benchmark:
    """Performance benchmarking utility."""
    
    def __init__(self, warmup_iterations: int = 10):
        self._warmup_iterations = warmup_iterations
        self._results: List[BenchmarkResult] = []
    
    async def run(
        self,
        name: str,
        func: Callable,
        iterations: int = 100,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Run benchmark."""
        # Warmup
        for _ in range(self._warmup_iterations):
            await func(*args, **kwargs)
        
        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            await func(*args, **kwargs)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        # Calculate statistics
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            p50=self._percentile(times, 50),
            p95=self._percentile(times, 95),
            p99=self._percentile(times, 99),
            throughput=iterations / (sum(times) / 1000)
        )
        
        self._results.append(result)
        return result
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def report(self) -> str:
        """Generate benchmark report."""
        lines = ["=" * 60, "BENCHMARK RESULTS", "=" * 60]
        
        for result in self._results:
            lines.extend([
                f"\n{result.name}",
                f"  Iterations:    {result.iterations}",
                f"  Total Time:    {result.total_time:.2f}ms",
                f"  Average:       {result.avg_time:.2f}ms",
                f"  Min:           {result.min_time:.2f}ms",
                f"  Max:           {result.max_time:.2f}ms",
                f"  Std Dev:       {result.std_dev:.2f}ms",
                f"  P50:           {result.p50:.2f}ms",
                f"  P95:           {result.p95:.2f}ms",
                f"  P99:           {result.p99:.2f}ms",
                f"  Throughput:    {result.throughput:.2f} ops/sec"
            ])
        
        return "\n".join(lines)
    
    def save_json(self, path: str):
        """Save results to JSON."""
        data = [
            {
                "name": r.name,
                "iterations": r.iterations,
                "total_time": r.total_time,
                "avg_time": r.avg_time,
                "min_time": r.min_time,
                "max_time": r.max_time,
                "std_dev": r.std_dev,
                "p50": r.p50,
                "p95": r.p95,
                "p99": r.p99,
                "throughput": r.throughput
            }
            for r in self._results
        ]
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# Usage
async def run_benchmarks():
    benchmark = Benchmark(warmup_iterations=10)
    
    # Benchmark video fetch
    async def fetch_video():
        return await client.get_video("dQw4w9WgXcQ")
    
    result = await benchmark.run(
        "Video Fetch (cached)",
        fetch_video,
        iterations=100
    )
    
    # Benchmark video processing
    async def process_video():
        video = await client.get_video("dQw4w9WgXcQ")
        return await processor.process(video)
    
    result = await benchmark.run(
        "Video Processing",
        process_video,
        iterations=50
    )
    
    # Print report
    print(benchmark.report())
    
    # Save results
    benchmark.save_json("benchmark_results.json")
```

### Load Testing

```python
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List
import time

@dataclass
class LoadTestResult:
    """Load test result."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float


class LoadTester:
    """HTTP load testing utility."""
    
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._results: List[LoadTestResult] = []
    
    async def run_test(
        self,
        endpoint: str,
        concurrent_users: int,
        duration_seconds: int,
        method: str = "GET",
        body: dict = None
    ) -> LoadTestResult:
        """Run load test."""
        url = f"{self._base_url}{endpoint}"
        
        start_time = time.time()
        response_times = []
        success_count = 0
        failure_count = 0
        
        async def make_request(session: aiohttp.ClientSession):
            nonlocal success_count, failure_count
            
            while time.time() - start_time < duration_seconds:
                try:
                    req_start = time.time()
                    
                    async with session.request(method, url, json=body) as response:
                        response_times.append((time.time() - req_start) * 1000)
                        
                        if response.status < 400:
                            success_count += 1
                        else:
                            failure_count += 1
                            
                except Exception:
                    failure_count += 1
                
                await asyncio.sleep(0)  # Yield control
        
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(concurrent_users)]
            await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        total_requests = success_count + failure_count
        
        result = LoadTestResult(
            total_requests=total_requests,
            successful_requests=success_count,
            failed_requests=failure_count,
            requests_per_second=total_requests / total_time,
            avg_response_time=sum(response_times) / len(response_times) if response_times else 0,
            p95_response_time=self._percentile(response_times, 95),
            p99_response_time=self._percentile(response_times, 99),
            error_rate=failure_count / total_requests if total_requests > 0 else 0
        )
        
        self._results.append(result)
        return result
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def report(self) -> str:
        """Generate load test report."""
        lines = ["=" * 60, "LOAD TEST RESULTS", "=" * 60]
        
        for result in self._results:
            lines.extend([
                f"\nTotal Requests:     {result.total_requests}",
                f"Successful:         {result.successful_requests}",
                f"Failed:             {result.failed_requests}",
                f"Requests/Second:    {result.requests_per_second:.2f}",
                f"Avg Response Time:  {result.avg_response_time:.2f}ms",
                f"P95 Response Time:  {result.p95_response_time:.2f}ms",
                f"P99 Response Time:  {result.p99_response_time:.2f}ms",
                f"Error Rate:         {result.error_rate*100:.2f}%"
            ])
        
        return "\n".join(lines)


# Usage
async def run_load_tests():
    tester = LoadTester("http://localhost:8080")
    
    # Test with 10 concurrent users for 30 seconds
    result = await tester.run_test(
        endpoint="/api/videos",
        concurrent_users=10,
        duration_seconds=30
    )
    
    print(tester.report())
```

---

## Monitoring and Profiling

### Performance Monitoring

```python
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self, retention_seconds: int = 3600):
        self._retention = retention_seconds
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
    
    def increment(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment counter."""
        key = self._make_key(name, labels)
        self._counters[key] += value
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge value."""
        key = self._make_key(name, labels)
        self._gauges[key] = value
    
    def observe(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record histogram observation."""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        
        # Also record as time series
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        )
        self._metrics[key].append(point)
        
        # Cleanup old data
        self._cleanup(key)
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create metric key."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def _cleanup(self, key: str):
        """Remove old metric data."""
        cutoff = time.time() - self._retention
        self._metrics[key] = [
            p for p in self._metrics[key]
            if p.timestamp > cutoff
        ]
    
    def get_counter(self, name: str, labels: Dict[str, str] = None) -> int:
        """Get counter value."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)
    
    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get gauge value."""
        key = self._make_key(name, labels)
        return self._gauges.get(key, 0)
    
    def get_histogram_stats(
        self,
        name: str,
        labels: Dict[str, str] = None
    ) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0, "sum": 0, "avg": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Counters
        for key, value in self._counters.items():
            name = key.split("{")[0] if "{" in key else key
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{key} {value}")
        
        # Gauges
        for key, value in self._gauges.items():
            name = key.split("{")[0] if "{" in key else key
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{key} {value}")
        
        # Histograms
        for key, values in self._histograms.items():
            name = key.split("{")[0] if "{" in key else key
            lines.append(f"# TYPE {name} histogram")
            if values:
                lines.append(f'{key}_sum {sum(values)}')
                lines.append(f'{key}_count {len(values)}')
        
        return "\n".join(lines)


# Usage
monitor = PerformanceMonitor()

# Record metrics
monitor.increment("api.requests.total", labels={"endpoint": "/videos"})
monitor.set_gauge("system.memory.used", memory_usage)
monitor.observe("api.request.duration", request_time, labels={"endpoint": "/videos"})

# Export for Prometheus
print(monitor.export_prometheus())
```

### Profiling Integration

```python
import cProfile
import pstats
import io
from contextlib import contextmanager
import asyncio

class Profiler:
    """Application profiler."""
    
    def __init__(self):
        self._profiler: Optional[cProfile.Profile] = None
        self._stats: Optional[pstats.Stats] = None
    
    @contextmanager
    def profile(self):
        """Context manager for profiling."""
        self._profiler = cProfile.Profile()
        self._profiler.enable()
        try:
            yield
        finally:
            self._profiler.disable()
            self._stats = pstats.Stats(self._profiler)
    
    def get_top_functions(self, n: int = 20, sort_by: str = "cumulative") -> str:
        """Get top N functions by time."""
        if not self._stats:
            return "No profiling data available"
        
        stream = io.StringIO()
        self._stats.sort_stats(sort_by).print_stats(n, stream=stream)
        return stream.getvalue()
    
    def save_stats(self, path: str):
        """Save profiling stats to file."""
        if self._stats:
            self._stats.dump_stats(path)
    
    def get_call_graph(self) -> dict:
        """Get call graph data."""
        if not self._stats:
            return {}
        
        call_graph = {}
        for key, (cc, nc, tt, ct, callers) in self._stats.stats.items():
            func_name = key[2]  # (filename, line, funcname)
            call_graph[func_name] = {
                "call_count": nc,
                "total_time": tt,
                "cumulative_time": ct,
                "callers": {
                    caller[2]: data[0]
                    for caller, data in callers.items()
                }
            }
        
        return call_graph


# Async profiling
async def profile_async(func, *args, **kwargs):
    """Profile async function."""
    profiler = Profiler()
    
    with profiler.profile():
        result = await func(*args, **kwargs)
    
    return result, profiler.get_top_functions(20)


# Usage
async def main():
    result, profile_output = await profile_async(process_all_videos)
    print(profile_output)
```

---

## Performance Tuning Checklist

### Application Level

- [ ] Enable connection pooling for all external services
- [ ] Implement multi-level caching (memory + Redis)
- [ ] Use batch operations where possible
- [ ] Implement proper rate limiting
- [ ] Use async I/O for all network operations
- [ ] Stream large files instead of loading into memory
- [ ] Implement circuit breakers for external services
- [ ] Use object pooling for expensive resources

### Database Level

- [ ] Add appropriate indexes for query patterns
- [ ] Use connection pooling
- [ ] Implement query result caching
- [ ] Use prepared statements
- [ ] Optimize slow queries
- [ ] Consider read replicas for read-heavy workloads
- [ ] Implement database connection timeout

### Infrastructure Level

- [ ] Use CDN for static assets
- [ ] Implement load balancing
- [ ] Configure auto-scaling
- [ ] Use appropriate instance types
- [ ] Enable compression (gzip/brotli)
- [ ] Configure proper timeouts
- [ ] Implement health checks
- [ ] Set up monitoring and alerting

### Code Level

- [ ] Profile code to identify bottlenecks
- [ ] Use vectorized operations (NumPy) for data processing
- [ ] Avoid unnecessary object creation
- [ ] Use generators for large datasets
- [ ] Implement lazy loading
- [ ] Use appropriate data structures
- [ ] Minimize lock contention
- [ ] Avoid blocking calls in async code

---

*Documentation generated for YouTube Enhancement Tools v3.2.0*
*Last updated: March 4, 2026*
