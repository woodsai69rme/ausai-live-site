# YouTube Enhancement Tools v3.2.0 - Security Guide

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [Input Validation](#input-validation)
3. [Authentication & Authorization](#authentication--authorization)
4. [Encryption](#encryption)
5. [Audit Logging](#audit-logging)
6. [Security Best Practices](#security-best-practices)
7. [Threat Model](#threat-model)
8. [Incident Response](#incident-response)

---

## Security Architecture

### Security Overview

YouTube Enhancement Tools v3.2.0 implements defense-in-depth security with multiple layers of protection:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        SECURITY ARCHITECTURE                              │
└──────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                      PERIMETER SECURITY                              │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │     WAF     │  │   DDoS      │  │    TLS      │                 │
  │  │   (Rules)   │  │ Protection  │  │  1.3 Only   │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      APPLICATION SECURITY                            │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │   Input     │  │    Auth     │  │   Session   │                 │
  │  │ Validation  │  │   & AuthZ   │  │  Management │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │     CSRF    │  │    Rate     │  │    Audit    │                 │
  │  │ Protection  │  │  Limiting   │  │   Logging   │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                        DATA SECURITY                                 │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │ Encryption  │  │    Key      │  │   Secret    │                 │
  │  │  at Rest    │  │ Management  │  │  Storage    │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │    Data     │  │   Backup    │  │   Access    │                 │
  │  │  Masking    │  │ Encryption  │  │  Control    │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  └─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     INFRASTRUCTURE SECURITY                          │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
  │  │   Network   │  │    Host     │  │  Container  │                 │
  │  │ Segmentation│  │   Hardening │  │   Security  │                 │
  │  └─────────────┘  └─────────────┘  └─────────────┘                 │
  └─────────────────────────────────────────────────────────────────────┘
```

### Security Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Least Privilege** | Grant minimum necessary permissions | Role-based access control |
| **Defense in Depth** | Multiple security layers | Perimeter, app, data security |
| **Secure by Default** | Safe defaults out of the box | HTTPS required, auth enabled |
| **Fail Secure** | Errors don't expose sensitive data | Generic error messages |
| **Zero Trust** | Never trust, always verify | Verify all inputs and requests |

---

## Input Validation

### Validation Framework

```python
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field, ValidationError
from enum import Enum
import re

class VideoId(BaseModel):
    """Validated YouTube video ID."""
    value: str = Field(
        ...,
        min_length=11,
        max_length=11,
        regex=r'^[a-zA-Z0-9_-]+$'
    )
    
    @validator('value')
    def validate_video_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', v):
            raise ValueError('Invalid video ID format')
        return v


class ChannelId(BaseModel):
    """Validated YouTube channel ID."""
    value: str = Field(
        ...,
        regex=r'^UC[a-zA-Z0-9_-]{22}$'
    )
    
    @validator('value')
    def validate_channel_id(cls, v):
        if not v.startswith('UC'):
            raise ValueError('Channel ID must start with UC')
        if len(v) != 24:
            raise ValueError('Channel ID must be 24 characters')
        return v


class VideoQuality(Enum):
    """Valid video quality options."""
    HD_4K = "2160p"
    HD_1080 = "1080p"
    HD_720 = "720p"
    SD_480 = "480p"
    SD_360 = "360p"


class ProcessRequest(BaseModel):
    """Validated video processing request."""
    video_id: VideoId
    quality: VideoQuality = VideoQuality.HD_1080
    format: str = Field(default="mp4", regex=r'^(mp4|webm|mkv)$')
    watermark_enabled: bool = False
    trim_start: Optional[float] = Field(default=None, ge=0)
    trim_end: Optional[float] = Field(default=None, ge=0)
    
    @validator('trim_end')
    def validate_trim_range(cls, v, values):
        if v is not None and values.get('trim_start') is not None:
            if v <= values['trim_start']:
                raise ValueError('trim_end must be greater than trim_start')
        return v


class InputValidator:
    """Centralized input validation."""
    
    # Sanitization patterns
    HTML_PATTERN = re.compile(r'<[^>]*>')
    SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)",
        re.IGNORECASE
    )
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not value:
            return ""
        
        # Remove scripts
        value = cls.SCRIPT_PATTERN.sub('', value)
        
        # Remove HTML tags
        value = cls.HTML_PATTERN.sub('', value)
        
        # Trim whitespace
        value = value.strip()
        
        # Enforce max length
        return value[:max_length]
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: List[str] = None) -> str:
        """Validate URL input."""
        from urllib.parse import urlparse
        
        if allowed_schemes is None:
            allowed_schemes = ['https']
        
        parsed = urlparse(url)
        
        if parsed.scheme not in allowed_schemes:
            raise ValueError(f"URL scheme must be one of: {allowed_schemes}")
        
        if not parsed.netloc:
            raise ValueError("Invalid URL: missing domain")
        
        # Check for dangerous characters
        if any(char in url for char in ['<', '>', '"', "'", '`']):
            raise ValueError("URL contains invalid characters")
        
        return url
    
    @classmethod
    def validate_file_path(cls, path: str, allowed_base: str) -> str:
        """Validate file path to prevent directory traversal."""
        from pathlib import Path
        
        # Resolve to absolute path
        resolved = Path(path).resolve()
        base = Path(allowed_base).resolve()
        
        # Check path is within allowed base
        try:
            resolved.relative_to(base)
        except ValueError:
            raise ValueError("Path traversal detected")
        
        return str(resolved)
    
    @classmethod
    def validate_json(cls, data: str, schema: Dict) -> Dict:
        """Validate JSON against schema."""
        import json
        from jsonschema import validate, ValidationError
        
        try:
            parsed = json.loads(data)
            validate(instance=parsed, schema=schema)
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {e.message}")
```

### Request Validation Middleware

```python
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)


def validate_request(schema: type[BaseModel]):
    """Decorator to validate request data."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                # Parse request body
                body = await request.json()
                
                # Validate against schema
                validated = schema(**body)
                
                # Add validated data to request
                request.state.validated_data = validated
                
                return await func(request, *args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "validation_error", "details": e.errors()}
                )
            except ValueError as e:
                logger.warning(f"Invalid input: {e}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "invalid_input", "message": str(e)}
                )
        
        return wrapper
    return decorator


# Usage
@app.post("/api/videos/process")
@validate_request(ProcessRequest)
async def process_video(request: Request):
    data: ProcessRequest = request.state.validated_data
    
    # Process with validated data
    result = await video_processor.process(
        video_id=data.video_id.value,
        quality=data.quality.value,
        format=data.format
    )
    
    return {"success": True, "result": result}
```

### SQL Injection Prevention

```python
from typing import Any, Dict, List, Optional
import asyncpg

class SafeQueryBuilder:
    """Build safe SQL queries with parameterization."""
    
    def __init__(self, connection: asyncpg.Connection):
        self._conn = connection
    
    async def fetch_all(
        self,
        table: str,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Fetch records safely."""
        # Validate table name (whitelist approach)
        allowed_tables = ['videos', 'channels', 'analytics', 'users']
        if table not in allowed_tables:
            raise ValueError(f"Invalid table: {table}")
        
        # Build query with placeholders
        query = f"SELECT * FROM {table}"
        params = []
        
        if where:
            conditions = []
            param_index = 1
            for column, value in where.items():
                # Validate column name
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                    raise ValueError(f"Invalid column: {column}")
                conditions.append(f"{column} = ${param_index}")
                params.append(value)
                param_index += 1
            query += " WHERE " + " AND ".join(conditions)
        
        if order_by:
            # Validate order by column
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\s+(ASC|DESC))?$', order_by):
                raise ValueError("Invalid order by clause")
            query += f" ORDER BY {order_by}"
        
        if limit:
            if not isinstance(limit, int) or limit < 0 or limit > 1000:
                raise ValueError("Limit must be between 0 and 1000")
            query += f" LIMIT ${len(params) + 1}"
            params.append(limit)
        
        return await self._conn.fetch(query, *params)
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert record safely."""
        allowed_tables = ['videos', 'channels', 'analytics', 'users']
        if table not in allowed_tables:
            raise ValueError(f"Invalid table: {table}")
        
        columns = []
        placeholders = []
        params = []
        
        for i, (column, value) in enumerate(data.items(), 1):
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                raise ValueError(f"Invalid column: {column}")
            columns.append(column)
            placeholders.append(f"${i}")
            params.append(value)
        
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        result = await self._conn.fetchval(query, *params)
        return result
```

---

## Authentication & Authorization

### JWT Authentication

```python
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

class JWTService:
    """JWT token service for authentication."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expiry: int = 3600,
        refresh_token_expiry: int = 604800  # 7 days
    ):
        self._secret_key = secret_key.encode()
        self._algorithm = algorithm
        self._access_expiry = access_token_expiry
        self._refresh_expiry = refresh_token_expiry
    
    def create_access_token(
        self,
        subject: str,
        claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create access token."""
        now = datetime.utcnow()
        
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(seconds=self._access_expiry),
            "type": "access",
            "jti": self._generate_jti()
        }
        
        if claims:
            payload.update(claims)
        
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
    
    def create_refresh_token(self, subject: str) -> str:
        """Create refresh token."""
        now = datetime.utcnow()
        
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(seconds=self._refresh_expiry),
            "type": "refresh",
            "jti": self._generate_jti()
        }
        
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode token."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub", "type"]}
            )
            
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError(f"Invalid token type: expected {token_type}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token."""
        payload = self.verify_token(refresh_token, "refresh")
        return self.create_access_token(payload["sub"])
    
    def revoke_token(self, token: str) -> None:
        """Add token to revocation list."""
        # In production, use Redis or database
        payload = jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
            options={"verify_exp": False}
        )
        jti = payload.get("jti")
        # Add to revocation list with TTL
        # await redis.setex(f"revoked:{jti}", expiry, "1")
    
    def _generate_jti(self) -> str:
        """Generate unique token ID."""
        import secrets
        return secrets.token_urlsafe(32)


class AuthenticationError(Exception):
    """Authentication failure."""
    pass
```

### Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import Set, List, Optional
from functools import wraps

class Permission(Enum):
    """System permissions."""
    # Video permissions
    VIDEO_READ = "video:read"
    VIDEO_WRITE = "video:write"
    VIDEO_DELETE = "video:delete"
    VIDEO_PROCESS = "video:process"
    VIDEO_UPLOAD = "video:upload"
    
    # Channel permissions
    CHANNEL_READ = "channel:read"
    CHANNEL_WRITE = "channel:write"
    
    # Analytics permissions
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SETTINGS = "admin:settings"
    ADMIN_PLUGINS = "admin:plugins"


class Role(Enum):
    """System roles."""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.GUEST: {
        Permission.VIDEO_READ,
        Permission.CHANNEL_READ,
    },
    Role.USER: {
        Permission.VIDEO_READ,
        Permission.VIDEO_WRITE,
        Permission.VIDEO_PROCESS,
        Permission.CHANNEL_READ,
        Permission.CHANNEL_WRITE,
        Permission.ANALYTICS_READ,
    },
    Role.PREMIUM: {
        Permission.VIDEO_READ,
        Permission.VIDEO_WRITE,
        Permission.VIDEO_DELETE,
        Permission.VIDEO_PROCESS,
        Permission.VIDEO_UPLOAD,
        Permission.CHANNEL_READ,
        Permission.CHANNEL_WRITE,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXPORT,
    },
    Role.ADMIN: {
        Permission.VIDEO_READ,
        Permission.VIDEO_WRITE,
        Permission.VIDEO_DELETE,
        Permission.VIDEO_PROCESS,
        Permission.VIDEO_UPLOAD,
        Permission.CHANNEL_READ,
        Permission.CHANNEL_WRITE,
        Permission.ANALYTICS_READ,
        Permission.ANALYTICS_EXPORT,
        Permission.ADMIN_USERS,
        Permission.ADMIN_PLUGINS,
    },
    Role.SUPER_ADMIN: set(Permission),  # All permissions
}


class PermissionService:
    """Service for permission checking."""
    
    def __init__(self):
        self._role_permissions = ROLE_PERMISSIONS
    
    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Check if role has permission."""
        return permission in self._role_permissions.get(role, set())
    
    def has_any_permission(self, role: Role, permissions: List[Permission]) -> bool:
        """Check if role has any of the permissions."""
        role_perms = self._role_permissions.get(role, set())
        return any(p in role_perms for p in permissions)
    
    def has_all_permissions(self, role: Role, permissions: List[Permission]) -> bool:
        """Check if role has all permissions."""
        role_perms = self._role_permissions.get(role, set())
        return all(p in role_perms for p in permissions)
    
    def get_permissions(self, role: Role) -> Set[Permission]:
        """Get all permissions for role."""
        return self._role_permissions.get(role, set())


def require_permission(permission: Permission):
    """Decorator to require permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get user role from request
            role = request.state.user_role
            
            permission_service = PermissionService()
            if not permission_service.has_permission(role, permission):
                raise AuthorizationError(f"Missing permission: {permission.value}")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(*roles: Role):
    """Decorator to require specific role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_role = request.state.user_role
            
            if user_role not in roles:
                raise AuthorizationError(
                    f"Required role: {', '.join(r.value for r in roles)}"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


class AuthorizationError(Exception):
    """Authorization failure."""
    pass
```

### OAuth 2.0 Integration

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

class OAuthService:
    """OAuth 2.0 service for external authentication."""
    
    def __init__(self, config: Config):
        self._oauth = OAuth(config)
        self._register_providers()
    
    def _register_providers(self):
        """Register OAuth providers."""
        # Google OAuth
        self._oauth.register(
            name='google',
            client_id=config('GOOGLE_CLIENT_ID'),
            client_secret=config('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile https://www.googleapis.com/auth/youtube'
            }
        )
        
        # GitHub OAuth
        self._oauth.register(
            name='github',
            client_id=config('GITHUB_CLIENT_ID'),
            client_secret=config('GITHUB_CLIENT_SECRET'),
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'}
        )
    
    async def authorize(self, provider: str, request: Request):
        """Initiate OAuth authorization."""
        oauth_provider = self._oauth.create_client(provider)
        if not oauth_provider:
            raise ValueError(f"Unknown OAuth provider: {provider}")
        
        redirect_uri = request.url_for('oauth_callback')
        return await oauth_provider.authorize_redirect(request, redirect_uri)
    
    async def get_access_token(self, provider: str, request: Request) -> str:
        """Get access token from OAuth callback."""
        oauth_provider = self._oauth.create_client(provider)
        token = await oauth_provider.authorize_access_token(request)
        return token.get('access_token')
    
    async def get_user_info(self, provider: str, token: str) -> Dict:
        """Get user info from OAuth provider."""
        oauth_provider = self._oauth.create_client(provider)
        
        if provider == 'google':
            userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
        elif provider == 'github':
            userinfo_endpoint = 'user'
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        response = await oauth_provider.get(userinfo_endpoint, token={'access_token': token})
        return response.json()
```

---

## Encryption

### Data Encryption at Rest

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

class EncryptionService:
    """Service for encrypting data at rest."""
    
    def __init__(self, master_key: bytes):
        self._master_key = master_key
    
    def derive_key(self, salt: bytes, purpose: str) -> bytes:
        """Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt + purpose.encode(),
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(self._master_key))
    
    def encrypt(self, plaintext: bytes, context: str = "") -> Dict[str, str]:
        """Encrypt data with authenticated encryption."""
        # Generate random salt
        salt = os.urandom(16)
        
        # Derive key
        key = self.derive_key(salt, context)
        
        # Create Fernet instance
        fernet = Fernet(key)
        
        # Encrypt
        ciphertext = fernet.encrypt(plaintext)
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "salt": base64.b64encode(salt).decode()
        }
    
    def decrypt(
        self,
        ciphertext: str,
        salt: str,
        context: str = ""
    ) -> bytes:
        """Decrypt data."""
        salt_bytes = base64.b64decode(salt)
        ciphertext_bytes = base64.b64decode(ciphertext)
        
        # Derive key
        key = self.derive_key(salt_bytes, context)
        
        # Decrypt
        fernet = Fernet(key)
        return fernet.decrypt(ciphertext_bytes)


class EncryptedField:
    """Descriptor for encrypted model fields."""
    
    def __init__(self, context: str = ""):
        self._context = context
        self._encryption_service: Optional[EncryptionService] = None
    
    def __set_name__(self, owner, name):
        self._name = f"_encrypted_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        encrypted_data = getattr(obj, self._name, None)
        if encrypted_data is None:
            return None
        
        if not self._encryption_service:
            raise RuntimeError("Encryption service not initialized")
        
        plaintext = self._encryption_service.decrypt(
            encrypted_data["ciphertext"],
            encrypted_data["salt"],
            self._context
        )
        return plaintext.decode()
    
    def __set__(self, obj, value):
        if not self._encryption_service:
            raise RuntimeError("Encryption service not initialized")
        
        if value is None:
            setattr(obj, self._name, None)
            return
        
        encrypted = self._encryption_service.encrypt(
            value.encode(),
            self._context
        )
        setattr(obj, self._name, encrypted)
```

### TLS Configuration

```python
import ssl
from typing import Tuple

class TLSConfig:
    """Secure TLS configuration."""
    
    @staticmethod
    def create_server_context(
        cert_path: str,
        key_path: str,
        ca_path: Optional[str] = None
    ) -> ssl.SSLContext:
        """Create secure server SSL context."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Only allow TLS 1.2 and 1.3
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Disable weak ciphers
        context.set_ciphers(
            'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:'
            '!aNULL:!MD5:!DSS:!3DES:!RC4'
        )
        
        # Load certificates
        context.load_cert_chain(cert_path, key_path)
        
        if ca_path:
            context.load_verify_locations(ca_path)
        
        # Enable OCSP stapling
        context.ocsp_client_callback = None  # Configure as needed
        
        return context
    
    @staticmethod
    def create_client_context(
        ca_path: Optional[str] = None,
        verify: bool = True
    ) -> ssl.SSLContext:
        """Create secure client SSL context."""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # Only allow TLS 1.2 and 1.3
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Disable weak ciphers
        context.set_ciphers(
            'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:'
            '!aNULL:!MD5:!DSS:!3DES:!RC4'
        )
        
        if verify:
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            
            if ca_path:
                context.load_verify_locations(ca_path)
            else:
                context.load_default_certs()
        else:
            context.verify_mode = ssl.CERT_NONE
            context.check_hostname = False
        
        return context


# aiohttp secure session
import aiohttp

async def create_secure_session() -> aiohttp.ClientSession:
    """Create secure HTTP client session."""
    connector = aiohttp.TCPConnector(
        ssl=TLSConfig.create_client_context(),
        enable_cleanup_closed=True
    )
    
    return aiohttp.ClientSession(
        connector=connector,
        timeout=aiohttp.ClientTimeout(total=30)
    )
```

### Secret Management

```python
from typing import Optional
from pathlib import Path
import json

class SecretManager:
    """Secure secret management."""
    
    def __init__(self, backend: str = "env"):
        self._backend = backend
        self._cache: dict = {}
    
    async def get(self, name: str) -> Optional[str]:
        """Get secret by name."""
        # Check cache first
        if name in self._cache:
            return self._cache[name]
        
        if self._backend == "env":
            value = self._get_from_env(name)
        elif self._backend == "file":
            value = self._get_from_file(name)
        elif self._backend == "aws_secrets":
            value = await self._get_from_aws(name)
        elif self._backend == "gcp_secret":
            value = await self._get_from_gcp(name)
        else:
            raise ValueError(f"Unknown secret backend: {self._backend}")
        
        if value:
            self._cache[name] = value
        
        return value
    
    def _get_from_env(self, name: str) -> Optional[str]:
        """Get secret from environment variable."""
        import os
        return os.environ.get(name)
    
    def _get_from_file(self, name: str) -> Optional[str]:
        """Get secret from file."""
        secrets_dir = Path("/run/secrets")
        secret_path = secrets_dir / name
        
        if secret_path.exists():
            return secret_path.read_text().strip()
        return None
    
    async def _get_from_aws(self, name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        import aioboto3
        
        session = aioboto3.Session()
        async with session.client("secretsmanager") as client:
            response = await client.get_secret_value(SecretId=name)
            return response.get("SecretString")
    
    async def _get_from_gcp(self, name: str) -> Optional[str]:
        """Get secret from GCP Secret Manager."""
        from google.cloud import secretmanager
        
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")


# Usage
async def get_database_url() -> str:
    """Get database URL from secrets."""
    secrets = SecretManager(backend="aws_secrets")
    return await secrets.get("database/url")
```

---

## Audit Logging

### Audit Log Framework

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import json
import logging

class AuditEventType(Enum):
    """Audit event types."""
    # Authentication
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    PASSWORD_CHANGE = "auth.password.change"
    
    # Authorization
    PERMISSION_DENIED = "authz.denied"
    ROLE_CHANGE = "authz.role.change"
    
    # Data Access
    DATA_READ = "data.read"
    DATA_CREATE = "data.create"
    DATA_UPDATE = "data.update"
    DATA_DELETE = "data.delete"
    
    # Video Operations
    VIDEO_UPLOAD = "video.upload"
    VIDEO_PROCESS = "video.process"
    VIDEO_DOWNLOAD = "video.download"
    VIDEO_DELETE = "video.delete"
    
    # System
    CONFIG_CHANGE = "system.config.change"
    PLUGIN_INSTALL = "system.plugin.install"
    PLUGIN_UNINSTALL = "system.plugin.uninstall"


class AuditLogger:
    """Structured audit logging."""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def log(
        self,
        event_type: AuditEventType,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log audit event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "actor": {
                "id": actor_id,
                "ip": ip_address,
                "user_agent": user_agent
            },
            "resource": {
                "type": resource_type,
                "id": resource_id
            },
            "action": action,
            "status": status,
            "details": details or {}
        }
        
        # Log as JSON for easy parsing
        self._logger.info(json.dumps(event))
    
    def log_data_access(
        self,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        operation: str,
        fields_accessed: Optional[list] = None
    ):
        """Log data access event."""
        self.log(
            event_type=AuditEventType.DATA_READ,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=operation,
            details={"fields": fields_accessed}
        )
    
    def log_auth_event(
        self,
        user_id: str,
        event_type: AuditEventType,
        success: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log authentication event."""
        self.log(
            event_type=event_type,
            actor_id=user_id,
            resource_type="user",
            resource_id=user_id,
            action=event_type.value.split(".")[-1],
            status="success" if success else "failure",
            details={"reason": reason} if reason else None,
            ip_address=ip_address
        )


# Configure audit logger
audit_logger = AuditLogger(logging.getLogger("audit"))

# Usage in application
async def login(username: str, password: str, ip_address: str):
    """Login with audit logging."""
    try:
        user = await authenticate_user(username, password)
        
        audit_logger.log_auth_event(
            user_id=user.id,
            event_type=AuditEventType.LOGIN_SUCCESS,
            success=True,
            ip_address=ip_address
        )
        
        return create_session(user)
        
    except AuthenticationError as e:
        audit_logger.log_auth_event(
            user_id=username,
            event_type=AuditEventType.LOGIN_FAILURE,
            success=False,
            reason=str(e),
            ip_address=ip_address
        )
        raise
```

### Log Aggregation

```python
import asyncio
import aiohttp
from typing import List

class LogAggregator:
    """Aggregate and forward logs to central system."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        batch_size: int = 100,
        flush_interval: int = 10
    ):
        self._endpoint = endpoint
        self._api_key = api_key
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._buffer: List[dict] = []
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start background flush task."""
        self._flush_task = asyncio.create_task(self._flush_loop())
    
    async def stop(self):
        """Stop and flush remaining logs."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush()
    
    async def add_log(self, log_entry: dict):
        """Add log entry to buffer."""
        async with self._lock:
            self._buffer.append(log_entry)
            
            if len(self._buffer) >= self._batch_size:
                await self._flush()
    
    async def _flush_loop(self):
        """Periodically flush logs."""
        while True:
            await asyncio.sleep(self._flush_interval)
            await self._flush()
    
    async def _flush(self):
        """Flush buffered logs."""
        async with self._lock:
            if not self._buffer:
                return
            
            logs_to_send = self._buffer.copy()
            self._buffer.clear()
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self._endpoint,
                    json={"logs": logs_to_send},
                    headers={"Authorization": f"Bearer {self._api_key}"}
                )
        except Exception as e:
            # Re-add failed logs to buffer
            async with self._lock:
                self._buffer.extend(logs_to_send)
            logging.error(f"Failed to send logs: {e}")
