# MoA Swarm Architecture

> **Enterprise-Grade Multi-Agent Swarm System with Mixture of Agents (MoA) Logic**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED.svg)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

The **MoA Swarm Architecture** is a production-ready multi-agent system that leverages Mixture of Agents (MoA) patterns to execute complex AI tasks with parallel processing, browser automation, and intelligent orchestration.

### What is MoA?

**Mixture of Agents (MoA)** is an architectural pattern where multiple AI models (proposers) generate diverse responses to the same input, and an aggregator model synthesizes these outputs into a refined, coherent result. This approach:

- **Improves quality** by combining diverse model perspectives
- **Reduces hallucination** through cross-validation
- **Enables specialization** with different models for different tasks
- **Scales horizontally** by adding more proposer agents

### Key Capabilities

- 🔄 **Parallel Model Calls** — Fire multiple LLM requests concurrently via `moa_batch_call()`
- 🧠 **Intelligent Aggregation** — Synthesize proposer outputs via `moa_aggregate()`
- 🌐 **Browser Automation** — Control browsers via Chrome DevTools Protocol and browserbase
- 🖥️ **Desktop Control** — Full OS-level automation via os-ai-computer-use
- 🔍 **Web Search** — Integrated search via anysearch MCP
- 👁️ **Vision Processing** — Screenshot analysis and OCR capabilities
- 📊 **Token Optimization** — Compress shell output via ztk
- 🏥 **Health Monitoring** — Built-in health checks and recovery

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOA SWARM ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Proposer 1  │    │  Proposer 2  │    │  Proposer N  │      │
│  │  (GLM-4.7)  │    │  (Claude-3)  │    │  (GPT-4)     │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │   Aggregator    │                          │
│                    │   (Best Model)  │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│  ┌──────────────────────────┼──────────────────────────┐       │
│  │                    ORCHESTRATOR                     │       │
│  │              (Swarm MCP + Router)                   │       │
│  └──────────────────────────┬──────────────────────────┘       │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         │                   │                   │               │
│  ┌──────▼───────┐    ┌──────▼───────┐    ┌──────▼───────┐      │
│  │   Browser    │    │   Desktop    │    │   Web Search  │      │
│  │   Agent      │    │   Agent      │    │   Agent       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Breakdown

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **Orchestration** | swarm-mcp | Node.js/Python | Spawn agents, manage pipelines, handle failures |
| **Perception** | anysearch + vision MCP | API | Web search, image analysis, screenshot understanding |
| **Action (Browser)** | Chrome DevTools MCP | Chrome Protocol | Precise browser control, DOM inspection, JS execution |
| **Action (Desktop)** | os-ai-computer-use | Python | Full desktop automation, mouse/keyboard control |
| **Infrastructure** | browserbase | SDK | Stealth proxies, session management, anti-bot |
| **Token Optimization** | ztk | Binary | Compress shell output, reduce token usage |
| **Model Layer** | heart_bleed.py | Python | Core model call function, MoA proposer/aggregator |

---

## Features

### Core Features

#### 1. Heart Bleed Model Function
The foundation of all model interactions. Provides both synchronous and asynchronous calling patterns.

```python
from core.heart_bleed import heart_bleed_call, heart_bleed_call_async, moa_batch_call, moa_aggregate

# Single synchronous call
result = heart_bleed_call(
    messages=[{"role": "user", "content": "Summarize this diff"}],
    model="glm-4.7-flash",
    max_tokens=400
)

# Async parallel calls (MoA proposer phase)
responses = await moa_batch_call([
    {"messages": [{"role": "user", "content": "Analyze from security angle"}], "model": "claude-3-opus"},
    {"messages": [{"role": "user", "content": "Analyze from performance angle"}], "model": "gpt-4"},
    {"messages": [{"role": "user", "content": "Analyze from UX angle"}], "model": "glm-4.7-flash"}
])

# Aggregate proposer outputs
final = moa_aggregate(responses, aggregator_config)
```

#### 2. MoA Proposer/Aggregator Pipeline
- **Proposer Phase:** Fire N model calls in parallel
- **Aggregation Phase:** Synthesize outputs into refined result
- **Built-in error handling** and retry logic
- **Metadata tracking** (latency, token usage)

#### 3. Browser Automation
- **Chrome DevTools MCP:** Screenshot capture, DOM inspection, JS execution
- **browserbase:** Stealth proxies, persistent sessions, anti-bot protection
- **OpenTabs:** API-first browser control

#### 4. Web Search & Vision
- **anysearch MCP:** Integrated web search
- **Vision MCP:** Screenshot analysis, OCR, element detection

#### 5. Token Optimization
- **ztk:** Compress shell command output before LLM processing
- **Token tracking:** Monitor usage across all agents

---

## Prerequisites

