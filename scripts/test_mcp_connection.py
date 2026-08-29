#!/usr/bin/env python3
"""
test_mcp_connection.py — MCP Server Connection Test for External AI

Tests the MCP server connection and verifies all tools and resources
are accessible for external AI scaffolding.

Usage:
    python scripts/test_mcp_connection.py
    python scripts/test_mcp_connection.py --verbose
    python scripts/test_mcp_connection.py --test-tools
    python scripts/test_mcp_connection.py --test-scaffold

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import json
import asyncio
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MCPConnectionTester:
    """Comprehensive MCP server connection tester."""
    
    def __init__(self, verbose=False):
        """Initialize the tester."""
        self.verbose = verbose
        self.server = None
        self.results = {"passed": 0, "failed": 0, "tests": []}
    
    def log(self, name, passed, msg="", verbose_only=False):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        self.results["tests"].append({"name": name, "passed": passed, "message": msg})
        
        if not verbose_only or self.verbose:
            print(f"  {status}: {name}")
            if msg:
                print(f"         {msg}")
    
    def print_section(self, title):
        """Print a section header."""
        print()
        print("-" * 70)
        print(f"  {title}")
        print("-" * 70)
    
    async def run_all_tests(self):
        """Run all MCP connection tests."""
        print("=" * 70)
        print("  MCP SERVER CONNECTION TEST")
        print("  Testing External AI Connection & Scaffolding")
        print("=" * 70)
        
        # Test 1: Import MCPServer
        self.print_section("1. Import MCPServer")
        try:
            from orchestrator.mcp_server import MCPServer, MCPTool, MCPResource
            self.log("Import MCPServer", True)
        except Exception as e:
            self.log("Import MCPServer", False, str(e))
            return self.results
        
        # Test 2: Create MCPServer
        self.print_section("2. Create MCPServer Instance")
        try:
            self.server = MCPServer()
            self.log("Create MCPServer", True)
        except Exception as e:
            self.log("Create MCPServer", False, str(e))
            return self.results
        
        # Test 3: List Tools
        self.print_section("3. List Available Tools")
        try:
            tools = self.server.list_tools()
            tool_names = [t["name"] for t in tools]
            self.log("List tools", len(tools) >= 10, f"{len(tools)} tools found")
            
            # Print all tools
            for tool in tools:
                print(f"     🔧 {tool['name']}: {tool['description'][:60]}...")
                if self.verbose:
                    required = tool.get("inputSchema", {}).get("required", [])
                    if required:
                        print(f"        Required: {', '.join(required)}")
        except Exception as e:
            self.log("List tools", False, str(e))
        
        # Test 4: List Resources
        self.print_section("4. List Available Resources")
        try:
            resources = self.server.list_resources()
            resource_uris = [r["uri"] for r in resources]
            self.log("List resources", len(resources) >= 5, f"{len(resources)} resources found")
            
            # Print all resources
            for resource in resources:
                print(f"     📄 {resource['uri']}: {resource['description'][:60]}...")
        except Exception as e:
            self.log("List resources", False, str(e))
        
        # Test 5: MCP Initialize Protocol
        self.print_section("5. MCP Protocol - Initialize")
        try:
            response = await self.server.handle_request({
                "method": "initialize",
                "params": {},
                "id": 1
            })
            has_result = "result" in response
            has_server_info = has_result and "serverInfo" in response.get("result", {})
            server_name = response.get("result", {}).get("serverInfo", {}).get("name", "unknown")
            server_version = response.get("result", {}).get("serverInfo", {}).get("version", "unknown")
            
            self.log("MCP Initialize", has_server_info, f"Server: {server_name} v{server_version}")
        except Exception as e:
            self.log("MCP Initialize", False, str(e))
        
        # Test 6: MCP Tools/List Protocol
        self.print_section("6. MCP Protocol - Tools/List")
        try:
            response = await self.server.handle_request({
                "method": "tools/list",
                "params": {},
                "id": 2
            })
            tools_list = response.get("result", {}).get("tools", [])
            self.log("MCP Tools/List", len(tools_list) >= 10, f"{len(tools_list)} tools via protocol")
        except Exception as e:
            self.log("MCP Tools/List", False, str(e))
        
        # Test 7: MCP Resources/List Protocol
        self.print_section("7. MCP Protocol - Resources/List")
        try:
            response = await self.server.handle_request({
                "method": "resources/list",
                "params": {},
                "id": 3
            })
            resources_list = response.get("result", {}).get("resources", [])
            self.log("MCP Resources/List", len(resources_list) >= 5, f"{len(resources_list)} resources via protocol")
        except Exception as e:
            self.log("MCP Resources/List", False, str(e))
        
        # Test 8: Error Handling - Unknown Method
        self.print_section("8. MCP Protocol - Error Handling")
        try:
            response = await self.server.handle_request({
                "method": "unknown/method",
                "params": {},
                "id": 4
            })
            has_error = "error" in response
            error_code = response.get("error", {}).get("code", "none")
            self.log("Unknown method error", has_error, f"Error code: {error_code}")
        except Exception as e:
            self.log("Unknown method error", False, str(e))
        
        # Test 9: Error Handling - Tool Not Found
        try:
            response = await self.server.handle_request({
                "method": "tools/call",
                "params": {"name": "nonexistent_tool", "arguments": {}},
                "id": 5
            })
            has_error = "error" in response
            error_code = response.get("error", {}).get("code", "none")
            self.log("Tool not found error", has_error, f"Error code: {error_code}")
        except Exception as e:
            self.log("Tool not found error", False, str(e))
        
        # Test 10: Error Handling - Resource Not Found
        try:
            response = await self.server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://nonexistent"},
                "id": 6
            })
            has_error = "error" in response
            error_code = response.get("error", {}).get("code", "none")
            self.log("Resource not found error", has_error, f"Error code: {error_code}")
        except Exception as e:
            self.log("Resource not found error", False, str(e))
        
        # Test 11: Tool Execution - get_swarm_status
        self.print_section("9. Tool Execution")
        try:
            response = await self.server.handle_request({
                "method": "tools/call",
                "params": {"name": "get_swarm_status", "arguments": {}},
                "id": 7
            })
            content = json.loads(response.get("result", {}).get("content", [{}])[0].get("text", "{}"))
            self.log("get_swarm_status tool", "status" in content, f"Status: {content.get('status', 'unknown')}")
            
            if self.verbose and "health" in content:
                health = content["health"]
                print(f"        Total agents: {health.get('total_agents', 0)}")
                print(f"        Healthy: {health.get('healthy', 0)}")
                print(f"        Available: {health.get('available', 0)}")
        except Exception as e:
            self.log("get_swarm_status tool", False, str(e))
        
        # Test 12: Tool Execution - create_task
        try:
            response = await self.server.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "create_task",
                    "arguments": {"input": "Test task", "role": "proposer"}
                },
                "id": 8
            })
            content = json.loads(response.get("result", {}).get("content", [{}])[0].get("text", "{}"))
            self.log("create_task tool", "task_id" in content, f"Task ID: {content.get('task_id', 'none')[:8]}...")
        except Exception as e:
            self.log("create_task tool", False, str(e))
        
        # Test 13: Tool Execution - scaffold_project
        try:
            response = await self.server.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "scaffold_project",
                    "arguments": {"project_name": "test_connection", "project_type": "api"}
                },
                "id": 9
            })
            content = json.loads(response.get("result", {}).get("content", [{}])[0].get("text", "{}"))
            files_created = content.get("files_created", [])
            self.log("scaffold_project tool", len(files_created) >= 3, f"{len(files_created)} files created")
            
            # Print created files
            for f in files_created:
                print(f"        📄 {f}")
            
            # Cleanup
            import shutil
            if os.path.exists("test_connection"):
                shutil.rmtree("test_connection")
        except Exception as e:
            self.log("scaffold_project tool", False, str(e))
        
        # Test 14: Resource Reading
        self.print_section("10. Resource Reading")
        try:
            response = await self.server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://health"},
                "id": 10
            })
            content = json.loads(response.get("result", {}).get("contents", [{}])[0].get("text", "{}"))
            self.log("Read moa://health", "status" in content, f"Status: {content.get('status', 'unknown')}")
        except Exception as e:
            self.log("Read moa://health", False, str(e))
        
        try:
            response = await self.server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://models"},
                "id": 11
            })
            content = json.loads(response.get("result", {}).get("contents", [{}])[0].get("text", "{}"))
            models = content.get("models", [])
            self.log("Read moa://models", len(models) >= 3, f"{len(models)} models available")
            
            if self.verbose:
                for model in models:
                    print(f"        🤖 {model['id']} ({model['provider']})")
        except Exception as e:
            self.log("Read moa://models", False, str(e))
        
        # Test 15: External AI Workflow Simulation
        self.print_section("11. External AI Workflow Simulation")
        try:
            # Step 1: Initialize
            init = await self.server.handle_request({
                "method": "initialize",
                "params": {},
                "id": 100
            })
            print(f"     📡 Connected: {init['result']['serverInfo']['name']} v{init['result']['serverInfo']['version']}")
            
            # Step 2: List tools
            tools_resp = await self.server.handle_request({
                "method": "tools/list",
                "params": {},
                "id": 101
            })
            tool_names = [t["name"] for t in tools_resp["result"]["tools"]]
            print(f"     🔧 Available tools: {len(tool_names)}")
            
            # Step 3: Read health
            health_resp = await self.server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://health"},
                "id": 102
            })
            health_data = json.loads(health_resp["result"]["contents"][0]["text"])
            print(f"     🏥 Health: {health_data.get('status', 'unknown')}")
            
            # Step 4: Read models
            models_resp = await self.server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://models"},
                "id": 103
            })
            models_data = json.loads(models_resp["result"]["contents"][0]["text"])
            print(f"     🤖 Models: {len(models_data.get('models', []))}")
            
            # Step 5: Scaffold project
            scaffold_resp = await self.server.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "scaffold_project",
                    "arguments": {"project_name": "ai_project", "project_type": "api"}
                },
                "id": 104
            })
            scaffold_data = json.loads(scaffold_resp["result"]["content"][0]["text"])
            print(f"     📁 Scaffolded: {scaffold_data['project_name']}")
            print(f"     📄 Files: {scaffold_data['files_created']}")
            
            # Step 6: Create task
            task_resp = await self.server.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "create_task",
                    "arguments": {"input": "Review the scaffolded project", "role": "proposer"}
                },
                "id": 105
            })
            task_data = json.loads(task_resp["result"]["content"][0]["text"])
            print(f"     📋 Task: {task_data.get('task_id', 'none')[:8]}...")
            
            # Cleanup
            import shutil
            if os.path.exists("ai_project"):
                shutil.rmtree("ai_project")
            
            self.log("Full external AI workflow", True)
        except Exception as e:
            self.log("Full external AI workflow", False, str(e))
        
        # Summary
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("  MCP CONNECTION TEST SUMMARY")
        print("=" * 70)
        
        for test in self.results["tests"]:
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['name']}")
        
        print()
        print("-" * 70)
        print(f"  Total:   {self.results['passed'] + self.results['failed']}")
        print(f"  Passed:  {self.results['passed']}")
        print(f"  Failed:  {self.results['failed']}")
        print(f"  Status:  {'✅ ALL TESTS PASSED' if self.results['failed'] == 0 else '❌ SOME TESTS FAILED'}")
        print("-" * 70)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Server Connection Test for External AI"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--test-tools",
        action="store_true",
        help="Test all tools in detail"
    )
    parser.add_argument(
        "--test-scaffold",
        action="store_true",
        help="Test scaffolding functionality"
    )
    
    args = parser.parse_args()
    
    tester = MCPConnectionTester(verbose=args.verbose)
    results = await tester.run_all_tests()
    
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
