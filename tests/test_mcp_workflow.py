"""
test_mcp_workflow.py — Full MCP Workflow Integration Test

Tests the complete MCP server workflow:
1. Server initialization
2. Tool listing and schemas
3. Resource listing
4. Tool execution (model_call, moa_workflow, browser, scaffold)
5. External AI connection simulation
6. Scaffolding operations
7. Full end-to-end workflow

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


async def test_mcp_server():
    """Run all MCP server tests."""
    print("=" * 70)
    print("  MCP SERVER FULL WORKFLOW TEST")
    print("=" * 70)
    print()
    
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    def log_result(name, passed, message=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        results["tests"].append({"name": name, "passed": passed, "message": message})
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if message:
            print(f"         {message}")
    
    try:
        # ─── Test 1: Import MCPServer ──────────────────────────────────────
        print("-" * 70)
        print("TEST 1: Import MCPServer")
        print("-" * 70)
        
        from orchestrator.mcp_server import MCPServer, MCPTool, MCPResource, get_mcp_server
        log_result("Import MCPServer", True)
        
        # ─── Test 2: Create Server Instance ────────────────────────────────
        print("-" * 70)
        print("TEST 2: Create MCPServer Instance")
        print("-" * 70)
        
        server = MCPServer()
        log_result("Create MCPServer instance", True)
        
        # ─── Test 3: List Tools ────────────────────────────────────────────
        print("-" * 70)
        print("TEST 3: List Registered Tools")
        print("-" * 70)
        
        tools = server.list_tools()
        log_result("List tools", len(tools) > 0, f"Found {len(tools)} tools")
        
        for tool in tools:
            print(f"     📦 {tool['name']}: {tool['description'][:60]}...")
        
        # ─── Test 4: List Resources ────────────────────────────────────────
        print("-" * 70)
        print("TEST 4: List Registered Resources")
        print("-" * 70)
        
        resources = server.list_resources()
        log_result("List resources", len(resources) > 0, f"Found {len(resources)} resources")
        
        for resource in resources:
            print(f"     📄 {resource['uri']}: {resource['description'][:60]}...")
        
        # ─── Test 5: MCP Initialize Protocol ───────────────────────────────
        print("-" * 70)
        print("TEST 5: MCP Initialize Protocol")
        print("-" * 70)
        
        init_response = await server.handle_request({
            "method": "initialize",
            "params": {},
            "id": 1
        })
        
        has_result = "result" in init_response
        has_server_info = has_result and "serverInfo" in init_response.get("result", {})
        log_result(
            "MCP Initialize request",
            has_server_info,
            f"Server: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}"
        )
        
        # ─── Test 6: MCP Tools List Protocol ───────────────────────────────
        print("-" * 70)
        print("TEST 6: MCP Tools List Protocol")
        print("-" * 70)
        
        tools_response = await server.handle_request({
            "method": "tools/list",
            "params": {},
            "id": 2
        })
        
        tools_list = tools_response.get("result", {}).get("tools", [])
        log_result(
            "MCP Tools/List request",
            len(tools_list) > 0,
            f"Found {len(tools_list)} tools via MCP protocol"
        )
        
        # ─── Test 7: MCP Resources List Protocol ───────────────────────────
        print("-" * 70)
        print("TEST 7: MCP Resources List Protocol")
        print("-" * 70)
        
        resources_response = await server.handle_request({
            "method": "resources/list",
            "params": {},
            "id": 3
        })
        
        resources_list = resources_response.get("result", {}).get("resources", [])
        log_result(
            "MCP Resources/List request",
            len(resources_list) > 0,
            f"Found {len(resources_list)} resources via MCP protocol"
        )
        
        # ─── Test 8: Execute Unknown Method (Error Handling) ───────────────
        print("-" * 70)
        print("TEST 8: Error Handling for Unknown Method")
        print("-" * 70)
        
        error_response = await server.handle_request({
            "method": "unknown/method",
            "params": {},
            "id": 4
        })
        
        has_error = "error" in error_response
        log_result(
            "Error handling for unknown method",
            has_error,
            f"Error code: {error_response.get('error', {}).get('code', 'none')}"
        )
        
        # ─── Test 9: Execute Tool - system_status ──────────────────────────
        print("-" * 70)
        print("TEST 9: Execute Tool - get_swarm_status")
        print("-" * 70)
        
        status_response = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "get_swarm_status",
                "arguments": {}
            },
            "id": 5
        })
        
        status_result = json.loads(
            status_response.get("result", {}).get("content", [{}])[0].get("text", "{}")
        )
        log_result(
            "Execute get_swarm_status tool",
            "status" in status_result,
            f"Status: {status_result.get('status', 'unknown')}"
        )
        
        # ─── Test 10: Execute Tool - scaffold_project ──────────────────────
        print("-" * 70)
        print("TEST 10: Execute Tool - scaffold_project")
        print("-" * 70)
        
        scaffold_response = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "scaffold_project",
                "arguments": {
                    "project_name": "test_project",
                    "project_type": "api"
                }
            },
            "id": 6
        })
        
        scaffold_result = json.loads(
            scaffold_response.get("result", {}).get("content", [{}])[0].get("text", "{}")
        )
        log_result(
            "Execute scaffold_project tool",
            "files_created" in scaffold_result,
            f"Created {len(scaffold_result.get('files_created', []))} files"
        )
        
        # List created files
        if "files_created" in scaffold_result:
            for f in scaffold_result["files_created"]:
                print(f"     📄 {f}")
        
        # ─── Test 11: Execute Tool - create_task ───────────────────────────
        print("-" * 70)
        print("TEST 11: Execute Tool - create_task")
        print("-" * 70)
        
        task_response = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "create_task",
                "arguments": {
                    "input": "Analyze code quality",
                    "role": "proposer"
                }
            },
            "id": 7
        })
        
        task_result = json.loads(
            task_response.get("result", {}).get("content", [{}])[0].get("text", "{}")
        )
        log_result(
            "Execute create_task tool",
            "task_id" in task_result,
            f"Task ID: {task_result.get('task_id', 'none')}"
        )
        
        # ─── Test 12: Full MCP Workflow Simulation ─────────────────────────
        print("-" * 70)
        print("TEST 12: Full External AI Connection Simulation")
        print("-" * 70)
        
        # Simulate external AI connecting and using the MCP server
        print("     🤖 Simulating external AI connection...")
        
        # Step 1: Initialize
        init = await server.handle_request({
            "method": "initialize",
            "params": {},
            "id": 100
        })
        print(f"     📡 Connected: {init['result']['serverInfo']['name']} v{init['result']['serverInfo']['version']}")
        
        # Step 2: List available tools
        tools_resp = await server.handle_request({
            "method": "tools/list",
            "params": {},
            "id": 101
        })
        tool_names = [t["name"] for t in tools_resp["result"]["tools"]]
        print(f"     🔧 Available tools: {', '.join(tool_names)}")
        
        # Step 3: Read resources
        resources_resp = await server.handle_request({
            "method": "resources/read",
            "params": {"uri": "moa://health"},
            "id": 102
        })
        health_content = resources_resp.get("result", {}).get("contents", [{}])[0].get("text", "{}")
        health_data = json.loads(health_content)
        print(f"     🏥 System health: {health_data.get('status', 'unknown')}")
        
        # Step 4: Scaffold a project
        scaffold_resp = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "scaffold_project",
                "arguments": {
                    "project_name": "external_ai_project",
                    "project_type": "api"
                }
            },
            "id": 103
        })
        scaffold_data = json.loads(
            scaffold_resp["result"]["content"][0]["text"]
        )
        print(f"     📁 Scaffolded project: {scaffold_data['project_name']}")
        print(f"     📄 Created files: {scaffold_data['files_created']}")
        
        # Step 5: Create and execute a task
        task_resp = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "create_task",
                "arguments": {
                    "input": "Review the scaffolded project for best practices",
                    "role": "proposer"
                }
            },
            "id": 104
        })
        task_data = json.loads(task_resp["result"]["content"][0]["text"])
        print(f"     📋 Created task: {task_data.get('task_id', 'none')}")
        
        # Step 6: Get swarm status
        status_resp = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "get_swarm_status",
                "arguments": {}
            },
            "id": 105
        })
        status_data = json.loads(status_resp["result"]["content"][0]["text"])
        print(f"     🌐 Swarm status: {status_data.get('status', 'unknown')}")
        
        log_result("Full external AI workflow simulation", True)
        
        # ─── Test 13: Verify MCP Schema Compliance ────────────────────────
        print("-" * 70)
        print("TEST 13: Verify MCP Schema Compliance")
        print("-" * 70)
        
        # Check that all tools have proper MCP schema
        schema_valid = True
        for tool in tools_list:
            if "name" not in tool or "description" not in tool or "inputSchema" not in tool:
                schema_valid = False
                print(f"     ❌ Tool {tool.get('name', 'unknown')} missing required fields")
        
        # Check that all resources have proper schema
        for resource in resources_list:
            if "uri" not in resource or "name" not in resource:
                schema_valid = False
                print(f"     ❌ Resource missing required fields")
        
        log_result("MCP schema compliance", schema_valid)
        
        # ─── Test 14: Tool Error Handling ──────────────────────────────────
        print("-" * 70)
        print("TEST 14: Tool Error Handling")
        print("-" * 70)
        
        # Try to call a non-existent tool
        tool_error = await server.handle_request({
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            },
            "id": 106
        })
        
        log_result(
            "Tool not found error handling",
            "error" in tool_error,
            f"Error: {tool_error.get('error', {}).get('message', 'none')}"
        )
        
        # ─── Test 15: Resource Error Handling ──────────────────────────────
        print("-" * 70)
        print("TEST 15: Resource Error Handling")
        print("-" * 70)
        
        resource_error = await server.handle_request({
            "method": "resources/read",
            "params": {"uri": "moa://nonexistent"},
            "id": 107
        })
        
        log_result(
            "Resource not found error handling",
            "error" in resource_error,
            f"Error: {resource_error.get('error', {}).get('message', 'none')}"
        )
        
        # ─── Cleanup ───────────────────────────────────────────────────────
        print("-" * 70)
        print("CLEANUP: Removing test scaffolding")
        print("-" * 70)
        
        import shutil
        for dir_name in ["test_project", "external_ai_project"]:
            dir_path = os.path.join(os.getcwd(), dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"     🗑️  Removed: {dir_name}/")
        
        # ─── Summary ───────────────────────────────────────────────────────
        print()
        print("=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        print(f"  Total:   {results['passed'] + results['failed']}")
        print(f"  Passed:  {results['passed']}")
        print(f"  Failed:  {results['failed']}")
        print(f"  Status:  {'✅ ALL TESTS PASSED' if results['failed'] == 0 else '❌ SOME TESTS FAILED'}")
        print("=" * 70)
        
        return results
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        results["failed"] += 1
        results["tests"].append({"name": "FATAL", "passed": False, "message": str(e)})
        return results


def main():
    """Main entry point."""
    results = asyncio.run(test_mcp_server())
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