```

---

## Security Best Practices

### Secure Configuration

```yaml
# config/security.yaml
security:
  # Authentication
  authentication:
    enabled: true
    session_timeout: 3600  # 1 hour
    max_login_attempts: 5
    lockout_duration: 900  # 15 minutes
    
  # Password policy
  password:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special: true
    max_age_days: 90
    history_count: 12
    
  # Rate limiting
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    burst_limit: 10
    
  # CORS
  cors:
    allowed_origins:
      - https://app.example.com
    allowed_methods:
      - GET
      - POST
      - PUT
      - DELETE
    allow_credentials: true
    
  # Headers
  headers:
    strict_transport_security: "max-age=31536000; includeSubDomains"
    content_security_policy: "default-src 'self'"
    x_content_type_options: "nosniff"
    x_frame_options: "DENY"
    x_xss_protection: "1; mode=block"
    
  # Encryption
  encryption:
    algorithm: "AES-256-GCM"
    key_rotation_days: 90
    
  # Audit logging
  audit:
    enabled: true
    log_level: "INFO"
    retention_days: 365
    include_request_body: false
```

### Security Headers Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # HSTS
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.youtube.com"
        )
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        
        return response
```

### Dependency Security

```python
# security/dependency_check.py
import subprocess
import json
from typing import List, Dict

class DependencyScanner:
    """Scan dependencies for vulnerabilities."""
    
    def __init__(self):
        self._vulnerabilities: List[Dict] = []
    
    async def scan(self) -> List[Dict]:
        """Scan project dependencies."""
        # Run safety check
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return []
        
        vulnerabilities = json.loads(result.stdout)
        self._vulnerabilities = vulnerabilities
        
        return vulnerabilities
    
    def get_critical_vulnerabilities(self) -> List[Dict]:
        """Get critical severity vulnerabilities."""
        return [
            v for v in self._vulnerabilities
            if v.get("severity") == "critical"
        ]
    
    def generate_report(self) -> str:
        """Generate vulnerability report."""
        if not self._vulnerabilities:
            return "No vulnerabilities found."
        
        lines = ["DEPENDENCY VULNERABILITIES", "=" * 40]
        
        for vuln in self._vulnerabilities:
            lines.extend([
                f"\nPackage: {vuln.get('package_name')}",
                f"Installed: {vuln.get('installed_version')}",
                f"Vulnerable: {vuln.get('vulnerable_spec')}",
                f"Severity: {vuln.get('severity')}",
                f"CVE: {vuln.get('cve_id')}",
                f"Advice: {vuln.get('advice')}"
            ])
        
        return "\n".join(lines)


# Usage in CI/CD
async def security_scan():
    scanner = DependencyScanner()
    vulnerabilities = await scanner.scan()
    
    if vulnerabilities:
        print(scanner.generate_report())
        
        # Fail build on critical vulnerabilities
        critical = scanner.get_critical_vulnerabilities()
        if critical:
            raise SystemExit(1)
```

