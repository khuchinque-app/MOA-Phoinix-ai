"""
mcp_server.py — MCP Server for External AI Access

This module implements an MCP (Model Context Protocol) server that allows
external AI agents to:
1. Access the MoA swarm capabilities
2. Perform scaffolding operations
3. Interact with browser automation
4. Execute tasks through the swarm

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import json
import asyncio
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from core.config import get_config, MoASwarmConfig
from core.heart_bleed import (
    heart_bleed_call,
    heart_bleed_call_async,
    moa_batch_call,
    moa_aggregate,
    HeartBleedConfig,
)
from orchestrator.router import SwarmRouter
from orchestrator.agent_pool import AgentPool
from action.browser import BrowserAgent


# ─── MCP Tool Definitions ─────────────────────────────────────────────────────

@dataclass
class MCPTool:
    """Definition of an MCP tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters,
                "required": [k for k, v in self.parameters.items() if v.get("required", False)],
            }
        }


@dataclass
class MCPResource:
    """Definition of an MCP resource."""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
        }


# ─── MCP Server ───────────────────────────────────────────────────────────────

class MCPServer:
    """
    MCP Server for External AI Access and Scaffolding.
    
    This server exposes MoA swarm capabilities through the MCP protocol,
    allowing external AI agents to:
    - Call models through heart_bleed
    - Execute MoA workflows
    - Control browser automation
    - Access swarm resources
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the MCP Server.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.router = SwarmRouter(self.config)
        self.agent_pool = AgentPool(self.config)
        self.browser_agent = BrowserAgent(self.config)
        
        # Registered tools and resources
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        
        # Session management
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default tools and resources
        self._register_default_tools()
        self._register_default_resources()
    
    # ─── Tool Registration ────────────────────────────────────────────────────
    
    def register_tool(self, tool: MCPTool) -> None:
        """Register an MCP tool."""
        self.tools[tool.name] = tool
    
    def _register_default_tools(self) -> None:
        """Register default MCP tools."""
        
        # Tool 1: Model Call
        self.register_tool(MCPTool(
            name="model_call",
            description="Call an AI model through the MoA swarm",
            parameters={
                "messages": {
                    "type": "array",
                    "description": "List of messages with role and content",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["user", "assistant", "system"]},
                            "content": {"type": "string"}
                        }
                    }
                },
                "model": {
                    "type": "string",
                    "description": "Model identifier (e.g., glm-4.7-flash, claude-3-opus)",
                    "default": "glm-4.7-flash"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate",
                    "default": 400
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature (0.0 to 2.0)",
                    "default": 0.7
                }
            },
            handler=self._handle_model_call
        ))
        
        # Tool 2: MoA Workflow
        self.register_tool(MCPTool(
            name="moa_workflow",
            description="Execute a full MoA (Mixture of Agents) workflow with proposers and aggregator",
            parameters={
                "input": {
                    "type": "string",
                    "description": "Input text to analyze",
                    "required": True
                },
                "proposer_models": {
                    "type": "array",
                    "description": "List of proposer model identifiers",
                    "items": {"type": "string"},
                    "default": ["glm-4.7-flash"]
                },
                "aggregator_model": {
                    "type": "string",
                    "description": "Aggregator model identifier",
                    "default": "glm-4.7-flash"
                }
            },
            handler=self._handle_moa_workflow
        ))
        
        # Tool 3: Browser Navigate
        self.register_tool(MCPTool(
            name="browser_navigate",
            description="Navigate to a URL in the browser",
            parameters={
                "url": {
                    "type": "string",
                    "description": "URL to navigate to",
                    "required": True
                },
                "session_id": {
                    "type": "string",
                    "description": "Browser session ID (creates new if not provided)"
                }
            },
            handler=self._handle_browser_navigate
        ))
        
        # Tool 4: Browser Screenshot
        self.register_tool(MCPTool(
            name="browser_screenshot",
            description="Take a screenshot of the current browser page",
            parameters={
                "session_id": {
                    "type": "string",
                    "description": "Browser session ID",
                    "required": True
                },
                "full_page": {
                    "type": "boolean",
                    "description": "Capture full page (not just viewport)",
                    "default": False
                }
            },
            handler=self._handle_browser_screenshot
        ))
        
        # Tool 5: Browser Click
        self.register_tool(MCPTool(
            name="browser_click",
            description="Click an element on the page",
            parameters={
                "session_id": {
                    "type": "string",
                    "description": "Browser session ID",
                    "required": True
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector for the element",
                    "required": True
                }
            },
            handler=self._handle_browser_click
        ))
        
        # Tool 6: Browser Fill
        self.register_tool(MCPTool(
            name="browser_fill",
            description="Fill a form field",
            parameters={
                "session_id": {
                    "type": "string",
                    "description": "Browser session ID",
                    "required": True
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector for the input field",
                    "required": True
                },
                "value": {
                    "type": "string",
                    "description": "Value to fill",
                    "required": True
                }
            },
            handler=self._handle_browser_fill
        ))
        
        # Tool 7: Get Swarm Status
        self.register_tool(MCPTool(
            name="get_swarm_status",
            description="Get the current status of the MoA swarm",
            parameters={},
            handler=self._handle_get_swarm_status
        ))
        
        # Tool 8: Create Task
        self.register_tool(MCPTool(
            name="create_task",
            description="Create a new task in the swarm",
            parameters={
                "input": {
                    "type": "string",
                    "description": "Task input text",
                    "required": True
                },
                "role": {
                    "type": "string",
                    "description": "Agent role (proposer, aggregator, browser, etc.)",
                    "default": "proposer"
                }
            },
            handler=self._handle_create_task
        ))
        
        # Tool 9: Execute Task
        self.register_tool(MCPTool(
            name="execute_task",
            description="Execute a task in the swarm",
            parameters={
                "task_id": {
                    "type": "string",
                    "description": "Task ID to execute",
                    "required": True
                }
            },
            handler=self._handle_execute_task
        ))
        
        # Tool 10: Scaffold Project
        self.register_tool(MCPTool(
            name="scaffold_project",
            description="Scaffold a new project structure with files and configuration",
            parameters={
                "project_name": {
                    "type": "string",
                    "description": "Name of the project",
                    "required": True
                },
                "project_type": {
                    "type": "string",
                    "description": "Type of project (api, web, cli, library)",
                    "default": "api"
                },
                "files": {
                    "type": "array",
                    "description": "List of files to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    }
                }
            },
            handler=self._handle_scaffold_project
        ))
    
    # ─── Resource Registration ────────────────────────────────────────────────
    
    def register_resource(self, resource: MCPResource) -> None:
        """Register an MCP resource."""
        self.resources[resource.uri] = resource
    
    def _register_default_resources(self) -> None:
        """Register default MCP resources."""
        
        # Resource 1: Swarm Configuration
        self.register_resource(MCPResource(
            uri="moa://config",
            name="Swarm Configuration",
            description="Current MoA swarm configuration",
        ))
        
        # Resource 2: Agent Pool Status
        self.register_resource(MCPResource(
            uri="moa://agents",
            name="Agent Pool",
            description="Current agent pool status and statistics",
        ))
        
        # Resource 3: Health Status
        self.register_resource(MCPResource(
            uri="moa://health",
            name="Health Status",
            description="System health status",
        ))
        
        # Resource 4: Task History
        self.register_resource(MCPResource(
            uri="moa://tasks",
            name="Task History",
            description="History of executed tasks",
        ))
        
        # Resource 5: Available Models
        self.register_resource(MCPResource(
            uri="moa://models",
            name="Available Models",
            description="List of available AI models",
        ))
    
    # ─── Tool Handlers ────────────────────────────────────────────────────────
    
    async def _handle_model_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle model_call tool invocation."""
        messages = params.get("messages", [])
        model = params.get("model", "glm-4.7-flash")
        max_tokens = params.get("max_tokens", 400)
        temperature = params.get("temperature", 0.7)
        
        config = HeartBleedConfig(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        result = await heart_bleed_call_async(messages, config)
        return result
    
    async def _handle_moa_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle moa_workflow tool invocation."""
        input_text = params.get("input", "")
        proposer_models = params.get("proposer_models", ["glm-4.7-flash"])
        aggregator_model = params.get("aggregator_model", "glm-4.7-flash")
        
        proposer_configs = [
            HeartBleedConfig(model=m) for m in proposer_models
        ]
        aggregator_config = HeartBleedConfig(model=aggregator_model)
        
        result = await self.router.route_moa(
            input_message=input_text,
            proposer_configs=proposer_configs,
            aggregator_config=aggregator_config,
        )
        
        return result
    
    async def _handle_browser_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle browser_navigate tool invocation."""
        url = params.get("url", "")
        session_id = params.get("session_id")
        
        # Create session if not provided
        if not session_id:
            session = await self.browser_agent.create_session()
            session_id = session.session_id
        
        result = await self.browser_agent.navigate(session_id, url)
        result["session_id"] = session_id
        
        return result
    
    async def _handle_browser_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle browser_screenshot tool invocation."""
        session_id = params.get("session_id", "")
        full_page = params.get("full_page", False)
        
        result = await self.browser_agent.screenshot(session_id, full_page=full_page)
        return result
    
    async def _handle_browser_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle browser_click tool invocation."""
        session_id = params.get("session_id", "")
        selector = params.get("selector", "")
        
        result = await self.browser_agent.click(session_id, selector)
        return result
    
    async def _handle_browser_fill(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle browser_fill tool invocation."""
        session_id = params.get("session_id", "")
        selector = params.get("selector", "")
        value = params.get("value", "")
        
        result = await self.browser_agent.fill(session_id, selector, value)
        return result
    
    async def _handle_get_swarm_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_swarm_status tool invocation."""
        health = self.agent_pool.check_health()
        stats = self.agent_pool.get_stats()
        
        return {
            "status": "running",
            "health": health,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _handle_create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_task tool invocation."""
        input_text = params.get("input", "")
        role = params.get("role", "proposer")
        
        from core.models import AgentRole
        
        # Map role string to AgentRole enum
        role_map = {
            "proposer": AgentRole.PROPOSER,
            "aggregator": AgentRole.AGGREGATOR,
            "browser": AgentRole.BROWSER,
            "desktop": AgentRole.DESKTOP,
            "search": AgentRole.SEARCH,
            "vision": AgentRole.VISION,
        }
        
        agent_role = role_map.get(role, AgentRole.PROPOSER)
        
        task = self.router.create_task(
            input_text=input_text,
            role=agent_role,
        )
        
        return {
            "task_id": task.id,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
        }
    
    async def _handle_execute_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute_task tool invocation."""
        task_id = params.get("task_id", "")
        
        task = self.router.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        result = await self.router.execute_task(task)
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "result": result,
        }
    
    async def _handle_scaffold_project(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scaffold_project tool invocation."""
        import os
        
        project_name = params.get("project_name", "my_project")
        project_type = params.get("project_type", "api")
        files = params.get("files", [])
        
        # Create project directory
        project_dir = os.path.join(os.getcwd(), project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        created_files = []
        
        # Create files
        for file_info in files:
            file_path = file_info.get("path", "")
            file_content = file_info.get("content", "")
            
            if file_path:
                full_path = os.path.join(project_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w") as f:
                    f.write(file_content)
                
                created_files.append(file_path)
        
        # Create default files if none provided
        if not files:
            default_files = self._get_default_project_files(project_name, project_type)
            
            for file_path, file_content in default_files.items():
                full_path = os.path.join(project_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w") as f:
                    f.write(file_content)
                
                created_files.append(file_path)
        
        return {
            "project_name": project_name,
            "project_dir": project_dir,
            "files_created": created_files,
            "project_type": project_type,
        }
    
    def _get_default_project_files(self, project_name: str, project_type: str) -> Dict[str, str]:
        """Get default files for a project type."""
        
        if project_type == "api":
            return {
                "main.py": f'''"""
{project_name} - API Server
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{project_name}")


class HealthResponse(BaseModel):
    status: str


@app.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.get("/")
async def root():
    return {{"message": "Welcome to {project_name}"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                "requirements.txt": "fastapi\nuvicorn\npydantic\n",
                "README.md": f"""# {project_name}

A FastAPI-based API server.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
""",
            }
        
        elif project_type == "cli":
            return {
                "cli.py": f'''"""
{project_name} - CLI Tool
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="{project_name}")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Executing: {{args.command}}")
    
    print(f"Running {project_name}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''',
                "requirements.txt": "",
                "README.md": f"""# {project_name}

A command-line tool.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python cli.py <command>
```
""",
            }
        
        else:  # Default to library
            return {
                f"{project_name}.py": f'''"""
{project_name} - Library
"""


def hello():
    """Say hello."""
    return "Hello from {project_name}!"
''',
                "__init__.py": f'from .{project_name} import hello\n',
                "requirements.txt": "",
                "README.md": f"""# {project_name}

A Python library.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from {project_name} import hello
print(hello())
```
""",
            }
    
    # ─── MCP Protocol Methods ─────────────────────────────────────────────────
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP protocol request.
        
        Args:
            request: MCP request dictionary
        
        Returns:
            MCP response dictionary
        """
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Route to appropriate handler
        if method == "initialize":
            return await self._handle_initialize(params, request_id)
        elif method == "tools/list":
            return await self._handle_tools_list(params, request_id)
        elif method == "tools/call":
            return await self._handle_tools_call(params, request_id)
        elif method == "resources/list":
            return await self._handle_resources_list(params, request_id)
        elif method == "resources/read":
            return await self._handle_resources_read(params, request_id)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def _handle_initialize(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "moa-swarm-mcp",
                    "version": "1.0.0"
                }
            }
        }
    
    async def _handle_tools_list(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = [tool.to_schema() for tool in self.tools.values()]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_tools_call(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        try:
            tool = self.tools[tool_name]
            result = await tool.handler(arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
    
    async def _handle_resources_list(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle resources/list request."""
        resources = [resource.to_schema() for resource in self.resources.values()]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": resources
            }
        }
    
    async def _handle_resources_read(self, params: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle resources/read request."""
        uri = params.get("uri", "")
        
        if uri not in self.resources:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            }
        
        # Get resource content based on URI
        content = await self._get_resource_content(uri)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(content, indent=2)
                    }
                ]
            }
        }
    
    async def _get_resource_content(self, uri: str) -> Dict[str, Any]:
        """Get content for a resource URI."""
        
        if uri == "moa://config":
            return self.config.to_dict()
        
        elif uri == "moa://agents":
            return self.agent_pool.get_stats()
        
        elif uri == "moa://health":
            from orchestrator.health import HealthMonitor
            monitor = HealthMonitor(self.config)
            return monitor.get_health_report()
        
        elif uri == "moa://tasks":
            return {
                "tasks": [
                    {
                        "id": task.id,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat(),
                    }
                    for task in self.router.tasks.values()
                ]
            }
        
        elif uri == "moa://models":
            return {
                "models": [
                    {"id": "glm-4.7-flash", "provider": "glm", "description": "Fast GLM model"},
                    {"id": "claude-3-opus", "provider": "anthropic", "description": "Powerful Claude model"},
                    {"id": "gpt-4", "provider": "openai", "description": "Advanced GPT model"},
                ]
            }
        
        return {}
    
    # ─── Utility Methods ──────────────────────────────────────────────────────
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        return [tool.to_schema() for tool in self.tools.values()]
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all registered resources."""
        return [resource.to_schema() for resource in self.resources.values()]


# ─── Singleton Server ─────────────────────────────────────────────────────────

_server_instance: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """
    Get the singleton MCP server instance.
    
    Returns:
        MCPServer instance
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPServer()
    return _server_instance


def setup_mcp_server(config: Optional[MoASwarmConfig] = None) -> MCPServer:
    """
    Setup MCP server with the given configuration.
    
    Args:
        config: MoASwarmConfig instance
    
    Returns:
        MCPServer instance
    """
    global _server_instance
    _server_instance = MCPServer(config)
    return _server_instance


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize MCP server
        server = MCPServer()
        
        print("MCP Server initialized!")
        print()
        
        # List tools
        print("Available Tools:")
        for tool in server.list_tools():
            print(f"  - {tool['name']}: {tool['description'][:50]}...")
        
        print()
        
        # List resources
        print("Available Resources:")
        for resource in server.list_resources():
            print(f"  - {resource['uri']}: {resource['description'][:50]}...")
        
        print()
        
        # Test initialize request
        print("Testing initialize request...")
        init_response = await server.handle_request({
            "method": "initialize",
            "params": {},
            "id": 1
        })
        print(f"  Response: {init_response['result']['serverInfo']}")
        
        print()
        
        # Test tools/list request
        print("Testing tools/list request...")
        tools_response = await server.handle_request({
            "method": "tools/list",
            "params": {},
            "id": 2
        })
        print(f"  Found {len(tools_response['result']['tools'])} tools")
        
        print()
        
        # Test resources/list request
        print("Testing resources/list request...")
        resources_response = await server.handle_request({
            "method": "resources/list",
            "params": {},
            "id": 3
        })
        print(f"  Found {len(resources_response['result']['resources'])} resources")
        
        print()
        print("MCP Server test completed!")
    
    asyncio.run(main())
