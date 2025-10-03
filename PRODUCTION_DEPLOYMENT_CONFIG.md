# Production Deployment Configuration

**Date**: 2025-10-03
**System**: Archon V2 Alpha AI Empire
**Status**: Production-Ready Configuration

---

## Overview

Complete production deployment configuration for the Archon V2 Alpha system including environment variables, Docker compose, nginx configuration, and deployment scripts.

---

## Environment Variables

### Production .env Template

Create `.env.production` with the following configuration:

```bash
# ===== ENVIRONMENT =====
NODE_ENV=production
ARCHON_ENV=production

# ===== SERVER PORTS =====
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
FRONTEND_PORT=5173

# ===== DATABASE =====
SUPABASE_URL=https://your-production-project.supabase.co
SUPABASE_SERVICE_KEY=your-production-service-key
SUPABASE_ANON_KEY=your-production-anon-key

# ===== AI PROVIDERS =====
# IMPORTANT: Only use OpenRouter for all AI requests
OPENROUTER_API_KEY=your-production-openrouter-key

# ===== FEATURES =====
PROJECTS_ENABLED=true
USE_DATABASE_STORAGE=true
USE_AGENTIC_RAG=true
LOGFIRE_ENABLED=true
SERENA_ENABLED=true
CLAUDE_CONTEXT_ENABLED=true

# ===== MONITORING =====
LOGFIRE_TOKEN=your-production-logfire-token
LOG_LEVEL=INFO

# ===== SECURITY =====
JWT_SECRET=your-secure-random-jwt-secret-here
API_KEY_SALT=your-secure-random-salt-here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ===== RATE LIMITING =====
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# ===== SSL/TLS =====
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/archon.crt
SSL_KEY_PATH=/etc/ssl/private/archon.key
```

---

## Docker Configuration

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  # Backend API
  archon-api:
    build:
      context: ./python
      dockerfile: Dockerfile.production
    container_name: archon-api
    restart: unless-stopped
    environment:
      - ARCHON_ENV=production
      - ARCHON_SERVER_PORT=8181
    env_file:
      - .env.production
    ports:
      - "8181:8181"
    volumes:
      - ./python:/app
      - /app/node_modules
    networks:
      - archon-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8181/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # MCP Server
  archon-mcp:
    build:
      context: ./python
      dockerfile: Dockerfile.mcp
    container_name: archon-mcp
    restart: unless-stopped
    environment:
      - ARCHON_ENV=production
      - ARCHON_MCP_PORT=8051
    env_file:
      - .env.production
    ports:
      - "8051:8051"
    volumes:
      - ./python:/app
    networks:
      - archon-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8051/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Frontend
  archon-frontend:
    build:
      context: ./archon-ui-main
      dockerfile: Dockerfile.production
    container_name: archon-frontend
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    ports:
      - "5173:5173"
    networks:
      - archon-network
    depends_on:
      - archon-api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5173"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: archon-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
      - ./logs/nginx:/var/log/nginx
    networks:
      - archon-network
    depends_on:
      - archon-api
      - archon-mcp
      - archon-frontend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  archon-network:
    driver: bridge

volumes:
  python-modules:
  node-modules:
```

---

## Nginx Configuration

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream archon_backend {
        server archon-api:8181;
    }

    upstream archon_mcp {
        server archon-mcp:8051;
    }

    upstream archon_frontend {
        server archon-frontend:5173;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    # HTTP -> HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # Main HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/ssl/certs/archon.crt;
        ssl_certificate_key /etc/ssl/private/archon.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # Frontend
        location / {
            limit_req zone=general_limit burst=20 nodelay;
            proxy_pass http://archon_frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            limit_req zone=api_limit burst=10 nodelay;
            proxy_pass http://archon_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # CORS headers
            add_header Access-Control-Allow-Origin $http_origin always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
            add_header Access-Control-Allow-Credentials true always;

            if ($request_method = OPTIONS) {
                return 204;
            }
        }

        # MCP Server
        location /mcp/ {
            limit_req zone=api_limit burst=10 nodelay;
            proxy_pass http://archon_mcp/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # WebSocket support
        location /socket.io/ {
            proxy_pass http://archon_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Health check endpoints (no rate limiting)
        location /health {
            proxy_pass http://archon_backend;
        }

        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Logging
        access_log /var/log/nginx/archon_access.log;
        error_log /var/log/nginx/archon_error.log warn;
    }
}
```

---

## Dockerfiles

### Python Backend Dockerfile.production

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 archon && chown -R archon:archon /app
USER archon

# Expose port
EXPOSE 8181

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8181/health || exit 1

# Start application
CMD ["uv", "run", "python", "-m", "src.server.main"]
```

### Frontend Dockerfile.production

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy built files
COPY --from=builder /app/dist ./dist

# Create non-root user
RUN addgroup -g 1000 archon && adduser -D -u 1000 -G archon archon
USER archon

# Expose port
EXPOSE 5173

# Serve the application
CMD ["serve", "-s", "dist", "-l", "5173"]
```

---

## Deployment Scripts

### deploy.sh

