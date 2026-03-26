#!/bin/bash
# M537 Voice Gateway Deployment Script
# V5.3 Compliant

set -e

PROJECT_DIR="/data/projects/m537_voice_gateway"
DOMAIN="m537.x1000.ai"

echo "=== M537 Voice Gateway Deployment ==="
echo "Date: $(date)"
echo ""

# 1. Enter project directory
cd $PROJECT_DIR
echo "[1/6] Entered project directory: $PROJECT_DIR"

# 2. Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[2/6] Created .env from .env.example"
else
    echo "[2/6] .env already exists"
fi

# 3. Build Docker image
echo "[3/6] Building Docker image..."
docker compose build --no-cache

# 4. Stop existing container (if any)
echo "[4/6] Stopping existing container..."
docker compose down || true

# 5. Start new container
echo "[5/6] Starting new container..."
docker compose up -d

# 6. Wait and verify
echo "[6/6] Waiting for service to be ready..."
sleep 10

# Health check
echo ""
echo "=== Health Check ==="
if curl -sf http://localhost:5537/health > /dev/null; then
    echo "Health check: PASSED"
    curl -s http://localhost:5537/health | python3 -m json.tool
else
    echo "Health check: FAILED"
    echo "Check logs with: docker compose logs"
    exit 1
fi

echo ""
echo "=== Deployment Complete ==="
echo "Local access: http://localhost:5537"
echo "External access: https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  View logs: docker compose logs -f"
echo "  Stop: docker compose down"
echo "  Restart: docker compose restart"
