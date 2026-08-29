# MoA Swarm Architecture — Master Blueprint

> **Project:** Multi-Agent Swarm with Mixture of Agents (MoA) Logic
> **Status:** 🟢 Installed on Ubuntu
> **Last Updated:** August 29, 2026 — 16:50 UTC
> **Environment:** Ubuntu (Real VPS, not WSL)

---

## Installation Status

| Tool | Purpose | Status | Location |
|------|---------|--------|----------|
| **ztk** | Token compression (78%+) | ✅ Installed v0.3.1 | `~/.local/bin/ztk` |
| **swarm-mcp** | Agent orchestration | ✅ Installed v0.9.5 | npm global |
| **vision-mcp** | Visual understanding | ✅ Installed v0.1.0 | npm global |
| **browserbase** | Browser sessions | ✅ Installed v1.18.0 | pip |
| **anysearch** | Web search | ✅ Installed v0.2.2 | pip |
| **Chrome DevTools MCP** | Browser control | ✅ Installed | mcp-chrome-bridge |
| **graph-engineering** | Memory architecture | ✅ Cloned | vendor/graph-engineering |
| **agent-harness** | Workflow framework | ✅ Cloned | vendor/agent-harness |
| **playwright** | Browser automation | ✅ Installed v1.62.1 | npm global |

---

## Environment

```
OS: Ubuntu (Real VPS)
Python: 3.10.12
Node.js: v24.19.0
npm: 11.17.0
User: chinque
Home: /home/chinque
```

---

## Tool Verification

### ztk (Token Compression)
```bash
$ ztk --version
ztk 0.3.1

$ ztk run echo 'test'
test
```

### swarm-mcp (Agent Orchestration)
```bash
$ which swarm-mcp
/home/chinque/.nvm/versions/node/v24.19.0/bin/swarm-mcp
```

### vision-mcp (Visual Understanding)
```bash
$ which vision-mcp
/home/chinque/.nvm/versions/node/v24.19.0/bin/vision-mcp
```

### browserbase (Browser Sessions)
```python
>>> import browserbase
>>> print(browserbase.__version__)
1.18.0
```

### anysearch (Web Search)
```python
>>> import anysearch
>>> print('OK')
OK
```

### Chrome DevTools MCP
```bash
$ cat .mcp.json
{
  "mcpServers": {
    "chrome-mcp": {
      "command": "node",
      "args": ["/home/chinque/.nvm/versions/node/v24.19.0/lib/node_modules/mcp-chrome-bridge/dist/mcp/mcp-server-stdio.js"]
    }
  }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOA SWARM ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 KNOWLEDGE LAYER                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  Knowledge   │  │  Task Graph  │  │  Collective  │  │   │
│  │  │  Graph       │  │  (Execution) │  │  Memory      │  │   │
│  │  │  (Memory)    │  │              │  │  (Shared)    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 ORCHESTRATION LAYER                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  swarm-mcp   │  │  Agent Pool  │  │  Health      │  │   │
│  │  │  (Installed) │  │  Manager     │  │  Monitor     │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 PERCEPTION LAYER                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  anysearch   │  │  vision-mcp  │  │  web_search  │  │   │
│  │  │  (Installed) │  │  (Installed) │  │  (Python)    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 ACTION LAYER                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  Chrome      │  │  browserbase │  │  playwright  │  │   │
│  │  │  DevTools    │  │  (Installed) │  │  (Installed) │  │   │
│  │  │  (Installed) │  │              │  │              │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 TOOL LAYER                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  ztk         │  │  heart_bleed │  │  Agent       │  │   │
│  │  │  (Installed) │  │  (Python)    │  │  Harness     │  │   │
│  │  │  v0.3.1      │  │              │  │  (Cloned)    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# 1. Navigate to project
cd /home/chinque

# 2. Activate Python environment
source ~/.local/bin/activate 2>/dev/null || true

# 3. Run ztk
ztk run echo 'Hello from MoA Swarm'

# 4. Run swarm-mcp
swarm-mcp --help

# 5. Run vision-mcp
vision-mcp --help

# 6. Start Chrome DevTools MCP
node /home/chinque/.nvm/versions/node/v24.19.0/lib/node_modules/mcp-chrome-bridge/dist/mcp/mcp-server-stdio.js
```

---

## MCP Server Configuration

### .mcp.json
```json
{
  "mcpServers": {
    "chrome-mcp": {
      "command": "node",
      "args": ["/home/chinque/.nvm/versions/node/v24.19.0/lib/node_modules/mcp-chrome-bridge/dist/mcp/mcp-server-stdio.js"]
    }
  }
}
```

---

## File Structure

```
/home/chinque/
├── .env                      # Secrets and Config
├── .env.example              # Template for .env
├── .mcp.json                 # MCP server configuration
├── plan.md                   # This file
├── README.md                 # Documentation
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point
├── ztk                       # Token compression binary
│
├── core/                     # Core model layer
│   ├── heart_bleed.py        # Model call function
│   ├── config.py             # Configuration
│   ├── models.py             # Pydantic models
│   └── memory.py             # Graph-engineering memory
│
├── orchestrator/             # Swarm orchestration
│   ├── router.py             # Task routing
│   ├── agent_pool.py         # Agent management
│   ├── health.py             # Health checks
│   └── mcp_server.py         # MCP server
│
├── perception/               # Web search & vision
│   ├── web_search.py         # Search interface
│   └── vision.py             # Image analysis
│
├── action/                   # Browser automation
│   ├── browser.py            # Browser control
│   └── desktop.py            # Desktop automation
│
├── utils/                    # Utilities
│   ├── token_optimizer.py    # ztk integration
│   └── logging.py            # Structured logging
│
├── config/                   # Configuration files
│   └── agents/
│       ├── proposer_config.json
│       └── aggregator_config.json
│
├── vendor/                   # External tools
│   ├── graph-engineering/    # Memory architecture
│   └── agent-harness/        # Workflow framework
│
├── scripts/                  # Automation scripts
│   ├── install_deps.sh
│   ├── setup_docker.sh
│   ├── run_swarm.sh
│   ├── check_api_config.py
│   └── validate_all.py
│
├── tests/                    # Verification suite
│   ├── unit/
│   └── run_all_tests.py
│
└── docker/                   # Docker configurations
    ├── Dockerfile.agent
    ├── Dockerfile.orchestrator
    └── docker-compose.yml
```

---

## Verification Commands

```bash
# Verify ztk
ztk --version
ztk run ls -la

# Verify swarm-mcp
which swarm-mcp
swarm-mcp --help

# Verify vision-mcp
which vision-mcp
vision-mcp --help

# Verify browserbase
python3 -c "import browserbase; print(browserbase.__version__)"

# Verify anysearch
python3 -c "import anysearch; print('OK')"

# Verify Chrome DevTools MCP
cat .mcp.json

# Verify graph-engineering
ls vendor/graph-engineering/

# Verify agent-harness
ls vendor/agent-harness/
```

---

*Generated by Codebuff MoA Swarm Planner*
*Last verified: August 29, 2026 — 16:50 UTC*
*Environment: Ubuntu (Real VPS)*
