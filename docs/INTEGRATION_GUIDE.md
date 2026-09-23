# YouTube Enhancement Tools v3.2.0 - Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [YouTube API Integration](#youtube-api-integration)
3. [OAuth Setup](#oauth-setup)
4. [Cloud Storage Integration](#cloud-storage-integration)
5. [Database Integration](#database-integration)
6. [Cache Integration](#cache-integration)
7. [Queue Integration](#queue-integration)
8. [Webhook Configuration](#webhook-configuration)
9. [Third-Party Services](#third-party-services)
10. [Custom Integrations](#custom-integrations)

---

## Overview

YouTube Enhancement Tools v3.2.0 supports integration with various external services to extend functionality. This guide covers setup and configuration for all supported integrations.

### Integration Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      YouTube Enhancement Tools                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   YouTube   │  │   Cloud     │  │  Database   │  │    Cache    │    │
│  │     API     │  │   Storage   │  │   Service   │  │   Service   │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         ▼                ▼                ▼                ▼            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Google     │  │  AWS S3     │  │   SQLite    │  │    Redis    │    │
│  │  Cloud      │  │  GCS        │  │ PostgreSQL  │  │   Memcached │    │
│  │  Platform   │  │  Azure      │  │    MySQL    │  │             │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Queue     │  │  Webhook    │  │  Analytics  │  │   Auth      │    │
│  │   Service   │  │  Service    │  │  Services   │  │  Providers  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │            │
│         ▼                ▼                ▼                ▼            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Celery    │  │  Discord    │  │  Google     │  │    OAuth    │    │
│  │   RabbitMQ  │  │   Slack     │  │  Analytics  │  │    JWT      │    │
│  │    Redis    │  │  Custom     │  │  Mixpanel   │  │   SAML      │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## YouTube API Integration

### Prerequisites

1. Google Cloud Platform account
2. YouTube Data API v3 enabled
3. YouTube Analytics API enabled (for analytics features)

### Step 1: Create Google Cloud Project

```bash
# 1. Go to Google Cloud Console
# https://console.cloud.google.com/

# 2. Create a new project or select existing
# Project Name: youtube-enhancement-tools

# 3. Note your Project ID
# Example: youtube-enhancement-12345
```

### Step 2: Enable Required APIs

```bash
# In Google Cloud Console:
# APIs & Services > Library

# Enable these APIs:
1. YouTube Data API v3
2. YouTube Analytics API
3. OAuth 2.0 API (for user authentication)
```

### Step 3: Create API Credentials

#### API Key (for public data)

```bash
# APIs & Services > Credentials > Create Credentials > API Key

# Restrict your API key:
# - HTTP referrers (for web apps)
# - IP addresses (for server apps)
# - API restrictions: YouTube Data API v3 only
```

#### OAuth 2.0 Client ID (for user data)

```bash
# APIs & Services > Credentials > Create Credentials > OAuth Client ID

# Application type: Web application
# Authorized redirect URIs:
# - http://localhost:8080/callback (development)
# - https://yourdomain.com/callback (production)

# Note your:
# - Client ID
# - Client Secret
```

### Step 4: Configure Application

```bash
# .env file
YOUTUBE_ENH_YOUTUBE_API_KEY=AIzaSy...your_api_key
YOUTUBE_ENH_YOUTUBE_CLIENT_ID=123456...apps.googleusercontent.com
YOUTUBE_ENH_YOUTUBE_CLIENT_SECRET=GOCSPX-...your_secret

# config.yaml
youtube:
  api_key: ${YOUTUBE_ENH_YOUTUBE_API_KEY}
  client_id: ${YOUTUBE_ENH_YOUTUBE_CLIENT_ID}
  client_secret: ${YOUTUBE_ENH_YOUTUBE_CLIENT_SECRET}
  redirect_uri: http://localhost:8080/callback
  scopes:
    - https://www.googleapis.com/auth/youtube
    - https://www.googleapis.com/auth/youtube.analytics.readonly
```

### Step 5: Test Connection

```python
from youtube_enhancement_tools import YouTubeClient

async def test_connection():
    client = YouTubeClient(api_key="YOUR_API_KEY")
    
    try:
        # Test basic API call
        video = await client.get_video("dQw4w9WgXcQ")
        print(f"Connected! Video: {video.title}")
        
        # Check quota
        quota = await client.get_quota_usage()
        print(f"Quota: {quota.used}/{quota.total}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await client.close()
```

### API Quota Management

```python
from youtube_enhancement_tools.client import RateLimiter

# Configure rate limiter
limiter = RateLimiter(
    quota_limit=10000,  # Daily quota
    requests_per_second=5
)

# Use with client
async with limiter:
    video = await client.get_video("video_id")

# Monitor quota usage
async def check_quota():
    usage = await client.get_quota_usage()
    
    if usage.percent_used > 80:
        print(f"Warning: {usage.percent_used}% quota used")
    
    if usage.remaining < 100:
        print("Critical: Low quota remaining")
```

### Quota Costs Reference

| Operation | Quota Cost |
|-----------|------------|
| `videos.list` | 1 |
| `channels.list` | 1 |
| `search.list` | 100 |
| `playlistItems.list` | 1 |
| `commentThreads.list` | 1 |
| `videos.insert` (upload) | 1600 |
| `analytics.reports.get` | 10 |

---

## OAuth Setup

### OAuth Flow Implementation

```python
from youtube_enhancement_tools.client import OAuthClient

class OAuthHandler:
    """Handle OAuth 2.0 flow for YouTube API."""
    
    def __init__(self, config):
        self.oauth = OAuthClient(
            client_id=config.youtube_client_id,
            client_secret=config.youtube_client_secret,
            redirect_uri=config.redirect_uri,
            scopes=[
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.analytics.readonly",
                "https://www.googleapis.com/auth/youtube.upload"
            ]
        )
        self.token_store = TokenStore()
    
    def get_authorization_url(self) -> str:
        """Get URL for user authorization."""
        state = self._generate_state()
        return self.oauth.get_authorization_url(state=state)
    
    async def handle_callback(self, code: str, state: str) -> TokenData:
        """Handle OAuth callback."""
        # Verify state
        if not self._verify_state(state):
            raise ValueError("Invalid state parameter")
        
        # Exchange code for tokens
        tokens = await self.oauth.exchange_code(code)
        
        # Store tokens securely
        await self.token_store.save(tokens)
        
        return tokens
    
    async def refresh_tokens(self) -> TokenData:
        """Refresh access token."""
        refresh_token = await self.token_store.get_refresh_token()
        new_tokens = await self.oauth.refresh_token(refresh_token)
        await self.token_store.save(new_tokens)
        return new_tokens
    
    def _generate_state(self) -> str:
        """Generate CSRF protection state."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _verify_state(self, state: str) -> bool:
        """Verify state parameter."""
        # Implement state verification
        pass
```

### Token Storage

```python
from cryptography.fernet import Fernet
import json
from pathlib import Path

class TokenStore:
    """Secure token storage."""
    
    def __init__(self, storage_path: Path, encryption_key: bytes):
        self.storage_path = storage_path
        self.cipher = Fernet(encryption_key)
    
    async def save(self, tokens: TokenData) -> None:
        """Save tokens securely."""
        data = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_at": tokens.expires_at.isoformat(),
            "scope": tokens.scope
        }
        
        # Encrypt and save
        encrypted = self.cipher.encrypt(json.dumps(data).encode())
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_bytes(encrypted)
    
    async def get_access_token(self) -> str:
        """Get valid access token."""
        data = await self._load()
        
        if datetime.fromisoformat(data["expires_at"]) < datetime.utcnow():
            raise TokenExpiredError()
        
        return data["access_token"]
    
    async def get_refresh_token(self) -> str:
        """Get refresh token."""
        data = await self._load()
        return data["refresh_token"]
    
    async def _load(self) -> dict:
        """Load and decrypt tokens."""
        encrypted = self.storage_path.read_bytes()
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted)
```

### OAuth Configuration

```yaml
# config/oauth.yaml
oauth:
  provider: google
  client_id: ${GOOGLE_CLIENT_ID}
  client_secret: ${GOOGLE_CLIENT_SECRET}
  redirect_uri: http://localhost:8080/callback
  
  scopes:
    - youtube
    - youtube.analytics.readonly
    - youtube.upload
  
  token_storage:
    type: file  # file, database, redis
    path: ./tokens/oauth_tokens.enc
    encryption_key: ${TOKEN_ENCRYPTION_KEY}
  
  refresh:
    enabled: true
    threshold_seconds: 300  # Refresh 5 minutes before expiry
```

---

## Cloud Storage Integration

### AWS S3 Integration

#### Prerequisites

```bash
# AWS CLI installed
aws --version

# AWS credentials configured
aws configure
```

#### Configuration

```bash
# .env file
YOUTUBE_ENH_STORAGE_PROVIDER=s3
YOUTUBE_ENH_AWS_ACCESS_KEY_ID=AKIA...
YOUTUBE_ENH_AWS_SECRET_ACCESS_KEY=...
YOUTUBE_ENH_AWS_REGION=us-east-1
YOUTUBE_ENH_S3_BUCKET=youtube-enhancement-storage
```

```yaml
# config/storage.yaml
storage:
  provider: s3
  
  s3:
    access_key_id: ${AWS_ACCESS_KEY_ID}
    secret_access_key: ${AWS_SECRET_ACCESS_KEY}
    region: us-east-1
    bucket: youtube-enhancement-storage
    
    # Optional settings
    endpoint_url: null  # For S3-compatible services
    use_ssl: true
    verify_ssl: true
    
    # Upload settings
    multipart_threshold: 8MB
    multipart_chunksize: 8MB
    max_concurrency: 10
    
    # ACL settings
    default_acl: private
    public_read_bucket: youtube-enhancement-public
```

#### Usage

```python
from youtube_enhancement_tools.storage import StorageService

async def s3_example():
    storage = StorageService(config)
    
    # Upload file
    remote_path = await storage.upload(
        local_path=Path("video.mp4"),
        remote_path="videos/2026/03/video.mp4",
        metadata={"content_type": "video/mp4"}
    )
    
    # Get presigned URL (valid for 1 hour)
    url = await storage.get_url(
        remote_path="videos/2026/03/video.mp4",
        expires_in=3600
    )
    
    # Download file
    await storage.download(
        remote_path="videos/2026/03/video.mp4",
        local_path=Path("downloaded.mp4")
    )
    
    # List files
    files = await storage.list_files(prefix="videos/2026/")
    for f in files:
        print(f"{f.key}: {f.size} bytes")
```

### Google Cloud Storage Integration

#### Prerequisites

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Create bucket
gsutil mb gs://youtube-enhancement-storage
```

#### Configuration

```bash
# .env file
YOUTUBE_ENH_STORAGE_PROVIDER=gcs
YOUTUBE_ENH_GCS_PROJECT_ID=your-project-id
YOUTUBE_ENH_GCS_BUCKET=youtube-enhancement-storage
YOUTUBE_ENH_GCS_CREDENTIALS=/path/to/service-account.json
```

```yaml
# config/storage.yaml
storage:
  provider: gcs
  
  gcs:
    project_id: ${GCS_PROJECT_ID}
    bucket: youtube-enhancement-storage
    credentials_path: ${GCS_CREDENTIALS}
    
    # Optional
    location: US
    storage_class: STANDARD
```

#### Usage

```python
from youtube_enhancement_tools.storage import StorageService

async def gcs_example():
    storage = StorageService(config)
    
    # Upload with GCS-specific metadata
    await storage.upload(
        local_path=Path("video.mp4"),
        remote_path="videos/video.mp4",
        metadata={
            "content_type": "video/mp4",
            "custom_metadata": {
                "video_id": "abc123",
                "processed_by": "youtube-enh"
            }
        }
    )
    
    # Get signed URL
    url = await storage.get_url(
        remote_path="videos/video.mp4",
        expires_in=3600
    )
```

### Azure Blob Storage Integration

#### Prerequisites

```bash
# Azure CLI installed
az --version

# Login to Azure
az login

# Create storage account
az storage account create \
  --name ytenhancement \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_LRS

# Create container
az storage container create \
  --name videos \
  --account-name ytenhancement
```

#### Configuration

```bash
# .env file
YOUTUBE_ENH_STORAGE_PROVIDER=azure
YOUTUBE_ENH_AZURE_ACCOUNT_NAME=ytenhancement
YOUTUBE_ENH_AZURE_ACCOUNT_KEY=...
YOUTUBE_ENH_AZURE_CONTAINER=videos
YOUTUBE_ENH_AZURE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
```

```yaml
# config/storage.yaml
storage:
  provider: azure
  
  azure:
    account_name: ${AZURE_ACCOUNT_NAME}
    account_key: ${AZURE_ACCOUNT_KEY}
    container: videos
    connection_string: ${AZURE_CONNECTION_STRING}
    
    # Optional
    blob_tier: Hot
    public_access: none
```

### Multi-Provider Setup

```yaml
# config/storage.yaml
storage:
  # Primary provider
  primary: s3
  
  # Fallback provider
  fallback: gcs
  
  # Provider-specific configs
  providers:
    s3:
      bucket: primary-bucket
      region: us-east-1
    
    gcs:
      bucket: backup-bucket
      project_id: my-project
    
    azure:
      container: backup-container
      account_name: backupaccount
  
  # Replication settings
  replication:
    enabled: true
    sync_on_upload: true
    verify_checksum: true
```

```python
from youtube_enhancement_tools.storage import MultiProviderStorage

async def multi_provider_example():
    storage = MultiProviderStorage(config)
    
    # Upload to primary, replicate to fallback
    await storage.upload(
        local_path=Path("video.mp4"),
        remote_path="videos/video.mp4"
    )
    
    # Read from primary
    data = await storage.download("videos/video.mp4")
    
    # Failover to fallback if primary unavailable
    storage.use_fallback = True
    data = await storage.download("videos/video.mp4")
```

---

## Database Integration

### SQLite (Default)

```yaml
# config/database.yaml
database:
  provider: sqlite
  url: sqlite:///youtube_enhancement.db
  
  # SQLite-specific settings
  pragmas:
    journal_mode: WAL
    synchronous: NORMAL
    cache_size: 10000
  
  pool:
    enabled: false  # SQLite doesn't need pooling
```

### PostgreSQL

#### Prerequisites

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE youtube_enhancement;
CREATE USER youtube_enh_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE youtube_enhancement TO youtube_enh_user;
```

#### Configuration

```bash
# .env file
YOUTUBE_ENH_DATABASE_PROVIDER=postgresql
YOUTUBE_ENH_DATABASE_URL=postgresql://youtube_enh_user:secure_password@localhost:5432/youtube_enhancement
YOUTUBE_ENH_DATABASE_POOL_SIZE=10
YOUTUBE_ENH_DATABASE_MAX_OVERFLOW=20
```

```yaml
# config/database.yaml
database:
  provider: postgresql
  url: ${DATABASE_URL}
  
  # Connection pool settings
  pool:
    size: 10
    max_overflow: 20
    pool_timeout: 30
    pool_recycle: 1800
  
  # SSL settings
  ssl:
    enabled: true
    ca_cert: /path/to/ca-cert.pem
    verify_mode: require
  
  # Performance settings
  settings:
    statement_timeout: 30000  # 30 seconds
    idle_in_transaction_session_timeout: 60000
```

#### Usage

```python
from youtube_enhancement_tools.storage import DatabaseService

async def postgres_example():
    db = DatabaseService(config)
    
    # Save video
    video_id = await db.save_video(video_data)
    
    # Query videos
    videos = await db.query_videos(
        filters={"channel_id": "UC123"},
        limit=50,
        offset=0
    )
    
    # Custom query
    async with db.get_connection() as conn:
        result = await conn.execute(
            "SELECT COUNT(*) FROM videos WHERE created_at > $1",
            datetime.utcnow() - timedelta(days=7)
        )
        count = result.scalar()
```

### MySQL/MariaDB

```bash
# .env file
YOUTUBE_ENH_DATABASE_PROVIDER=mysql
YOUTUBE_ENH_DATABASE_URL=mysql://user:password@localhost:3306/youtube_enhancement
```

```yaml
# config/database.yaml
database:
  provider: mysql
  url: ${DATABASE_URL}
  
  pool:
    size: 10
    max_overflow: 20
  
  # MySQL-specific settings
  charset: utf8mb4
  collation: utf8mb4_unicode_ci
```

### MongoDB

```bash
# .env file
YOUTUBE_ENH_DATABASE_PROVIDER=mongodb
YOUTUBE_ENH_DATABASE_URL=mongodb://localhost:27017
YOUTUBE_ENH_DATABASE_NAME=youtube_enhancement
```

```yaml
# config/database.yaml
database:
  provider: mongodb
  url: ${DATABASE_URL}
  database: youtube_enhancement
  
  # Connection settings
  connection:
    max_pool_size: 50
    min_pool_size: 10
    max_idle_time_ms: 300000
  
  # Replica set (optional)
  replica_set:
    enabled: false
    name: rs0
    read_preference: secondaryPreferred
```

### Database Migrations

```python
# migrations/001_initial.py
"""Initial database schema."""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'videos',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('duration', sa.Integer()),
        sa.Column('view_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
    )
    
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('video_id', sa.String(), sa.ForeignKey('videos.id')),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('views', sa.Integer()),
        sa.Column('watch_time_minutes', sa.Integer()),
        sa.UniqueConstraint('video_id', 'date'),
    )
    
    op.create_index('idx_videos_channel', 'videos', ['channel_id'])
    op.create_index('idx_analytics_video_date', 'analytics', ['video_id', 'date'])

def downgrade():
    op.drop_index('idx_analytics_video_date', 'analytics')
    op.drop_index('idx_videos_channel', 'videos')
    op.drop_table('analytics')
    op.drop_table('videos')
```

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision -m "add_thumbnail_table"
```

---

## Cache Integration

### Redis Integration

#### Prerequisites

```bash
# Install Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis

# Test connection
redis-cli ping  # Should return PONG
```

#### Configuration

```bash
# .env file
YOUTUBE_ENH_CACHE_PROVIDER=redis
YOUTUBE_ENH_REDIS_URL=redis://localhost:6379
YOUTUBE_ENH_REDIS_PASSWORD=  # Optional
YOUTUBE_ENH_REDIS_DB=0
```

```yaml
# config/cache.yaml
cache:
  provider: redis
  
  redis:
    url: ${REDIS_URL}
    password: ${REDIS_PASSWORD}
    db: 0
    
    # Connection pool
    pool:
      max_connections: 50
      min_idle_connections: 10
    
    # Key settings
    key_prefix: "youtube_enh:"
    default_ttl: 3600  # 1 hour
    
    # Sentinel (for HA)
    sentinel:
      enabled: false
      master_name: mymaster
      nodes:
        - host: sentinel1
          port: 26379
        - host: sentinel2
          port: 26379
    
    # Cluster (for scaling)
    cluster:
      enabled: false
      nodes:
        - host: redis1
          port: 6379
        - host: redis2
          port: 6379
```

#### Usage

```python
from youtube_enhancement_tools.cache import CacheService

async def redis_example():
    cache = CacheService(config)
    
    # Set with TTL
    await cache.set("video:abc123", video_data, ttl=3600)
    
    # Get value
    video = await cache.get("video:abc123")
    
    # Get multiple values
    videos = await cache.get_many([
        "video:abc123",
        "video:def456"
    ])
    
    # Increment counter
    count = await cache.increment("api:calls:today")
    
    # Check existence
    exists = await cache.exists("video:abc123")
    
    # Get remaining TTL
    ttl = await cache.get_ttl("video:abc123")
    
    # Delete
    await cache.delete("video:abc123")
    
    # Clear with pattern
    await cache.clear("video:*")
```

### Redis Caching Strategies

```python
from functools import wraps

def cache_video(ttl: int = 3600):
    """Decorator to cache video fetch results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, video_id: str, *args, **kwargs):
            cache_key = f"video:{video_id}"
            
            # Try cache first
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            # Fetch and cache
            result = await func(self, video_id, *args, **kwargs)
            await self.cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

class CachedYouTubeClient(YouTubeClient):
    @cache_video(ttl=3600)
    async def get_video(self, video_id: str) -> VideoData:
        return await super().get_video(video_id)
```

### Memcached Integration

```bash
# .env file
YOUTUBE_ENH_CACHE_PROVIDER=memcached
YOUTUBE_ENH_MEMCACHED_SERVERS=127.0.0.1:11211,127.0.0.1:11212
```

```yaml
# config/cache.yaml
cache:
  provider: memcached
  
  memcached:
    servers:
      - 127.0.0.1:11211
      - 127.0.0.1:11212
    
    # Connection settings
    timeout: 1
    max_connections: 10
    
    # Key settings
    key_prefix: "yt_enh:"
    default_ttl: 3600
```

### In-Memory Cache (Development)

```yaml
# config/cache.yaml
cache:
  provider: memory
  
  memory:
    max_size: 1000  # Maximum items
    default_ttl: 300  # 5 minutes
    
    # Eviction policy
    eviction: lru  # lru, lfu, fifo
```

---

## Queue Integration

### Redis Queue

```yaml
# config/queue.yaml
queue:
  provider: redis
  
  redis:
    url: ${REDIS_URL}
    
    # Queue settings
    queues:
      video_processing:
        priority: high
        max_retries: 3
        retry_delay: 60
      
      analytics:
        priority: normal
        max_retries: 2
      
      notifications:
        priority: low
        max_retries: 1
    
    # Worker settings
    workers:
      video_processing: 4
      analytics: 2
      notifications: 1
```

```python
from youtube_enhancement_tools.queue import TaskQueue, Worker

async def queue_example():
    queue = TaskQueue(config)
    
    # Enqueue task
    task_id = await queue.enqueue(
        task_name="process_video",
        kwargs={"video_id": "abc123"},
        priority=5,
        delay=0
    )
    
    # Check status
    status = await queue.get_task_status(task_id)
    print(f"Task {task_id}: {status.state}")
    
    # Cancel task
    await queue.cancel_task(task_id)
```

### Celery Integration

```python
# celery_config.py
from celery import Celery

app = Celery(
    'youtube_enhancement',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    
    # Rate limiting
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

@app.task(bind=True, max_retries=3)
def process_video_task(self, video_id: str):
    """Celery task for video processing."""
    try:
        processor = VideoProcessor(config)
        result = processor.process_sync(video_id)
        return {"success": True, "result": result}
    except Exception as e:
        self.retry(exc=e, countdown=60)

@app.task
def send_notification_task(notification_data: dict):
    """Celery task for notifications."""
    notifier = NotifierService(config)
    return notifier.send(notification_data)
```

```bash
# Start Celery worker
celery -A celery_config worker --loglevel=info --concurrency=4

# Start Celery beat (scheduled tasks)
celery -A celery_config beat --loglevel=info

# Monitor with Flower
celery -A celery_config flower --port=5555
```

### RabbitMQ Integration

```bash
# Install RabbitMQ
# Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Or native installation
# https://www.rabbitmq.com/download.html
```

```yaml
# config/queue.yaml
queue:
  provider: rabbitmq
  
  rabbitmq:
    host: localhost
    port: 5672
    username: guest
    password: guest
    virtual_host: /
    
    # Exchange settings
    exchange:
      name: youtube_enhancement
      type: topic
      durable: true
    
    # Queue settings
    queues:
      video.processing:
        durable: true
        auto_delete: false
        arguments:
          x-message-ttl: 86400000  # 24 hours
      
      video.completed:
        durable: true
        routing_key: video.completed
    
    # Consumer settings
    consumer:
      prefetch_count: 10
      ack_timeout: 30
```

---

## Webhook Configuration

### Incoming Webhooks

```yaml
# config/webhooks.yaml
webhooks:
  incoming:
    enabled: true
    port: 8080
    path: /webhooks
    
    # Authentication
    auth:
      type: signature  # signature, token, basic
      secret: ${WEBHOOK_SECRET}
    
    # Rate limiting
    rate_limit:
      requests_per_minute: 60
      burst: 10
    
    # Endpoints
    endpoints:
      - path: /youtube
        handler: youtube_webhook_handler
        events:
          - video.uploaded
          - video.processed
      
      - path: /analytics
        handler: analytics_webhook_handler
        events:
          - analytics.ready
```

```python
from youtube_enhancement_tools.utils import WebhookHandler

class YouTubeWebhookHandler(WebhookHandler):
    """Handle incoming YouTube webhooks."""
    
    async def handle(self, request: Request) -> Response:
        # Verify signature
        if not self.verify_signature(request):
            return Response(status=401)
        
        # Parse payload
        payload = await request.json()
        event_type = payload.get("type")
        data = payload.get("data")
        
        # Process based on event type
        if event_type == "video.uploaded":
            await self.handle_video_uploaded(data)
        elif event_type == "video.processed":
            await self.handle_video_processed(data)
        
        return Response(status=200)
    
    async def handle_video_uploaded(self, data: dict):
        """Handle video uploaded event."""
        video_id = data.get("video_id")
        
        # Trigger processing
        await self.queue.enqueue(
            "process_video",
            kwargs={"video_id": video_id}
        )
    
    def verify_signature(self, request: Request) -> bool:
        """Verify webhook signature."""
        signature = request.headers.get("X-Webhook-Signature")
        body = await request.body()
        
        import hmac
        import hashlib
        
        expected = hmac.new(
            self.secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, f"sha256={expected}")
```

### Outgoing Webhooks

```yaml
# config/webhooks.yaml
webhooks:
  outgoing:
    enabled: true
    
    # Destinations
    destinations:
      - name: discord
        url: ${DISCORD_WEBHOOK_URL}
        events:
          - video.processing_complete
          - video.processing_failed
        format: discord
        
      - name: slack
        url: ${SLACK_WEBHOOK_URL}
        events:
          - video.uploaded
          - analytics.ready
        format: slack
      
      - name: custom
        url: https://api.example.com/webhooks
        events:
          - "*"  # All events
        format: json
        headers:
          Authorization: Bearer ${CUSTOM_API_TOKEN}
        
        # Retry settings
        retry:
          max_attempts: 3
          backoff: exponential
          initial_delay: 1
```

```python
from youtube_enhancement_tools.utils import WebhookSender

class WebhookNotifier:
    """Send outgoing webhooks."""
    
    def __init__(self, config):
        self.config = config
        self.destinations = config.webhooks.outgoing.destinations
    
    async def notify(self, event_type: str, data: dict):
        """Send notification to all matching destinations."""
        tasks = []
        
        for dest in self.destinations:
            if self._matches_event(event_type, dest.events):
                tasks.append(self._send_to_destination(dest, event_type, data))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_to_destination(
        self,
        dest: dict,
        event_type: str,
        data: dict
    ):
        """Send to single destination."""
        import aiohttp
        
        payload = self._format_payload(dest.format, event_type, data)
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(dest.retry.max_attempts):
                try:
                    async with session.post(
                        dest.url,
                        json=payload,
                        headers=dest.get("headers", {})
                    ) as response:
                        if response.status < 400:
                            return
                except Exception as e:
                    if attempt == dest.retry.max_attempts - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _format_payload(self, format_type: str, event_type: str, data: dict):
        """Format payload for destination."""
        if format_type == "discord":
            return {
                "embeds": [{
                    "title": f"Event: {event_type}",
                    "fields": [
                        {"name": k, "value": str(v)}
                        for k, v in data.items()
                    ]
                }]
            }
        elif format_type == "slack":
            return {
                "text": f"Event: {event_type}",
                "attachments": [{
                    "fields": [
                        {"title": k, "value": str(v)}
                        for k, v in data.items()
                    ]
                }]
            }
        else:
            return {"event": event_type, "data": data}
```

---

## Third-Party Services

### Google Analytics Integration

```yaml
# config/analytics.yaml
analytics:
  providers:
    google_analytics:
      enabled: true
      measurement_id: ${GA_MEASUREMENT_ID}
      api_secret: ${GA_API_SECRET}
      
      # Event tracking
      track_events:
        - video.viewed
        - video.processed
        - video.downloaded
      
      # Custom dimensions
      custom_dimensions:
        video_id: dimension1
        channel_id: dimension2
        processing_time: dimension3
```

```python
from google_analytics_data import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

class GoogleAnalyticsIntegration:
    """Google Analytics 4 integration."""
    
    def __init__(self, config):
        self.property_id = config.ga.property_id
        self.client = BetaAnalyticsDataClient()
    
    async def track_event(self, event_name: str, params: dict):
        """Track custom event."""
        # Implementation for GA4 Measurement Protocol
        pass
    
    async def get_report(self, metrics: list, dimensions: list):
        """Get analytics report."""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[{"start_date": "7daysAgo", "end_date": "today"}]
        )
        
        response = self.client.run_report(request)
        return self._parse_response(response)
```

### Slack Integration

```yaml
# config/integrations.yaml
slack:
  enabled: true
  bot_token: ${SLACK_BOT_TOKEN}
  signing_secret: ${SLACK_SIGNING_SECRET}
  
  channels:
    notifications: "#youtube-notifications"
    errors: "#youtube-errors"
    analytics: "#youtube-analytics"
  
  # Slash commands
  commands:
    /youtube-status: youtube_status_command
    /youtube-process: youtube_process_command
```

```python
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

app = App(token=config.slack.bot_token)

@app.command("/youtube-status")
def handle_status_command(ack, say, command):
    """Handle /youtube-status slash command."""
    ack()
    
    # Get system status
    status = get_system_status()
    
    say(f"""
    *YouTube Enhancement Status*
    • API Quota: {status.quota_used}/{status.quota_total}
    • Queue Length: {status.queue_length}
    • Active Workers: {status.active_workers}
    """)

@app.event("message")
def handle_messages(event, say):
    """Handle messages."""
    if "process video" in event.get("text", "").lower():
        say("I can help with that! Use /youtube-process <video_id>")
```

### Discord Integration

```yaml
# config/integrations.yaml
discord:
  enabled: true
  bot_token: ${DISCORD_BOT_TOKEN}
  guild_id: ${DISCORD_GUILD_ID}
  
  channels:
    notifications: 123456789012345678
    logs: 123456789012345679
  
  # Bot commands
  commands:
    prefix: "!"
    commands:
      status: discord_status_command
      process: discord_process_command
```

```python
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command(name="status")
async def status_command(ctx):
    """Show system status."""
    status = get_system_status()
    
    embed = discord.Embed(
        title="YouTube Enhancement Status",
        color=discord.Color.green()
    )
    embed.add_field(name="API Quota", value=f"{status.quota_used}/{status.quota_total}")
    embed.add_field(name="Queue", value=str(status.queue_length))
    embed.add_field(name="Workers", value=str(status.active_workers))
    
    await ctx.send(embed=embed)

@bot.command(name="process")
async def process_command(ctx, video_id: str):
    """Process a video."""
    await ctx.send(f"Processing video {video_id}...")
    
    # Queue the processing task
    await queue.enqueue("process_video", kwargs={"video_id": video_id})
```

---

## Custom Integrations

### Creating Custom Integration Module

```python
# youtube_enhancement_tools/integrations/custom_service.py
"""Custom service integration module."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import aiohttp


class BaseIntegration(ABC):
    """Base class for custom integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to service."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check service health."""
        pass


class CustomServiceIntegration(BaseIntegration):
    """Example custom service integration."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
    
    async def connect(self) -> bool:
        """Connect to custom service."""
        try:
            async with self._session.get(
                f"{self.base_url}/health",
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from service."""
        pass
    
    async def health_check(self) -> bool:
        """Check service health."""
        return await self.connect()
    
    async def send_data(self, data: Dict[str, Any]) -> bool:
        """Send data to custom service."""
        try:
            async with self._session.post(
                f"{self.base_url}/api/data",
                json=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            ) as response:
                return response.status == 200
        except Exception as e:
            self._log_error(f"Failed to send data: {e}")
            return False
    
    async def fetch_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from custom service."""
        try:
            async with self._session.get(
                f"{self.base_url}/api/data",
                params=params,
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            self._log_error(f"Failed to fetch data: {e}")
            return {}
    
    def _log_error(self, message: str):
        """Log error message."""
        import logging
        logging.error(f"[CustomService] {message}")
```

### Integration Registry

```python
# youtube_enhancement_tools/integrations/registry.py
"""Integration registry for custom services."""

from typing import Dict, Type
from .custom_service import CustomServiceIntegration


class IntegrationRegistry:
    """Registry for integration classes."""
    
    _integrations: Dict[str, Type[BaseIntegration]] = {}
    
    @classmethod
    def register(cls, name: str, integration_class: Type[BaseIntegration]):
        """Register an integration class."""
        cls._integrations[name] = integration_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseIntegration]]:
        """Get integration class by name."""
        return cls._integrations.get(name)
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> Optional[BaseIntegration]:
        """Create integration instance."""
        integration_class = cls.get(name)
        if integration_class:
            return integration_class(config)
        return None


# Register built-in integrations
IntegrationRegistry.register("custom_service", CustomServiceIntegration)
```

### Usage Example

```python
from youtube_enhancement_tools.integrations import IntegrationRegistry

async def use_custom_integration():
    """Use custom integration."""
    config = {
        "base_url": "https://api.custom-service.com",
        "api_key": "your_api_key"
    }
    
    async with IntegrationRegistry.create("custom_service", config) as integration:
        if await integration.connect():
            # Send data
            await integration.send_data({"video_id": "abc123"})
            
            # Fetch data
            data = await integration.fetch_data({"id": "abc123"})
        else:
            print("Failed to connect to custom service")
```

---

## Troubleshooting

### Common Issues

#### YouTube API Connection Failed

```bash
# Check API key
echo $YOUTUBE_ENH_YOUTUBE_API_KEY

# Test API directly
curl "https://www.googleapis.com/youtube/v3/videos?id=dQw4w9WgXcQ&key=$YOUTUBE_ENH_YOUTUBE_API_KEY&part=snippet"

# Check quota
# Google Cloud Console > APIs & Services > Dashboard
```

#### Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# Check connection string
echo $YOUTUBE_ENH_REDIS_URL

# Test connection
python -c "import redis; r = redis.from_url('$YOUTUBE_ENH_REDIS_URL'); print(r.ping())"
```

#### Database Connection Failed

```bash
# PostgreSQL
psql $YOUTUBE_ENH_DATABASE_URL -c "SELECT 1"

# MySQL
mysql $YOUTUBE_ENH_DATABASE_URL -e "SELECT 1"

# Check pool settings
# May need to increase pool size or timeout
```

### Debug Mode

```yaml
# config/debug.yaml
debug:
  enabled: true
  
  # Logging
  logging:
    level: DEBUG
    format: detailed
    include_body: true
  
  # Request tracing
  tracing:
    enabled: true
    sample_rate: 1.0  # 100% sampling
  
  # Integration debugging
  integrations:
    log_requests: true
    log_responses: true
    log_headers: true
```

---

*Documentation generated for YouTube Enhancement Tools v3.2.0*
*Last updated: March 4, 2026*
