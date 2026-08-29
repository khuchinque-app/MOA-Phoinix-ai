#!/bin/bash
# ============================================================================
# MoA Swarm Architecture - Swarm Startup Script
# ============================================================================
# This script starts the MoA Swarm system.
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
USE_DOCKER=false
MODE="local"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            USE_DOCKER=true
            MODE="docker"
            shift
            ;;
        --local)
            USE_DOCKER=false
            MODE="local"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker    Start swarm using Docker containers"
            echo "  --local     Start swarm locally (default)"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# Pre-flight Checks
# ============================================================================

print_header "Pre-flight Checks"

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please edit .env with your API keys before continuing"
    else
        print_error ".env file not found and no template available"
        exit 1
    fi
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# ============================================================================
# Docker Mode
# ============================================================================

if [ "$USE_DOCKER" = true ]; then
    print_header "Starting Swarm in Docker Mode"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    # Build and start containers
    print_warning "Building Docker images..."
    cd docker
    
    # Build images
    docker compose build
    
    print_success "Docker images built"
    
    # Start containers
    print_warning "Starting containers..."
    docker compose up -d
    
    print_success "Containers started"
    
    # Wait for health checks
    print_warning "Waiting for services to become healthy..."
    sleep 10
    
    # Check container status
    docker compose ps
    
    cd ..
    
    print_success "Swarm started in Docker mode"
    echo ""
    echo "Useful commands:"
    echo "  - View logs: cd docker && docker compose logs -f"
    echo "  - Stop swarm: cd docker && docker compose down"
    echo "  - View containers: docker ps"
    
# ============================================================================
# Local Mode
# ============================================================================

else
    print_header "Starting Swarm in Local Mode"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed"
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -f "venv/lib/python*/site-packages/requests/__init__.py" ]; then
        print_warning "Installing Python dependencies..."
        pip install -r requirements.txt
    fi
    
    # Create log directory
    mkdir -p logs
    
    print_success "Starting MoA Swarm locally..."
    echo ""
    echo "Press Ctrl+C to stop the swarm"
    echo ""
    
    # Start the orchestrator
    python3 -m orchestrator.router
fi

# ============================================================================
# Cleanup Function
# ============================================================================

cleanup() {
    echo ""
    print_header "Shutting Down"
    
    if [ "$USE_DOCKER" = true ]; then
        cd docker
        docker compose down
        cd ..
        print_success "Docker containers stopped"
    else
        print_success "Local swarm stopped"
    fi
    
    print_success "Shutdown complete"
}

# Trap Ctrl+C
trap cleanup EXIT INT TERM

# ============================================================================
# Wait for Exit (Docker mode keeps running)
# ============================================================================

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "Swarm is running in the background."
    echo "Use 'cd docker && docker compose logs -f' to view logs"
    echo "Use 'cd docker && docker compose down' to stop"
    
    # Keep script running to allow Ctrl+C
    while true; do
        sleep 60
    done
fi

# ============================================================================
# End of Script
# ============================================================================
