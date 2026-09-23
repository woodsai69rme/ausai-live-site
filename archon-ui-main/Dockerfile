# Production-ready Node.js build

# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++ git

COPY package*.json ./
RUN npm ci

COPY . .

# Build the app
RUN npm run build

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Install only runtime dependencies
RUN apk add --no-cache curl

# Copy built app from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Expose Vite's default port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Start Vite dev server with host binding for Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
