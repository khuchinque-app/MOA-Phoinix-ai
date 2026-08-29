#!/bin/bash
# ============================================================================
# MoA Swarm Architecture - Docker Setup Script
# ============================================================================
# This script sets up Docker containers for the MoA Swarm system.
# Run this script from the project root directory.
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ============================================================================
# Configuration
# ============================================================================

IMAGE_PREFIX="moa-swarm"
NETWORK_NAME="moa-swarm-net"
AGENT_IMAGE="${IMAGE_PREFIX}-agent"
ORCHESTRATOR_IMAGE="${IMAGE_PREFIX}-orchestrator"

# ============================================================================
# Check Docker
# ============================================================================

print_header "Checking Docker"

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

print_success "Docker is installed and running"

# ============================================================================
# Create Docker Network
# ============================================================================

print_header "Creating Docker Network"

if docker network inspect "$NETWORK_NAME" &> /dev/null; then
    print_success "Network '$NETWORK_NAME' already exists"
else
    docker network create "$NETWORK_NAME"
    print_success "Network '$NETWORK_NAME' created"
fi

# ============================================================================
# Create Dockerfiles
# ============================================================================

print_header "Creating Dockerfiles"

# Agent Dockerfile
cat > docker/Dockerfile.agent << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium

# Copy application code
COPY core/ ./core/
COPY orchestrator/ ./orchestrator/
COPY perception/ ./perception/
COPY action/ ./action/
COPY utils/ ./utils/
COPY config/ ./config/

# Copy environment file
COPY .env* ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "-m", "orchestrator.router"]
EOF

print_success "Agent Dockerfile created"

# Orchestrator Dockerfile
cat > docker/Dockerfile.orchestrator << 'EOF'
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY orchestrator/ ./orchestrator/
COPY perception/ ./perception/
COPY action/ ./action/
COPY utils/ ./utils/
COPY config/ ./config/

# Copy environment file
COPY .env* ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose ports
EXPOSE 8080

# Default command
CMD ["python", "-m", "orchestrator.router", "--server"]
EOF

print_success "Orchestrator Dockerfile created"

# ============================================================================
# Docker Compose
# ============================================================================

print_header "Creating Docker Compose Configuration"

cat > docker/docker-compose.yml << EOF
version: '3.8'

services:
  orchestrator:
    build:
      context: ..
      dockerfile: docker/Dockerfile.orchestrator
    container_name: ${ORCHESTRATOR_IMAGE}
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - LOG_LEVEL=INFO
    volumes:
      - ../logs:/app/logs
      - ../config:/app/config
    networks:
      - ${NETWORK_NAME}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  agent-1:
    build:
      context: ..
      dockerfile: docker/Dockerfile.agent
    container_name: ${AGENT_IMAGE}-1
    environment:
      - AGENT_ID=agent-1
      - AGENT_ROLE=proposer
      - MODEL=glm-4.7-flash
    volumes:
      - ../logs:/app/logs
      - ../config:/app/config
    networks:
      - ${NETWORK_NAME}
    restart: unless-stopped
    depends_on:
      orchestrator:
        condition: service_healthy

  agent-2:
    build:
      context: ..
      dockerfile: docker/Dockerfile.agent
    container_name: ${AGENT_IMAGE}-2
    environment:
      - AGENT_ID=agent-2
      - AGENT_ROLE=proposer
      - MODEL=claude-3-opus
    volumes:
      - ../logs:/app/logs
      - ../config:/app/config
    networks:
      - ${NETWORK_NAME}
    restart: unless-stopped
    depends_on:
      orchestrator:
        condition: service_healthy

  agent-3:
    build:
      context: ..
      dockerfile: docker/Dockerfile.agent
    container_name: ${AGENT_IMAGE}-3
    environment:
      - AGENT_ID=agent-3
      - AGENT_ROLE=proposer
      - MODEL=gpt-4
    volumes:
      - ../logs:/app/logs
      - ../config:/app/config
    networks:
      - ${NETWORK_NAME}
    restart: unless-stopped
    depends_on:
      orchestrator:
        condition: service_healthy

  aggregator:
    build:
      context: ..
      dockerfile: docker/Dockerfile.agent
    container_name: ${AGENT_IMAGE}-aggregator
    environment:
      - AGENT_ID=aggregator
      - AGENT_ROLE=aggregator
      - MODEL=claude-3-opus
    volumes:
      - ../logs:/app/logs
      - ../config:/app/config
    networks:
      - ${NETWORK_NAME}
    restart: unless-stopped
    depends_on:
      orchestrator:
        condition: service_healthy

networks:
  ${NETWORK_NAME}:
    driver: bridge
EOF

print_success "Docker Compose configuration created"

# ============================================================================
# Build Docker Images
# ============================================================================

print_header "Building Docker Images"

# Build agent image
print_warning "Building agent image..."
docker build -t "$AGENT_IMAGE" -f docker/Dockerfile.agent ..
print_success "Agent image built"

# Build orchestrator image
print_warning "Building orchestrator image..."
docker build -t "$ORCHESTRATOR_IMAGE" -f docker/Dockerfile.orchestrator ..
print_success "Orchestrator image built"

# ============================================================================
# Verification
# ============================================================================

print_header "Verification"

echo "Checking Docker images..."
docker images | grep "$IMAGE_PREFIX"

echo ""
echo "Checking Docker network..."
docker network inspect "$NETWORK_NAME" | grep -E '"Name"|"Driver"' || true

# ============================================================================
# Completion
# ============================================================================

print_header "Docker Setup Complete"

echo -e "${GREEN}Docker has been configured successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the swarm: cd docker && docker-compose up -d"
echo "  2. View logs: docker-compose logs -f"
echo "  3. Stop the swarm: docker-compose down"
echo ""
echo "Individual container management:"
echo "  - View running containers: docker ps"
echo "  - Enter a container: docker exec -it <container_name> bash"
echo "  - View container logs: docker logs <container_name>"
echo ""

# ============================================================================
# End of Script
# ============================================================================
