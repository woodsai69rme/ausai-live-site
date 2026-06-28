# Production Configuration Summary

## Environment Variables

All services have been configured with production settings:
- **DEBUG_MODE**: `false` (debug mode disabled)
- **ARCHON_ENV**: `production` (production environment)
- **LOG_LEVEL**: `INFO` (logging level)

## Healthchecks

All services now have healthcheck endpoints:
- **archon-server**: `/health` - accessible at `http://localhost:8181/health`
- **archon-mcp**: `/health` - accessible at `http://localhost:8051/health`
- **archon-agents**: `/health` - accessible at `http://localhost:8052/health`
- **frontend**: root endpoint `/` - accessible at `http://localhost:3737`

## Resource Limits

Each service has been configured with appropriate resource limits:

| Service         | Memory Limit | Memory Reservation | CPU Limit | CPU Reservation |
|----------------|--------------|---------------------|-----------|------------------|
| archon-server  | 2GB          | 1GB                 | 1.0       | 0.5              |
| archon-mcp     | 1GB          | 512MB               | 0.5       | 0.25             |
| archon-agents  | 3GB          | 1.5GB               | 1.5       | 0.75             |
| frontend       | 512MB        | 256MB               | 0.5       | 0.25             |

## User Permissions

All containers now run as non-root user with UID 1000 and GID 1000 for improved security.

## Restart Policy

All services are configured to restart automatically:
- **Restart Policy**: `unless-stopped`

## Debug Mode

Debug mode has been disabled for all services:
- **DEBUG_MODE=false** ensures debugging information is not exposed
- **ARCHON_ENV=production** indicates production environment

## Volume Mounts

Development volume mounts have been removed from the server and frontend services to avoid using host volumes in production.

## Healthcheck Configuration

Each service's healthcheck is configured with:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 40-60 seconds
- **Retries**: 3

## Playwright Service

The PlaywrightService now includes import fallback and error handling:
- If Playwright fails to import, it falls back to disabled mode
- Crawling functionality returns appropriate error responses when Playwright is unavailable
- Logs warnings and errors appropriately

## Running the Application

### Start the application
```bash
cd C:\Users\karma
docker-compose up -d
```

### Check container status
```bash
docker-compose ps
```

### Check service logs
```bash
docker-compose logs <service-name>  # e.g., archon-server
docker-compose logs -f            # follow all logs
```

### Check resource usage
```bash
docker stats
```

### Stop the application
```bash
docker-compose down
```

### Check environment variables in containers
```bash
# Server
docker-compose exec archon-server printenv | grep -E 'DEBUG_MODE|ARCHON_ENV|LOG_LEVEL'

# MCP
docker-compose exec archon-mcp printenv | grep -E 'DEBUG_MODE|ARCHON_ENV|LOG_LEVEL'

# Agents
docker-compose exec archon-agents printenv | grep -E 'DEBUG_MODE|ARCHON_ENV|LOG_LEVEL'
```

## Healthcheck Endpoints

All healthcheck endpoints should return JSON with status:

```json
{
  "status": "healthy",
  "service": "Service Name"
}
```

### Test health endpoints
```bash
curl -X GET http://localhost:8181/health  # Server
curl -X GET http://localhost:8051/health  # MCP
curl -X GET http://localhost:8052/health  # Agents
curl -X GET http://localhost:3737/        # Frontend
```

## Verification

The configuration has been verified with:
- **Docker Compose Validation**: `docker-compose config` shows valid configuration
- **Image Build**: `docker-compose build --no-cache` successfully builds all images
- **Container Startup**: `docker-compose up -d` starts all containers
- **Healthchecks**: All services pass healthchecks
- **Environment Variables**: Correct production values are set
- **Resource Limits**: Containers respect resource constraints
- **User Permissions**: Services run as non-root user