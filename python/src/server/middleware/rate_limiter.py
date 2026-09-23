import time
from fastapi import Request, HTTPException, status
from typing import Dict, List

# In-memory storage for request times
# Format: {ip: [timestamp1, timestamp2, ...]}
request_times: Dict[str, List[float]] = {}

# Configuration
REQUESTS_PER_MINUTE = 10  # Allow 10 requests per minute per IP
CLEANUP_INTERVAL = 60     # Clean up entries older than 60 seconds

def rate_limiter(request: Request):
    """
    Simple rate limiter dependency that limits requests per IP address.
    """
    # Get client IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    
    # Clean up old requests (older than 1 minute)
    now = time.time()
    if ip in request_times:
        # Remove timestamps older than 1 minute
        request_times[ip] = [t for t in request_times[ip] if now - t < CLEANUP_INTERVAL]
        # If the list is empty, remove the IP entry
        if not request_times[ip]:
            del request_times[ip]
    else:
        request_times[ip] = []
    
    # Check if the IP has exceeded the request limit
    if len(request_times[ip]) >= REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )
    
    # Add current request timestamp
    request_times[ip].append(now)