---

## Threat Model

### Threat Categories

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           THREAT MODEL                                    │
└──────────────────────────────────────────────────────────────────────────┘

  STRIDE Categories:
  ┌─────────────────────────────────────────────────────────────────────┐
  │ S - Spoofing          │ Impersonating users or systems              │
  │ T - Tampering         │ Modifying data or code                      │
  │ R - Repudiation       │ Denying actions                             │
  │ I - Information       │ Accessing unauthorized data                 │
  │     Disclosure        │                                             │
  │ D - Denial of Service │ Making services unavailable                 │
  │ E - Elevation of      │ Gaining unauthorized privileges             │
  │     Privilege         │                                             │
  └─────────────────────────────────────────────────────────────────────┘
```

### Threat Matrix

| Threat | Risk Level | Mitigation |
|--------|------------|------------|
| **API Key Theft** | High | Key rotation, IP restrictions, monitoring |
| **OAuth Token Theft** | High | Short expiry, refresh token rotation |
| **SQL Injection** | Medium | Parameterized queries, input validation |
| **XSS Attacks** | Medium | CSP headers, output encoding |
| **CSRF Attacks** | Medium | CSRF tokens, SameSite cookies |
| **DDoS Attacks** | Medium | Rate limiting, CDN, WAF |
| **Privilege Escalation** | High | RBAC, least privilege, audit logs |
| **Data Breach** | High | Encryption at rest, access controls |
| **Man-in-the-Middle** | High | TLS 1.3, certificate pinning |
| **Session Hijacking** | Medium | Secure cookies, session timeout |

### Attack Vectors

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         ATTACK VECTORS                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  EXTERNAL ATTACKS                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │   API       │  │   Web       │  │   Network   │                      │
│  │   Abuse     │  │   Attacks   │  │   Attacks   │                      │
│  │             │  │             │  │             │                      │
│  │ - Rate limit│  │ - XSS       │  │ - DDoS      │                      │
│  │   bypass    │  │ - CSRF      │  │ - MITM      │                      │
│  │ - Quota     │  │ - Injection │  │ - DNS       │                      │
│  │   exhaustion│  │ - Path      │  │   poisoning │                      │
│  │             │  │   traversal │  │             │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
│                                                                          │
│  INTERNAL ATTACKS                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │  Privilege  │  │   Data      │  │  Credential │                      │
│  │ Escalation  │  │   Exfil     │  │   Theft     │                      │
│  │             │  │             │  │             │                      │
│  │ - Role      │  │ - Bulk      │  │ - Token     │                      │
│  │   manipulation│ │ export    │  │   theft     │                      │
│  │ - Direct    │  │ - API       │  │ - Session   │                      │
│  │   DB access │  │   scraping  │  │   hijacking │                      │
│  │             │  │             │  │             │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
│                                                                          │
│  SUPPLY CHAIN ATTACKS                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │  Dependency │  │   Plugin    │  │   Build     │                      │
│  │  Injection  │  │   Compromise│  │   Compromise│                      │
│  │             │  │             │  │             │                      │
│  │ - Malicious │  │ - Rogue     │  │ - CI/CD     │                      │
│  │   packages  │  │   plugins   │  │   injection │                      │
│  │ - Version   │  │ - Data      │  │ - Artifact  │                      │
│  │   downgrade │  │   exfil     │  │   tampering │                      │
│  │             │  │             │  │             │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Security Controls

```python
class SecurityControls:
    """Implement security controls for threat mitigation."""
    
    @staticmethod
    async def validate_request_origin(request: Request) -> bool:
        """Validate request origin to prevent CSRF."""
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        allowed_origins = ["https://app.example.com"]
        
        if origin and origin not in allowed_origins:
            return False
        
        return True
    
    @staticmethod
    async def check_rate_limit(
        client_id: str,
        endpoint: str,
        limit: int = 60,
        window: int = 60
    ) -> bool:
        """Check rate limit for client."""
        key = f"ratelimit:{client_id}:{endpoint}"
        
        current = await redis.get(key)
        if current is None:
            await redis.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            return False
        
        await redis.incr(key)
        return True
    
    @staticmethod
    async def validate_csrf_token(
        request: Request,
        session_token: str
    ) -> bool:
        """Validate CSRF token."""
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            return False
        
        # Verify token matches session
        expected = await get_csrf_token_for_session(session_token)
        return csrf_token == expected
    
    @staticmethod
    def sanitize_output(data: Any, sensitivity: str = "public") -> Any:
        """Sanitize output based on sensitivity."""
        if sensitivity == "public":
            return data
        
        # Remove sensitive fields
        sensitive_fields = ["password", "token", "secret", "api_key"]
        
        if isinstance(data, dict):
            return {
                k: v for k, v in data.items()
                if k.lower() not in sensitive_fields
            }
        
        return data
