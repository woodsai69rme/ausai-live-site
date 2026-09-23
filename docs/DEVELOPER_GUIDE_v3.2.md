# YouTube Enhancement Tools v3.2.0 - Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Coding Standards](#coding-standards)
3. [Testing Guidelines](#testing-guidelines)
4. [Debugging Guide](#debugging-guide)
5. [Contributing Guidelines](#contributing-guidelines)
6. [Code Review Checklist](#code-review-checklist)
7. [Release Process](#release-process)

---

## Development Environment Setup

### Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| Python | 3.10+ | [python.org](https://python.org) |
| pip | 23.0+ | Included with Python |
| Git | 2.30+ | [git-scm.com](https://git-scm.com) |
| Node.js | 18+ (optional) | [nodejs.org](https://nodejs.org) |
| Redis | 6.0+ (optional) | [redis.io](https://redis.io) |
| FFmpeg | 5.0+ | [ffmpeg.org](https://ffmpeg.org) |

### System Requirements

```
Minimum:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 10 GB free space
- OS: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+)

Recommended:
- CPU: 8 cores
- RAM: 16 GB
- Storage: 50 GB SSD
- OS: Latest stable release
```

### Installation Steps

#### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/youtube-enhancement-tools.git
cd youtube-enhancement-tools

# Install pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Install base dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install optional dependencies
pip install -r requirements-optional.txt
```

#### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# .env file
# YouTube API Configuration
YOUTUBE_ENH_YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_ENH_YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_ENH_YOUTUBE_CLIENT_SECRET=your_client_secret

# Redis Configuration
YOUTUBE_ENH_REDIS_URL=redis://localhost:6379

# Database Configuration
YOUTUBE_ENH_DATABASE_URL=sqlite:///youtube_enh.db

# Storage Configuration
YOUTUBE_ENH_STORAGE_PROVIDER=local
YOUTUBE_ENH_STORAGE_PATH=./storage

# AWS S3 (if using)
YOUTUBE_ENH_AWS_ACCESS_KEY_ID=your_aws_key
YOUTUBE_ENH_AWS_SECRET_ACCESS_KEY=your_aws_secret
YOUTUBE_ENH_AWS_REGION=us-east-1
YOUTUBE_ENH_S3_BUCKET=your-bucket-name

# Logging
YOUTUBE_ENH_LOG_LEVEL=DEBUG
YOUTUBE_ENH_LOG_FORMAT=json

# Feature Flags
YOUTUBE_ENH_ENABLE_CACHE=true
YOUTUBE_ENH_ENABLE_QUEUE=true
YOUTUBE_ENH_MAX_CONCURRENT_TASKS=10
```

#### 5. Verify Installation

```bash
# Run health check
python -m youtube_enhancement_tools.health

# Run tests
pytest tests/ -v

# Check code style
ruff check .
mypy youtube_enhancement_tools/
```

### Docker Development Setup

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    redis-tools \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source
COPY . .

# Set environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "pytest", "tests/", "-v"]
```

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    environment:
      - YOUTUBE_ENH_REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests in container
docker-compose -f docker-compose.dev.yml run app pytest tests/
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org) with some modifications enforced by our linting tools.

#### Code Formatting

```python
# Use Black for formatting
# Line length: 88 characters (Black default)
# Indentation: 4 spaces

# Good
def process_video(
    video_id: str,
    options: Optional[ProcessOptions] = None,
    timeout: float = 30.0
) -> ProcessedVideo:
    """Process a video with the given options."""
    pass

# Bad - too long line
def process_video(video_id: str, options: Optional[ProcessOptions] = None, timeout: float = 30.0) -> ProcessedVideo:
    pass
```

#### Type Hints

All public functions and methods MUST have type hints:

```python
from typing import Optional, List, Dict, Any, Union

# Good - complete type hints
def get_video(
    video_id: str,
    fields: Optional[List[str]] = None
) -> VideoData:
    pass

def process_batch(
    videos: List[VideoData],
    config: Dict[str, Any]
) -> Dict[str, Union[ProcessedVideo, Error]]:
    pass

# Use TypedDict for complex dictionaries
from typing import TypedDict

class VideoMetadata(TypedDict, total=False):
    title: str
    description: str
    tags: List[str]
    category_id: str
```

#### Docstrings

Use Google-style docstrings:

```python
def fetch_analytics(
    channel_id: str,
    start_date: date,
    end_date: date,
    metrics: List[str]
) -> AnalyticsData:
    """
    Fetch analytics data for a channel.
    
    Args:
        channel_id: The YouTube channel ID
        start_date: Start date for analytics period
        end_date: End date for analytics period
        metrics: List of metrics to fetch (views, watchTime, etc.)
    
    Returns:
        AnalyticsData: The fetched analytics data
    
    Raises:
        APIError: If the API request fails
        ValueError: If date range is invalid
    
    Example:
        >>> analytics = await fetch_analytics(
        ...     "UC123456",
        ...     date(2026, 1, 1),
        ...     date(2026, 3, 1),
        ...     ["views", "watchTimeMinutes"]
        ... )
    """
    pass
```

#### Naming Conventions

```python
# Classes: PascalCase
class VideoProcessor:
    pass

# Functions/Methods: snake_case
def process_video():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30.0

# Private members: leading underscore
_internal_cache = {}

# Module-private: double underscore (name mangling)
class _InternalClass:
    __private_attr = None

# Type variables: Capitalized single letters or descriptive names
T = TypeVar("T")
VideoT = TypeVar("VideoT", bound="VideoData")
```

#### Async Code Standards

```python
# Always use async/await for I/O operations
async def fetch_data(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

# Use asyncio.gather for concurrent operations
async def fetch_all(video_ids: List[str]) -> List[VideoData]:
    tasks = [fetch_video(vid) for vid in video_ids]
    return await asyncio.gather(*tasks)

# Use async context managers
async def process_with_lock(lock: asyncio.Lock):
    async with lock:
        # Critical section
        pass

# Proper exception handling in async
async def safe_operation():
    try:
        return await risky_operation()
    except asyncio.CancelledError:
        # Handle cancellation properly
        raise
    except Exception as e:
        logger.exception("Operation failed")
        raise
```

#### Error Handling

```python
# Use custom exceptions
from youtube_enhancement_tools.core.exceptions import (
    YouTubeEnhancementError,
    APIError,
    VideoProcessingError
)

def validate_video(video: VideoData) -> None:
    """Validate video data."""
    if not video.id:
        raise ValueError("Video ID is required")
    if not video.title:
        raise ValueError("Video title is required")

async def safe_api_call():
    """Handle API errors gracefully."""
    try:
        return await api_client.request()
    except APIError as e:
        if e.is_quota_exceeded:
            logger.warning("Quota exceeded, retrying later")
            raise QuotaExceededError from e
        elif e.is_rate_limited:
            logger.info("Rate limited, backing off")
            await asyncio.sleep(e.retry_after)
            return await safe_api_call()
        raise
```

### Linting Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "ASYNC", # flake8-async
]
ignore = [
    "E501",  # line too long (handled by Black)
]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-aiofiles
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and configuration
├── unit/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_processor.py
│   ├── test_analytics.py
│   └── test_plugins.py
├── integration/
│   ├── __init__.py
│   ├── test_api_integration.py
│   ├── test_storage_integration.py
│   └── test_database_integration.py
├── e2e/
│   ├── __init__.py
│   └── test_full_pipeline.py
└── fixtures/
    ├── sample_video.json
    ├── sample_channel.json
    └── test_files/
```

### Writing Unit Tests

```python
# tests/unit/test_client.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from youtube_enhancement_tools.client import YouTubeClient
from youtube_enhancement_tools.core.types import VideoData

class TestYouTubeClient:
    """Tests for YouTubeClient class."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return YouTubeClient(api_key="test_key")
    
    @pytest.fixture
    def sample_video_data(self):
        """Sample video data for testing."""
        return {
            "id": "test_video_id",
            "title": "Test Video",
            "channelId": "test_channel",
            # ... more fields
        }
    
    @pytest.mark.asyncio
    async def test_get_video_success(
        self,
        client: YouTubeClient,
        sample_video_data: dict
    ):
        """Test successful video fetch."""
        with patch.object(client, '_api_request') as mock_request:
            mock_request.return_value = {"items": [sample_video_data]}
            
            video = await client.get_video("test_video_id")
            
            assert isinstance(video, VideoData)
            assert video.id == "test_video_id"
            assert video.title == "Test Video"
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_video_not_found(self, client: YouTubeClient):
        """Test video not found error."""
        with patch.object(client, '_api_request') as mock_request:
            mock_request.return_value = {"items": []}
            
            with pytest.raises(VideoNotFoundError):
                await client.get_video("nonexistent_id")
    
    @pytest.mark.asyncio
    async def test_get_video_quota_exceeded(self, client: YouTubeClient):
        """Test quota exceeded error handling."""
        with patch.object(client, '_api_request') as mock_request:
            mock_request.side_effect = APIError(
                "Quota exceeded",
                error_code="quotaExceeded"
            )
            
            with pytest.raises(QuotaExceededError):
                await client.get_video("test_id")
    
    @pytest.mark.asyncio
    async def test_get_videos_batching(self, client: YouTubeClient):
        """Test batch video fetching."""
        video_ids = [f"video_{i}" for i in range(100)]
        
        with patch.object(client, '_api_request') as mock_request:
            mock_request.return_value = {"items": []}
            
            await client.get_videos(video_ids, batch_size=50)
            
            # Should make 2 API calls (100 videos / 50 batch size)
            assert mock_request.call_count == 2
```

### Writing Integration Tests

```python
# tests/integration/test_api_integration.py
import pytest
from youtube_enhancement_tools import YouTubeClient

@pytest.mark.integration
@pytest.mark.asyncio
class TestAPIIntegration:
    """Integration tests requiring API access."""
    
    @pytest.fixture
    async def client(self):
        """Create real client for integration tests."""
        client = YouTubeClient(api_key=os.environ.get("TEST_YOUTUBE_API_KEY"))
        yield client
        await client.close()
    
    async def test_real_video_fetch(self, client: YouTubeClient):
        """Test fetching a real video."""
        # Use a well-known video ID
        video = await client.get_video("dQw4w9WgXcQ")
        
        assert video is not None
        assert video.id == "dQw4w9WgXcQ"
        assert video.title  # Should have a title
    
    async def test_channel_videos_pagination(self, client: YouTubeClient):
        """Test channel video pagination."""
        channel_id = "UCuAXFkgsw1L7xaCfnd5JJOw"
        
        videos = []
        async for video in client.get_channel_videos(
            channel_id,
            max_results=100
        ):
            videos.append(video)
        
        assert len(videos) > 0
        assert all(v.channel_id == channel_id for v in videos)
```

### Writing End-to-End Tests

```python
# tests/e2e/test_full_pipeline.py
import pytest
from pathlib import Path
from youtube_enhancement_tools import (
    YouTubeClient,
    VideoProcessor,
    AnalyticsEngine
)

@pytest.mark.e2e
@pytest.mark.asyncio
class TestFullPipeline:
    """End-to-end tests for complete workflows."""
    
    @pytest.fixture
    def test_config(self, tmp_path: Path):
        """Create test configuration."""
        from youtube_enhancement_tools.config import Config
        
        return Config(
            youtube_api_key=os.environ.get("TEST_YOUTUBE_API_KEY"),
            database_url=f"sqlite:///{tmp_path}/test.db",
            redis_url="redis://localhost:6379",
            storage_provider="local",
            storage_path=str(tmp_path / "storage")
        )
    
    async def test_video_download_and_process(
        self,
        test_config
    ):
        """Test complete video download and processing pipeline."""
        client = YouTubeClient(api_key=test_config.youtube_api_key)
        processor = VideoProcessor(config=test_config)
        
        try:
            # Fetch video
            video = await client.get_video("test_video_id")
            
            # Download video
            video_path = await processor.download(video)
            assert video_path.exists()
            
            # Process video
            result = await processor.process(video)
            assert result.success
            
            # Verify output
            assert result.output_path.exists()
            
        finally:
            await client.close()
            await processor.cleanup()
```

### Fixtures and Mocks

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

@pytest.fixture
def sample_video_dict():
    """Return sample video data dictionary."""
    return {
        "kind": "youtube#video",
        "id": "test_video_id",
        "snippet": {
            "title": "Test Video Title",
            "description": "Test description",
            "channelId": "UC_test_channel",
            "channelTitle": "Test Channel",
            "publishedAt": "2026-01-01T00:00:00Z",
            "thumbnails": {
                "default": {"url": "http://example.com/thumb.jpg"}
            }
        },
        "contentDetails": {
            "duration": "PT3M30S",
            "definition": "hd"
        },
        "statistics": {
            "viewCount": "1000000",
            "likeCount": "50000"
        }
    }

@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client

@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    return redis

@pytest.fixture
def temp_video_file(tmp_path: Path):
    """Create a temporary video file for testing."""
    video_path = tmp_path / "test_video.mp4"
    video_path.write_bytes(b"fake video content")
    return video_path

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_client.py -v

# Run specific test class
pytest tests/unit/test_client.py::TestYouTubeClient -v

# Run specific test
pytest tests/unit/test_client.py::TestYouTubeClient::test_get_video_success -v

# Run with coverage
pytest tests/ --cov=youtube_enhancement_tools --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests (requires API key)
pytest tests/integration/ -v -m integration

# Run with parallel execution
pytest tests/ -n auto

# Run with timeout
pytest tests/ --timeout=60

# Run failed tests only
pytest tests/ --lf
```

### Test Configuration

```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests (requires external services)
    e2e: End-to-end tests
    slow: Slow running tests
addopts = 
    -v
    --tb=short
    --strict-markers
    -ra
filterwarnings =
    ignore::DeprecationWarning
```

---

## Debugging Guide

### Debugging Tools

#### Using pdb (Python Debugger)

```python
# Insert breakpoint
def process_video(video):
    import pdb; pdb.set_trace()  # Traditional breakpoint
    # Or in Python 3.7+
    breakpoint()  # Modern breakpoint
    
    result = transform(video)
    return result

# Common pdb commands:
# n (next) - Execute next line
# s (step) - Step into function
# c (continue) - Continue execution
# l (list) - Show code context
# p expr (print) - Print expression
# w (where) - Show stack trace
# q (quit) - Quit debugger
```

#### Using VS Code Debugger

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "YOUTUBE_ENH_LOG_LEVEL": "DEBUG"
            }
        },
        {
            "name": "Python: Module",
            "type": "python",
            "request": "launch",
            "module": "youtube_enhancement_tools.cli",
            "args": ["process", "video_id"],
            "console": "integratedTerminal"
        },
        {
            "name": "Python: pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${file}", "-v", "-s"],
            "console": "integratedTerminal"
        }
    ]
}
```

#### Async Debugging

```python
import asyncio
import aiodebug

# Enable async debugging
aiodebug.log_slow_callbacks(enable=True)

# Debug async code
async def debug_async():
    task = asyncio.create_task(some_async_function())
    
    # Inspect task state
    print(f"Task done: {task.done()}")
    print(f"Task cancelled: {task.cancelled()}")
    
    # Wait with timeout for debugging
    try:
        result = await asyncio.wait_for(task, timeout=5.0)
    except asyncio.TimeoutError:
        print("Task timed out!")
        task.cancel()
```

### Logging for Debugging

```python
import logging
from youtube_enhancement_tools.utils import Logger

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = Logger("debug_module", level="DEBUG")

# Structured logging for debugging
logger.debug(
    "Processing video",
    extra={
        "video_id": "abc123",
        "stage": "download",
        "attempt": 1,
        "context": {"size": "100MB", "format": "mp4"}
    }
)
```

### Profiling

```python
# CPU Profiling
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    process_videos()
    
    profiler.disable()
    
    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

# Memory Profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    data = []
    for i in range(10000):
        data.append({"id": i, "data": "x" * 1000})
    return data

# Async Profiling
import aioitertools
from pyinstrument import Profiler

async def profile_async():
    profiler = Profiler()
    profiler.start()
    
    await process_all_videos()
    
    profiler.stop()
    print(profiler.output_text())
```

### Common Issues and Solutions

#### Issue: Async Function Not Awaited

```python
# Problem
async def process():
    result = some_async_function()  # Missing await!
    return result

# Solution
async def process():
    result = await some_async_function()
    return result

# Detection
# Enable warnings
python -W default::RuntimeWarning your_script.py
```

#### Issue: Event Loop Closed

```python
# Problem
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
# Later...
asyncio.run(other_function())  # Error: Event loop is closed

# Solution
# Use asyncio.run() for entry point
asyncio.run(main())

# Or reuse the same loop
async def main():
    await function1()
    await function2()

asyncio.run(main())
```

#### Issue: Resource Not Cleaned Up

```python
# Problem
async def fetch():
    session = aiohttp.ClientSession()
    response = await session.get(url)
    # Session not closed!

# Solution - Use context manager
async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Or explicit cleanup
async def fetch():
    session = aiohttp.ClientSession()
    try:
        response = await session.get(url)
        return await response.text()
    finally:
        await session.close()
```

---

## Contributing Guidelines

### Contribution Workflow

```
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Run linting and tests
6. Submit a pull request
7. Address review feedback
8. Merge after approval
```

### Branch Naming

```bash
# Feature branches
git checkout -b feature/add-new-processor
git checkout -b feature/video-watermark-support

# Bug fix branches
git checkout -b fix/quota-handling
git checkout -b fix/async-timeout-issue

# Documentation branches
git checkout -b docs/update-api-reference
git checkout -b docs/add-plugin-guide

# Release branches
git checkout -b release/v3.2.0
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org):

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, etc.) |
| `refactor` | Code refactoring |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

#### Examples

```bash
# Good commit messages
git commit -m "feat(processor): add watermark support for videos"
git commit -m "fix(client): handle quota exceeded errors gracefully"
git commit -m "docs(api): update YouTubeClient documentation"
git commit -m "refactor(analytics): simplify metrics calculation"
git commit -m "test(client): add unit tests for rate limiter"

# Commit with body
git commit -m "feat(plugins): add hook system for video processing

- Add pre_process and post_process hooks
- Support hook priorities
- Add filter chain support

Closes #123"
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code
- [ ] I have updated documentation
- [ ] I have added tests
- [ ] All tests pass
- [ ] No new warnings

## Related Issues
Closes #123
```

### Code Review Process

1. **Automated Checks**: All CI checks must pass
2. **First Review**: Core team member reviews within 48 hours
3. **Changes**: Address all review feedback
4. **Approval**: Requires at least 2 approvals for merge
5. **Merge**: Squash and merge to main branch

---

## Code Review Checklist

### Functionality

- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] No logic errors or bugs
- [ ] Performance is acceptable

### Code Quality

- [ ] Follows coding standards
- [ ] Type hints are complete
- [ ] Docstrings are present and accurate
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Functions are focused and not too long
- [ ] Variable names are descriptive

### Testing

- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests cover error conditions
- [ ] Tests are independent and repeatable
- [ ] No test duplication

### Security

- [ ] Input validation is present
- [ ] No hardcoded credentials
- [ ] Sensitive data is handled securely
- [ ] No SQL injection vulnerabilities
- [ ] Authentication/authorization is correct

### Documentation

- [ ] Code is self-documenting where possible
- [ ] Complex logic is commented
- [ ] API documentation is updated
- [ ] README is updated if needed
- [ ] Changelog is updated

### Async Best Practices

- [ ] Async functions are properly awaited
- [ ] Resources are properly cleaned up
- [ ] Timeouts are set for external calls
- [ ] Concurrency is controlled
- [ ] No blocking calls in async code

---

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org):

```
MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)
```

### Release Checklist

```markdown
## Pre-Release

- [ ] All tests pass
- [ ] Code coverage >= 90%
- [ ] No outstanding critical bugs
- [ ] Documentation is up to date
- [ ] Changelog is updated
- [ ] Version number is updated
- [ ] Dependencies are up to date

## Release

- [ ] Create release branch
- [ ] Run final tests
- [ ] Build distribution packages
- [ ] Tag release
- [ ] Publish to PyPI
- [ ] Create GitHub release
- [ ] Update documentation

## Post-Release

- [ ] Monitor for issues
- [ ] Update website/download links
- [ ] Announce release
- [ ] Merge release branch to main
```

### Release Commands

```bash
# Update version
# Edit youtube_enhancement_tools/__version__.py
__version__ = "3.2.0"

# Update changelog
# Edit CHANGELOG.md

# Create and tag release
git checkout -b release/v3.2.0
git add .
git commit -m "chore: release version 3.2.0"
git tag -a v3.2.0 -m "Release version 3.2.0"

# Build distribution
python -m build

# Test installation
pip install dist/youtube_enhancement_tools-3.2.0.tar.gz

# Publish to PyPI
python -m twine upload dist/*

# Push to GitHub
git push origin release/v3.2.0
git push origin v3.2.0
```

### Changelog Format

```markdown
## [3.2.0] - 2026-03-04

### Added
- New plugin hook system for video processing
- Support for H.265 video encoding
- Redis cluster support for caching

### Changed
- Improved async performance by 30%
- Updated YouTube API client with retry logic

### Fixed
- Fixed memory leak in video processor
- Fixed race condition in plugin loader

### Deprecated
- Deprecated `VideoProcessor.sync_process()` method

### Removed
- Removed Python 3.9 support

### Security
- Fixed potential XSS in web interface
```

---

*Documentation generated for YouTube Enhancement Tools v3.2.0*
*Last updated: March 4, 2026*