### System Requirements

- **OS:** Linux (Ubuntu 20.04+ recommended) or macOS
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 20GB free space
- **CPU:** 4 cores minimum

### Software Requirements

- Python 3.10+
- Node.js 18+
- Docker 20.10+
- Docker Compose v2+
- Git 2.30+

### API Keys Required

| Service | Purpose | Get Key At |
|---------|---------|------------|
| OpenAI | GPT-4, GPT-3.5 | https://platform.openai.com/api-keys |
| Anthropic | Claude 3 | https://console.anthropic.com/ |
| GLM (Zhipu) | GLM-4.7-flash | https://open.bigmodel.cn/ |
| Browserbase | Stealth browsers | https://browserbase.com/ |

---

## Installation

### Quick Start (Automated)

```bash
# Clone the repository
git clone https://github.com/your-org/moa-swarm.git
cd moa-swarm

# Run automated setup
chmod +x scripts/install_deps.sh
./scripts/install_deps.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the swarm
chmod +x scripts/run_swarm.sh
./scripts/run_swarm.sh
```

### Manual Installation

#### Step 1: System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools
sudo apt install -y build-essential curl wget git

# Install Python 3.10+
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

#### Step 2: Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Project Setup

```bash
# Create project structure
mkdir -p core orchestrator perception action utils config/agents tests/{unit,integration,smoke} scripts docker

# Initialize Python packages
touch core/__init__.py orchestrator/__init__.py perception/__init__.py action/__init__.py utils/__init__.py
```

#### Step 4: Install ztk

```bash
# Download ztk binary (adjust URL for your architecture)
wget https://github.com/your-org/ztk/releases/latest/download/ztk-linux-amd64
chmod +x ztk-linux-amd64
sudo mv ztk-linux-amd64 /usr/local/bin/ztk
```

#### Step 5: Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GLM_API_KEY=your_glm_key_here
BROWSERBASE_API_KEY=your_browserbase_key_here

# Model Endpoints
DEFAULT_MODEL_ENDPOINT=https://api.openai.com/v1/chat/completions
GLM_ENDPOINT=https://open.bigmodel.cn/api/paas/v4/chat/completions

# VPS Configuration
VPS_IP=your_vps_ip_here

# Docker
DOCKER_NETWORK=moa-swarm-net

# Swarm Configuration
AGENT_POOL_SIZE=5
TASK_TIMEOUT=60
RETRY_ATTEMPTS=3
EOF
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `GLM_API_KEY` | - | GLM (Zhipu) API key |
| `BROWSERBASE_API_KEY` | - | Browserbase API key |
| `DEFAULT_MODEL_ENDPOINT` | `https://api.openai.com/v1/chat/completions` | Default model API endpoint |
| `GLM_ENDPOINT` | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | GLM API endpoint |
| `AGENT_POOL_SIZE` | `5` | Number of concurrent agents |
| `TASK_TIMEOUT` | `60` | Task timeout in seconds |
| `RETRY_ATTEMPTS` | `3` | Number of retry attempts |
| `HEALTH_CHECK_INTERVAL` | `30` | Health check interval in seconds |

### Agent Configuration

#### Proposer Config (`config/agents/proposer_config.json`)

```json
{
  "models": ["glm-4.7-flash", "claude-3-opus", "gpt-4"],
  "default_model": "glm-4.7-flash",
  "max_tokens": 400,
  "temperature": 0.7,
  "reasoning_effort": "none",
  "timeout": 30,
  "system_prompts": {
    "security": "Analyze from a security perspective, focusing on vulnerabilities and risks.",
    "performance": "Analyze from a performance perspective, focusing on efficiency and optimization.",
    "ux": "Analyze from a user experience perspective, focusing on usability and accessibility."
  }
}
```

#### Aggregator Config (`config/agents/aggregator_config.json`)

```json
{
  "model": "claude-3-opus",
  "max_tokens": 800,
  "temperature": 0.3,
  "reasoning_effort": "medium",
  "timeout": 60,
  "system_prompt": "You are an expert aggregator. Synthesize the proposer outputs into a single, coherent, refined response. Resolve contradictions, combine strengths, discard weaknesses."
}
```

#### Swarm Config (`config/swarm_config.json`)

```json
{
  "pool_size": 5,
  "task_timeout": 60,
  "retry_attempts": 3,
  "health_check_interval": 30,
  "routing": {
    "single_call": "direct",
    "batch_call": "parallel",
    "pipeline": "sequential"
  },
  "fallback": {
    "enabled": true,
    "fallback_model": "glm-4.7-flash",
    "max_retries": 2
  }
}
```

---

## Usage

### Basic Usage

```python
from core.heart_bleed import heart_bleed_call

# Simple model call
result = heart_bleed_call(
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    model="glm-4.7-flash"
)

print(result["choices"][0]["message"]["content"])
# Output: "The capital of France is Paris."
```