```

---

## Incident Response

### Incident Response Plan

```python
from enum import Enum
from datetime import datetime
from typing import List, Optional

class IncidentSeverity(Enum):
    """Incident severity levels."""
    CRITICAL = "critical"  # Data breach, service down
    HIGH = "high"          # Security vulnerability exploited
    MEDIUM = "medium"      # Suspicious activity detected
    LOW = "low"            # Minor policy violation


class IncidentResponse:
    """Incident response management."""
    
    def __init__(self):
        self._response_team: List[str] = []
        self._escalation_contacts: dict = {}
    
    async def create_incident(
        self,
        title: str,
        severity: IncidentSeverity,
        description: str,
        detected_by: str
    ) -> str:
        """Create new incident."""
        incident_id = self._generate_incident_id()
        
        incident = {
            "id": incident_id,
            "title": title,
            "severity": severity.value,
            "description": description,
            "status": "open",
            "detected_by": detected_by,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "timeline": [],
            "actions_taken": []
        }
        
        # Store incident
        await self._store_incident(incident)
        
        # Notify response team
        await self._notify_team(incident)
        
        return incident_id
    
    async def update_incident(
        self,
        incident_id: str,
        status: str,
        update: str,
        updated_by: str
    ):
        """Update incident status."""
        incident = await self._get_incident(incident_id)
        
        incident["status"] = status
        incident["updated_at"] = datetime.utcnow().isoformat()
        incident["timeline"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "status_update",
            "details": update,
            "by": updated_by
        })
        
        await self._store_incident(incident)
    
    async def escalate_incident(
        self,
        incident_id: str,
        reason: str,
        escalated_by: str
    ):
        """Escalate incident to higher severity."""
        incident = await self._get_incident(incident_id)
        
        # Escalate severity
        severity_order = list(IncidentSeverity)
        current_idx = severity_order.index(
            IncidentSeverity(incident["severity"])
        )
        
        if current_idx < len(severity_order) - 1:
            incident["severity"] = severity_order[current_idx + 1].value
            
            # Notify escalation contacts
            await self._notify_escalation_contacts(incident, reason)
        
        incident["timeline"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "escalation",
            "details": reason,
            "by": escalated_by
        })
        
        await self._store_incident(incident)
    
    async def close_incident(
        self,
        incident_id: str,
        resolution: str,
        closed_by: str
    ):
        """Close incident with resolution."""
        incident = await self._get_incident(incident_id)
        
        incident["status"] = "closed"
        incident["resolution"] = resolution
        incident["closed_at"] = datetime.utcnow().isoformat()
        incident["closed_by"] = closed_by
        
        await self._store_incident(incident)
        
        # Generate post-incident report
        await self._generate_report(incident)
    
    async def _notify_team(self, incident: dict):
        """Notify response team."""
        # Send notifications via configured channels
        pass
    
    async def _notify_escalation_contacts(self, incident: dict, reason: str):
        """Notify escalation contacts."""
        # Send urgent notifications
        pass
    
    async def _generate_report(self, incident: dict):
        """Generate post-incident report."""
        report = {
            "incident_id": incident["id"],
            "title": incident["title"],
            "severity": incident["severity"],
            "duration": self._calculate_duration(incident),
            "timeline": incident["timeline"],
            "resolution": incident.get("resolution"),
            "lessons_learned": [],
            "action_items": []
        }
        
        # Store report
        await self._store_report(report)
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID."""
        import secrets
        return f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4)}"
    
    def _calculate_duration(self, incident: dict) -> str:
        """Calculate incident duration."""
        start = datetime.fromisoformat(incident["created_at"])
        end = datetime.fromisoformat(incident.get("closed_at", datetime.utcnow().isoformat()))
        return str(end - start)
```

### Security Monitoring

```python
class SecurityMonitor:
    """Real-time security monitoring."""
    
    def __init__(self):
        self._alerts: List[dict] = []
        self._rules: List[dict] = []
    
    def add_detection_rule(self, rule: dict):
        """Add detection rule."""
        self._rules.append(rule)
    
    async def check_events(self, events: List[dict]):
        """Check events against detection rules."""
        for event in events:
            for rule in self._rules:
                if self._matches_rule(event, rule):
                    await self._create_alert(event, rule)
    
    def _matches_rule(self, event: dict, rule: dict) -> bool:
        """Check if event matches rule."""
        # Implement rule matching logic
        pass
    
    async def _create_alert(self, event: dict, rule: dict):
        """Create security alert."""
        alert = {
            "id": self._generate_alert_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "rule": rule["name"],
            "severity": rule["severity"],
            "event": event,
            "status": "new"
        }
        
        self._alerts.append(alert)
        
        # Notify security team
        if rule["severity"] in ["critical", "high"]:
            await self._notify_security_team(alert)
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        import secrets
        return f"ALT-{secrets.token_hex(8)}"
    
    async def _notify_security_team(self, alert: dict):
        """Notify security team of critical alert."""
        # Send notification via PagerDuty, Slack, etc.
        pass


# Example detection rules
DETECTION_RULES = [
    {
        "name": "brute_force_login",
        "description": "Multiple failed login attempts",
        "condition": {
            "event_type": "auth.login.failure",
            "count": 5,
            "window_seconds": 300
        },
        "severity": "high"
    },
    {
        "name": "privilege_escalation",
        "description": "User role changed to admin",
        "condition": {
            "event_type": "authz.role.change",
            "new_role": "admin"
        },
        "severity": "critical"
    },
    {
        "name": "data_exfiltration",
        "description": "Large data export",
        "condition": {
            "event_type": "data.read",
            "record_count": 1000
        },
        "severity": "high"
    }
]
```

---

## Security Checklist

### Pre-Deployment

- [ ] All dependencies scanned for vulnerabilities
- [ ] Security headers configured
- [ ] TLS 1.2+ enforced
- [ ] Authentication enabled
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Secrets stored securely
- [ ] Input validation implemented
- [ ] Error messages sanitized
- [ ] CORS properly configured

### Post-Deployment

- [ ] Security monitoring active
- [ ] Alert notifications configured
- [ ] Backup encryption verified
- [ ] Access logs reviewed
- [ ] Penetration testing scheduled
- [ ] Incident response plan tested
- [ ] Security documentation updated
- [ ] Team security training completed

---

*Documentation generated for YouTube Enhancement Tools v3.2.0*
*Last updated: March 4, 2026*