```bash
#!/bin/bash

# Archon V2 Alpha - Production Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|status]

set -e

COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.production exists
if [ ! -f "$ENV_FILE" ]; then
    log_error "Production environment file not found: $ENV_FILE"
    log_info "Please create $ENV_FILE based on the template"
    exit 1
fi

# Main deployment commands
case "$1" in
    start)
        log_info "Starting Archon V2 Alpha in production mode..."
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d --build
        log_info "Waiting for services to be healthy..."
        sleep 10
        docker-compose -f $COMPOSE_FILE ps
        log_info "Deployment complete!"
        log_info "Access the dashboard at: https://yourdomain.com"
        ;;

    stop)
        log_info "Stopping Archon V2 Alpha services..."
        docker-compose -f $COMPOSE_FILE down
        log_info "All services stopped"
        ;;

    restart)
        log_info "Restarting Archon V2 Alpha services..."
        docker-compose -f $COMPOSE_FILE restart
        log_info "Services restarted"
        ;;

    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            docker-compose -f $COMPOSE_FILE logs -f
        else
            docker-compose -f $COMPOSE_FILE logs -f $SERVICE
        fi
        ;;

    status)
        log_info "Service Status:"
        docker-compose -f $COMPOSE_FILE ps
        echo ""
        log_info "Health Checks:"
        curl -f http://localhost:8181/health && echo "✅ Backend API: Healthy" || echo "❌ Backend API: Unhealthy"
        curl -f http://localhost:8051/health && echo "✅ MCP Server: Healthy" || echo "❌ MCP Server: Unhealthy"
        curl -f http://localhost:5173 && echo "✅ Frontend: Healthy" || echo "❌ Frontend: Unhealthy"
        ;;

    backup)
        log_info "Creating backup..."
        BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        cp -r python $BACKUP_DIR/
        cp -r archon-ui-main $BACKUP_DIR/
        cp $ENV_FILE $BACKUP_DIR/
        log_info "Backup created: $BACKUP_DIR"
        ;;

    update)
        log_info "Updating Archon V2 Alpha..."
        git pull origin main
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up -d --build
        log_info "Update complete!"
        ;;

    *)
        echo "Usage: $0 {start|stop|restart|logs|status|backup|update}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - View logs (optionally specify service name)"
        echo "  status  - Show service status and health"
        echo "  backup  - Create a backup of the system"
        echo "  update  - Pull latest code and rebuild"
        exit 1
        ;;
esac
```

---

## Security Checklist

### Pre-Deployment Security

- [ ] Update all environment variables with production values
- [ ] Generate secure random JWT_SECRET (32+ characters)
- [ ] Generate secure API_KEY_SALT (32+ characters)
- [ ] Configure proper CORS_ORIGINS (no wildcards in production)
- [ ] Obtain and install SSL/TLS certificates
- [ ] Review and update rate limiting settings
- [ ] Enable and configure Logfire monitoring
- [ ] Set up database backups
- [ ] Configure firewall rules (only allow 80, 443)
- [ ] Disable debug mode (LOG_LEVEL=INFO or WARNING)

### Post-Deployment Security

- [ ] Test SSL/TLS configuration (ssllabs.com)
- [ ] Verify CORS settings
- [ ] Test rate limiting
- [ ] Review security headers
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Test backup and restore procedures
- [ ] Run security audit (OWASP ZAP, Burp Suite)
- [ ] Set up intrusion detection
- [ ] Document incident response procedures

---

## Monitoring & Logging

### Log Files

```bash
# Application logs
docker-compose logs -f archon-api
docker-compose logs -f archon-mcp
docker-compose logs -f archon-frontend

# Nginx logs
tail -f logs/nginx/archon_access.log
tail -f logs/nginx/archon_error.log
```

### Health Monitoring

```bash
# Automated health check script
#!/bin/bash
while true; do
    curl -f http://localhost:8181/health || echo "❌ Backend unhealthy"
    curl -f http://localhost:8051/health || echo "❌ MCP unhealthy"
    curl -f http://localhost:5173 || echo "❌ Frontend unhealthy"
    sleep 60
done
```

---

## Backup Strategy

### Automated Backup Script

```bash
#!/bin/bash
# backup_cron.sh - Run daily at 2 AM

BACKUP_DIR="/backups/archon"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup application code
tar -czf $BACKUP_DIR/$DATE/code.tar.gz python/ archon-ui-main/

# Backup environment config
cp .env.production $BACKUP_DIR/$DATE/

# Backup database (if using local DB)
# pg_dump ... > $BACKUP_DIR/$DATE/database.sql

# Keep last 7 days of backups
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR/$DATE"
```

Add to crontab:
```bash
0 2 * * * /path/to/backup_cron.sh
```

---

## Performance Optimization

### Backend Optimization

1. **Database Connection Pooling**
   - Configure max connections in Supabase
   - Use connection pooling in application

2. **Caching**
   - Implement Redis for session storage
   - Cache frequently accessed data

3. **Load Balancing**
   - Deploy multiple backend instances
   - Use nginx load balancing

### Frontend Optimization

1. **Asset Optimization**
   - Minify JavaScript and CSS
   - Optimize images (WebP format)
   - Enable gzip compression

2. **CDN Integration**
   - Serve static assets from CDN
   - Configure proper cache headers

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] DNS records configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Security audit completed
- [ ] Documentation updated

### Deployment

- [ ] Create backup of current system
- [ ] Deploy to staging environment first
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Verify all services healthy
- [ ] Test critical user flows
- [ ] Monitor logs for errors

### Post-Deployment

- [ ] Update documentation
- [ ] Notify stakeholders
- [ ] Monitor performance metrics
- [ ] Review logs daily (first week)
- [ ] Schedule security review (1 month)

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop failed deployment
./deploy.sh stop

# 2. Restore from backup
cp -r backups/LATEST/* ./

# 3. Restart with previous version
docker-compose up -d

# 4. Verify health
./deploy.sh status
```

---

## Support & Maintenance

### Regular Maintenance Tasks

**Daily**:
- Review error logs
- Check service health
- Monitor resource usage

**Weekly**:
- Review security logs
- Check backup integrity
- Update dependencies

**Monthly**:
- Security audit
- Performance review
- Update documentation

---

**Configuration Version**: 1.0
**Last Updated**: 2025-10-03
**Status**: Production-Ready
