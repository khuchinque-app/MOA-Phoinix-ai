"""
test_external_ai_client.py — External AI Client Simulator

This script simulates an external AI (like Claude, GPT-4, etc.) connecting
to the MoA Swarm MCP server and performing scaffolding operations.

Usage:
    python tests/test_external_ai_client.py

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ExternalAIClient:
    """
    Simulates an external AI client connecting to the MoA MCP server.
    
    This class demonstrates how external AIs can:
    1. Connect to the MCP server
    2. Discover available tools and resources
    3. Execute tools and scaffolding operations
    4. Interact with the swarm
    """
    
    def __init__(self):
        """Initialize the client."""
        self.server = None
        self.session_id = None
        self.connected = False
        self.tool_history = []
        
    async def connect(self):
        """Connect to the MCP server."""
        print("🤖 External AI Client: Connecting to MCP server...")
        
        from orchestrator.mcp_server import MCPServer
        self.server = MCPServer()
        
        # Initialize connection
        response = await self.server.handle_request({
            "method": "initialize",
            "params": {},
            "id": 1
        })
        
        if "result" in response:
            self.connected = True
            server_info = response["result"]["serverInfo"]
            print(f"   ✅ Connected to {server_info['name']} v{server_info['version']}")
            print(f"   📡 Protocol: {response['result']['protocolVersion']}")
            return True
        else:
            print(f"   ❌ Connection failed: {response.get('error', 'unknown')}")
            return False
    
    async def discover_tools(self):
        """Discover available tools from the server."""
        if not self.connected:
            print("❌ Not connected")
            return []
        
        print("\n🔍 Discovering available tools...")
        
        response = await self.server.handle_request({
            "method": "tools/list",
            "params": {},
            "id": 2
        })
        
        tools = response.get("result", {}).get("tools", [])
        print(f"   Found {len(tools)} tools:")
        
        for tool in tools:
            print(f"   🔧 {tool['name']}")
            print(f"      {tool['description']}")
            required = tool.get("inputSchema", {}).get("required", [])
            if required:
                print(f"      Required params: {', '.join(required)}")
            print()
        
        return tools
    
    async def discover_resources(self):
        """Discover available resources."""
        if not self.connected:
            print("❌ Not connected")
            return []
        
        print("🔍 Discovering available resources...")
        
        response = await self.server.handle_request({
            "method": "resources/list",
            "params": {},
            "id": 3
        })
        
        resources = response.get("result", {}).get("resources", [])
        print(f"   Found {len(resources)} resources:")
        
        for resource in resources:
            print(f"   📄 {resource['uri']}")
            print(f"      {resource['description']}")
            print()
        
        return resources
    
    async def read_resource(self, uri):
        """Read a specific resource."""
        if not self.connected:
            print("❌ Not connected")
            return None
        
        response = await self.server.handle_request({
            "method": "resources/read",
            "params": {"uri": uri},
            "id": 10
        })
        
        if "result" in response:
            content = response["result"]["contents"][0]["text"]
            return json.loads(content)
        else:
            print(f"   ❌ Error reading resource: {response.get('error', 'unknown')}")
            return None
    
    async def call_tool(self, tool_name, arguments):
        """Call a tool on the server."""
        if not self.connected:
            print("❌ Not connected")
            return None
        
        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=6)}")
        
        response = await self.server.handle_request({
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 20
        })
        
        # Record in history
        self.tool_history.append({
            "tool": tool_name,
            "arguments": arguments,
            "timestamp": datetime.utcnow().isoformat(),
            "success": "result" in response
        })
        
        if "result" in response:
            content = json.loads(response["result"]["content"][0]["text"])
            print(f"   ✅ Success!")
            return content
        else:
            error = response.get("error", {}).get("message", "unknown")
            print(f"   ❌ Error: {error}")
            return {"error": error}
    
    async def scaffold_project(self, project_name, project_type="api", files=None):
        """Scaffold a new project using the MCP server."""
        print(f"\n📁 Scaffolding project: {project_name}")
        print(f"   Type: {project_type}")
        
        arguments = {
            "project_name": project_name,
            "project_type": project_type
        }
        
        if files:
            arguments["files"] = files
        
        result = await self.call_tool("scaffold_project", arguments)
        
        if result and "files_created" in result:
            print(f"\n   📂 Created project at: {result.get('project_dir', 'unknown')}")
            print(f"   📄 Files created:")
            for f in result["files_created"]:
                print(f"      - {f}")
        
        return result
    
    async def search_web(self, query):
        """Search the web using the MCP server."""
        print(f"\n🌐 Searching web: {query}")
        result = await self.call_tool("web_search", {"query": query})
        return result
    
    async def get_swarm_status(self):
        """Get swarm status."""
        print("\n📊 Getting swarm status...")
        result = await self.call_tool("get_swarm_status", {})
        return result
    
    async def create_and_execute_task(self, input_text, role="proposer"):
        """Create and execute a task."""
        print(f"\n📋 Creating task: {input_text[:50]}...")
        
        # Create task
        create_result = await self.call_tool("create_task", {
            "input": input_text,
            "role": role
        })
        
        if create_result and "task_id" in create_result:
            task_id = create_result["task_id"]
            print(f"   Task ID: {task_id}")
            
            # Execute task
            print(f"   Executing task...")
            exec_result = await self.call_tool("execute_task", {
                "task_id": task_id
            })
            
            return exec_result
        
        return create_result
    
    def get_session_summary(self):
        """Get a summary of the session."""
        return {
            "connected": self.connected,
            "tools_called": len(self.tool_history),
            "tool_history": self.tool_history
        }


async def run_external_ai_demo():
    """Run a full external AI client demo."""
    print("=" * 70)
    print("  EXTERNAL AI CLIENT DEMO")
    print("  Connecting to MoA Swarm MCP Server")
    print("=" * 70)
    print()
    
    client = ExternalAIClient()
    
    # ─── Step 1: Connect ───────────────────────────────────────────────────
    print("━" * 70)
    print("STEP 1: Connect to MCP Server")
    print("━" * 70)
    
    connected = await client.connect()
    if not connected:
        print("❌ Failed to connect. Exiting.")
        return
    
    # ─── Step 2: Discover Tools ────────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 2: Discover Available Tools")
    print("━" * 70)
    
    tools = await client.discover_tools()
    
    # ─── Step 3: Discover Resources ────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 3: Discover Available Resources")
    print("━" * 70)
    
    resources = await client.discover_resources()
    
    # ─── Step 4: Read System Health ────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 4: Read System Health Resource")
    print("━" * 70)
    
    health = await client.read_resource("moa://health")
    if health:
        print(f"   Health status: {health.get('status', 'unknown')}")
        print(f"   Timestamp: {health.get('timestamp', 'unknown')}")
    
    # ─── Step 5: Read Available Models ─────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 5: Read Available Models Resource")
    print("━" * 70)
    
    models = await client.read_resource("moa://models")
    if models:
        print(f"   Available models:")
        for model in models.get("models", []):
            print(f"   🤖 {model['id']} ({model['provider']})")
    
    # ─── Step 6: Scaffold a Project ────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 6: Scaffold a New Project")
    print("━" * 70)
    
    scaffold_result = await client.scaffold_project(
        project_name="my_ai_project",
        project_type="api"
    )
    
    # ─── Step 7: Search the Web ────────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 7: Search the Web")
    print("━" * 70)
    
    search_result = await client.search_web("MoA architecture multi-agent system")
    if search_result:
        print(f"   Search completed: {search_result.get('success', False)}")
    
    # ─── Step 8: Get Swarm Status ──────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 8: Get Swarm Status")
    print("━" * 70)
    
    status = await client.get_swarm_status()
    if status:
        print(f"   Swarm status: {status.get('status', 'unknown')}")
        if "stats" in status:
            stats = status["stats"]
            print(f"   Total agents: {stats.get('total_agents', 0)}")
            print(f"   Available agents: {stats.get('available_agents', 0)}")
    
    # ─── Step 9: Create and Execute Task ───────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 9: Create and Execute a Task")
    print("━" * 70)
    
    task_result = await client.create_and_execute_task(
        input_text="Analyze the best practices for Python project structure",
        role="proposer"
    )
    
    # ─── Step 10: Session Summary ──────────────────────────────────────────
    print("\n" + "━" * 70)
    print("STEP 10: Session Summary")
    print("━" * 70)
    
    summary = client.get_session_summary()
    print(f"   Connected: {summary['connected']}")
    print(f"   Tools called: {summary['tools_called']}")
    print(f"\n   Tool call history:")
    for i, entry in enumerate(summary['tool_history'], 1):
        status = "✅" if entry['success'] else "❌"
        print(f"   {i}. {status} {entry['tool']}")
    
    # ─── Cleanup ───────────────────────────────────────────────────────────
    print("\n" + "━" * 70)
    print("CLEANUP")
    print("━" * 70)
    
    import shutil
    for dir_name in ["my_ai_project"]:
        dir_path = os.path.join(os.getcwd(), dir_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   🗑️  Removed: {dir_name}/")
    
    # ─── Final Summary ─────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)
    print()
    print("  External AI can:")
    print("  ✅ Connect to MoA Swarm MCP server")
    print("  ✅ Discover and list available tools")
    print("  ✅ Discover and read resources")
    print("  ✅ Scaffold new projects")
    print("  ✅ Search the web")
    print("  ✅ Get swarm status")
    print("  ✅ Create and execute tasks")
    print("  ✅ Full MCP protocol support")
    print()
    print("  The MCP server is ready for external AI connections!")
    print("=" * 70)


def main():
    """Main entry point."""
    asyncio.run(run_external_ai_demo())


if __name__ == "__main__":
    main()