### MoA Workflow

```python
import asyncio
from core.heart_bleed import moa_batch_call, moa_aggregate, HeartBleedConfig

async def moa_workflow():
    # Step 1: Proposer Phase - Fire multiple models in parallel
    proposer_tasks = [
        {"messages": [{"role": "user", "content": "Review this code for security issues"}], "model": "claude-3-opus"},
        {"messages": [{"role": "user", "content": "Review this code for performance issues"}], "model": "gpt-4"},
        {"messages": [{"role": "user", "content": "Review this code for readability issues"}], "model": "glm-4.7-flash"},
    ]
    
    proposer_responses = await moa_batch_call(proposer_tasks)
    
    # Step 2: Aggregation Phase - Synthesize outputs
    aggregator_config = HeartBleedConfig(
        model="claude-3-opus",
        max_tokens=800,
        temperature=0.3
    )
    
    final_response = moa_aggregate(proposer_responses, aggregator_config)
    
    return final_response["choices"][0]["message"]["content"]

# Run the workflow
result = asyncio.run(moa_workflow())
print(result)
```

### Browser Automation

```python
from action.browser import BrowserAgent

# Initialize browser agent
browser = BrowserAgent()

# Navigate to a page
await browser.navigate("https://example.com")

# Take a screenshot
screenshot = await browser.screenshot()

# Click an element
await browser.click("button#submit")

# Fill a form
await browser.fill("input#email", "user@example.com")

# Execute JavaScript
result = await browser.execute_js("document.title")
```

### Web Search

```python
from perception.web_search import WebSearch

# Initialize search agent
search = WebSearch()

# Perform a search
results = await search.search("MoA architecture AI")

# Process results
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}\n")
```

---

## API Reference

### `heart_bleed.py`

#### `HeartBleedConfig`

```python
@dataclass
class HeartBleedConfig:
    model: str = "glm-4.7-flash"
    reasoning_effort: str = "none"  # none | low | medium | high
    max_tokens: int = 400
    temperature: float = 0.7
    api_url: str = DEFAULT_API_URL
    api_key: Optional[str] = None
    timeout: int = 30
```

#### `heart_bleed_call(messages, config=None, **overrides)`

Synchronous model call.

**Parameters:**
- `messages` (List[Dict[str, str]]): List of message dicts with `role` and `content`
- `config` (HeartBleedConfig, optional): Configuration object
- `**overrides`: Override any config field inline

**Returns:**
- `Dict[str, Any]`: API response with `_meta` metadata

#### `heart_bleed_call_async(messages, config=None, **overrides)`

Async version for concurrent calls.

**Parameters:**
- Same as `heart_bleed_call`

**Returns:**
- `Dict[str, Any]`: API response with `_meta` metadata

#### `moa_batch_call(tasks, config=None)`

Fire multiple model calls in parallel.

**Parameters:**
- `tasks` (List[Dict[str, Any]]): List of task dicts, each with `messages` and optional overrides
- `config` (HeartBleedConfig, optional): Base configuration

**Returns:**
- `List[Dict[str, Any]]`: List of responses in same order as tasks

#### `moa_aggregate(proposer_responses, aggregator_config)`

Synthesize proposer outputs.

**Parameters:**
- `proposer_responses` (List[Dict[str, Any]]): List of proposer responses
- `aggregator_config` (HeartBleedConfig): Aggregator model configuration

**Returns:**
- `Dict[str, Any]`: Aggregated response

---

## Project Structure

```
moa-swarm/
├── .env                      # Secrets and Config (NOT committed)
├── .env.example              # Template for .env
├── plan.md                   # Project plan with to-do list
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
│
├── core/                     # Core model layer
│   ├── __init__.py
│   ├── heart_bleed.py        # Model call function
│   ├── config.py             # Configuration management
│   └── models.py             # Pydantic models
│
├── orchestrator/             # Swarm orchestration
│   ├── __init__.py
│   ├── router.py             # Task routing
│   ├── agent_pool.py         # Agent management
│   └── health.py             # Health checks
│
├── perception/               # Web search & vision
│   ├── __init__.py
│   ├── web_search.py         # Search interface
│   └── vision.py             # Image analysis
│
├── action/                   # Browser & desktop automation
│   ├── __init__.py
│   ├── browser.py            # Browser control
│   └── desktop.py            # Desktop automation
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── token_optimizer.py    # ztk integration
│   └── logging.py            # Structured logging
│
├── config/                   # Configuration files
│   ├── agents/
│   │   ├── proposer_config.json
│   │   └── aggregator_config.json
│   └── swarm_config.json
│
├── scripts/                  # Automation scripts
│   ├── install_deps.sh
│   ├── setup_docker.sh
│   └── run_swarm.sh
│
├── tests/                    # Test suite
│   ├── unit/
│   ├── integration/
│   └── smoke/
│
└── docker/                   # Docker configurations
    ├── Dockerfile.agent
    ├── Dockerfile.orchestrator
    └── docker-compose.yml
```

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/moa-swarm.git
cd moa-swarm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python3 tests/run_all_tests.py

