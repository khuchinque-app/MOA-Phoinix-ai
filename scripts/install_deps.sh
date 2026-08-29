#!/bin/bash
# ============================================================================
# MoA Swarm Architecture - Dependency Installation Script
# ============================================================================
# This script installs all required dependencies for the MoA Swarm system.
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

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# System Check
# ============================================================================

print_header "System Information"

echo "Operating System: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "Kernel: $(uname -r)"

# ============================================================================
# Prerequisites Check
# ============================================================================

print_header "Checking Prerequisites"

# Check for curl
if check_command curl; then
    print_success "curl is installed"
else
    print_warning "curl not found. Installing..."
    sudo apt-get update && sudo apt-get install -y curl
fi

# Check for git
if check_command git; then
    print_success "git is installed"
else
    print_warning "git not found. Installing..."
    sudo apt-get update && sudo apt-get install -y git
fi

# ============================================================================
# Python Installation
# ============================================================================

print_header "Installing Python"

if check_command python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION is installed"
else
    print_warning "Python3 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
    print_success "Python3 installed"
fi

# Check Python version (requires 3.10+)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    print_success "Python version is compatible (3.10+)"
else
    print_warning "Python 3.10+ recommended. Current: Python $PYTHON_MAJOR.$PYTHON_MINOR"
fi

# ============================================================================
# Node.js Installation
# ============================================================================

print_header "Installing Node.js"

if check_command node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION is installed"
else
    print_warning "Node.js not found. Installing via nvm..."
    
    # Install nvm if not present
    if [ ! -d "$HOME/.nvm" ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    fi
    
    # Load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    # Install Node.js
    nvm install 18
    nvm use 18
    
    print_success "Node.js installed"
fi

# ============================================================================
# Docker Installation
# ============================================================================

print_header "Installing Docker"

if check_command docker; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    print_success "Docker $DOCKER_VERSION is installed"
else
    print_warning "Docker not found. Installing..."
    
    # Install Docker
    curl -fsSL https://get.docker.com | sh
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed"
    print_warning "Please log out and back in for group changes to take effect"
fi

# Check Docker Compose
if check_command docker-compose || docker compose version &> /dev/null; then
    print_success "Docker Compose is installed"
else
    print_warning "Docker Compose not found. Installing..."
    sudo apt-get install -y docker-compose-plugin
    print_success "Docker Compose installed"
fi

# ============================================================================
# Python Virtual Environment
# ============================================================================

print_header "Setting Up Python Virtual Environment"

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    print_success "Virtual environment already exists"
else
    print_warning "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# ============================================================================
# Python Dependencies
# ============================================================================

print_header "Installing Python Dependencies"

# Upgrade pip
pip install --upgrade pip
print_success "pip upgraded"

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_warning "requirements.txt not found. Installing core dependencies..."
    pip install requests aiohttp python-dotenv pydantic rich
fi

# ============================================================================
# Playwright Browser Installation
# ============================================================================

print_header "Installing Playwright Browsers"

if check_command playwright; then
    playwright install chromium
    print_success "Playwright browsers installed"
else
    print_warning "Playwright CLI not found. Installing browsers via Python..."
    python3 -m playwright install chromium
    print_success "Playwright browsers installed"
fi

# ============================================================================
# ztk Installation
# ============================================================================

print_header "Installing ztk (Token Optimizer)"

if check_command ztk; then
    print_success "ztk is already installed"
else
    print_warning "ztk not found. Attempting to install..."
    
    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ZTK_ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ZTK_ARCH="arm64"
    else
        ZTK_ARCH="amd64"
    fi
    
    # Try to download ztk (placeholder URL - replace with actual)
    ZTK_URL="https://github.com/your-org/ztk/releases/latest/download/ztk-linux-${ZTK_ARCH}"
    
    if curl -fsSL "$ZTK_URL" -o /tmp/ztk; then
        chmod +x /tmp/ztk
        sudo mv /tmp/ztk /usr/local/bin/ztk
        print_success "ztk installed"
    else
        print_warning "Could not install ztk automatically. Please install manually."
    fi
fi

# ============================================================================
# Environment Configuration
# ============================================================================

print_header "Setting Up Environment Configuration"

if [ -f ".env" ]; then
    print_success ".env file already exists"
elif [ -f ".env.example" ]; then
    cp .env.example .env
    print_success ".env file created from template"
    print_warning "Please edit .env with your API keys"
else
    print_warning ".env.example not found. Creating minimal .env file..."
    cat > .env << 'EOF'
# MoA Swarm Environment Configuration
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GLM_API_KEY=
BROWSERBASE_API_KEY=
EOF
    print_success ".env file created"
fi

# ============================================================================
# Directory Setup
# ============================================================================

print_header "Setting Up Directories"

# Create necessary directories
mkdir -p logs
mkdir -p screenshots
mkdir -p cache

print_success "Directories created"

# ============================================================================
# Verification
# ============================================================================

print_header "Verification"

echo "Checking installed components..."

# Python
if check_command python3; then
    print_success "Python: $(python3 --version)"
fi

# pip
if check_command pip; then
    print_success "pip: $(pip --version | awk '{print $1, $2}')"
fi

# Node.js
if check_command node; then
    print_success "Node.js: $(node --version)"
fi

# Docker
if check_command docker; then
    print_success "Docker: $(docker --version | awk '{print $3}' | tr -d ',')"
fi

# ztk
if check_command ztk; then
    print_success "ztk: installed"
else
    print_warning "ztk: not installed (optional)"
fi

# ============================================================================
# Completion
# ============================================================================

print_header "Installation Complete"

echo -e "${GREEN}All dependencies have been installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python -m core.heart_bleed (to test)"
echo "  4. Run: ./scripts/run_swarm.sh (to start the swarm)"
echo ""
echo -e "${YELLOW}Note: If you just installed Docker, please log out and back in${NC}"
echo -e "${YELLOW}for group changes to take effect.${NC}"
echo ""

# ============================================================================
# End of Script
# ============================================================================