# Run validation
python3 scripts/validate_all.py

# Check API configuration
python3 scripts/check_api_config.py

# Test MCP connection
python3 scripts/test_mcp_connection.py
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Write docstrings for all public functions
- Keep functions under 50 lines
- Maximum line length: 88 characters (Black formatter)

---

## Troubleshooting

### Common Issues

#### 1. Docker Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

#### 2. Python Version Issues

```bash
# Check Python version
python3 --version

# Install Python 3.10 if needed
sudo apt install python3.10 python3.10-venv
```

#### 3. API Key Errors

```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GLM_API_KEY

# Re-source .env file
source .env

# Run config checker
python3 scripts/check_api_config.py
```

#### 4. Port Already in Use

```bash
# Find process using port
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### 5. Memory Issues

```bash
# Check memory usage
free -h

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Logs

```bash
# View Docker container logs
docker logs moa-swarm-orchestrator

# View application logs
tail -f logs/swarm.log

# View health check logs
docker exec moa-swarm-orchestrator cat /var/log/health.log
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug

# Run with verbose output
python -m core.heart_bleed --verbose

# Run all tests
python3 tests/run_all_tests.py

# Run validation
python3 scripts/validate_all.py --verbose

# Test MCP connection
python3 scripts/test_mcp_connection.py --verbose
```

---

## Performance Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| Single Call Latency | ~2-5s | Depends on model and token count |
| MoA Proposer Phase (3 models) | ~5-8s | Parallel execution |
| Aggregation Phase | ~3-6s | Depends on proposer output size |
| Total MoA Workflow | ~10-15s | End-to-end |
| Token Compression (ztk) | ~40-60% | Varies by output type |
| Unit Tests | 176/176 passing | 100% pass rate |
| MCP Tools | 10 tools | Full protocol support |
| MCP Resources | 5 resources | Config, agents, health, tasks, models |

---

## Roadmap

- [x] **v1.0** — Core MoA implementation with heart_bleed.py
- [x] **v1.1** — Browser automation integration
- [x] **v1.2** — Web search and vision capabilities
- [x] **v1.3** — Desktop automation support
- [x] **v1.4** — Token optimization with ztk
- [x] **v1.5** — Production monitoring and observability
- [x] **v1.6** — MCP server for external AI access
- [x] **v1.7** — Comprehensive unit tests (176 tests)
- [x] **v1.8** — Validation and health check scripts
- [ ] **v2.0** — Multi-node VPS deployment
- [ ] **v2.1** — Auto-scaling agent pools
- [ ] **v2.2** — Custom model fine-tuning integration

---

## Security

- **Never commit API keys** — Use `.env` file (add to `.gitignore`)
- **Use environment variables** for all secrets
- **Enable HTTPS** for all API endpoints
- **Rotate API keys** regularly
- **Monitor usage** for unexpected patterns

```gitignore
# .gitignore
.env
*.pyc
__pycache__/
venv/
*.egg-info/
dist/
build/
logs/
.test_*
```

## Validation

### Run All Checks

```bash
# Comprehensive validation (all tests)
python3 scripts/validate_all.py

# Quick validation (skip unit tests)
python3 scripts/validate_all.py --quick

# Verbose output
python3 scripts/validate_all.py --verbose
```

### Individual Checks

```bash
# API configuration check
python3 scripts/check_api_config.py

# MCP connection test
python3 scripts/test_mcp_connection.py

# Unit tests
python3 tests/run_all_tests.py
```

### Expected Results

```
✅ API Configuration: 72/72 checks passed
✅ MCP Connection: 16/16 tests passed
✅ Unit Tests: 176/176 tests passed
✅ All validations passed!
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation:** [docs.moa-swarm.dev](https://docs.moa-swarm.dev)
- **Issues:** [GitHub Issues](https://github.com/your-org/moa-swarm/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-org/moa-swarm/discussions)
- **Email:** support@moa-swarm.dev

---

## Acknowledgments

- [swarm-mcp](https://github.com/your-org/swarm-mcp) — Agent orchestration
- [browserbase](https://browserbase.com/) — Stealth browser infrastructure
- [ztk](https://github.com/your-org/ztk) — Token optimization
- [os-ai-computer-use](https://github.com/777genius/os-ai-computer-use) — Desktop automation

---

*Built with ❤️ by the MoA Swarm Team*

*Generated by Codebuff 🤖*
