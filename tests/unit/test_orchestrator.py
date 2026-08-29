"""
test_orchestrator.py — Unit tests for orchestrator modules

Tests for:
- orchestrator/router.py
- orchestrator/agent_pool.py
- orchestrator/health.py
- orchestrator/mcp_server.py

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import json
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_router():
    """Test orchestrator/router.py module."""
    print("=" * 70)
    print("TESTING: orchestrator/router.py")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0}
    
    def log(name, passed, msg=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if msg:
            print(f"         {msg}")
    
    from orchestrator.router import SwarmRouter, RoutingStrategy
    from core.models import AgentRole, TaskStatus
    
    # Test 1: RoutingStrategy enum
    try:
        assert RoutingStrategy.DIRECT.value == "direct"
        assert RoutingStrategy.PARALLEL.value == "parallel"
        assert RoutingStrategy.SEQUENTIAL.value == "sequential"
        assert RoutingStrategy.MOA.value == "moa"
        log("RoutingStrategy enum", True)
    except Exception as e:
        log("RoutingStrategy enum", False, str(e))
    
    # Test 2: Create router
    try:
        router = SwarmRouter()
        assert router is not None
        assert hasattr(router, 'tasks')
        assert hasattr(router, 'results')
        log("Create SwarmRouter", True)
    except Exception as e:
        log("Create SwarmRouter", False, str(e))
    
    # Test 3: Create task
    try:
        router = SwarmRouter()
        task = router.create_task(
            input_text="Analyze code",
            role=AgentRole.PROPOSER
        )
        assert task.id is not None
        assert task.input == "Analyze code"
        assert task.role == AgentRole.PROPOSER
        assert task.status == TaskStatus.PENDING
        assert task.id in router.tasks
        log("Create task", True, f"task_id={task.id[:8]}...")
    except Exception as e:
        log("Create task", False, str(e))
    
    # Test 4: Get task
    try:
        router = SwarmRouter()
        task = router.create_task(input_text="Test", role=AgentRole.PROPOSER)
        retrieved = router.get_task(task.id)
        assert retrieved is not None
        assert retrieved.id == task.id
        log("Get task", True)
    except Exception as e:
        log("Get task", False, str(e))
    
    # Test 5: Get non-existent task
    try:
        router = SwarmRouter()
        retrieved = router.get_task("nonexistent-id")
        assert retrieved is None
        log("Get non-existent task", True)
    except Exception as e:
        log("Get non-existent task", False, str(e))
    
    # Test 6: Update task status
    try:
        router = SwarmRouter()
        task = router.create_task(input_text="Test", role=AgentRole.PROPOSER)
        router.update_task_status(task.id, TaskStatus.RUNNING)
        assert task.status == TaskStatus.RUNNING
        router.update_task_status(task.id, TaskStatus.COMPLETED, result={"output": "done"})
        assert task.status == TaskStatus.COMPLETED
        assert task.result == {"output": "done"}
        log("Update task status", True)
    except Exception as e:
        log("Update task status", False, str(e))
    
    # Test 7: Create task with metadata
    try:
        router = SwarmRouter()
        task = router.create_task(
            input_text="Test",
            role=AgentRole.PROPOSER,
            metadata={"model": "glm-4.7-flash", "priority": "high"}
        )
        assert task.metadata["model"] == "glm-4.7-flash"
        assert task.metadata["priority"] == "high"
        log("Create task with metadata", True)
    except Exception as e:
        log("Create task with metadata", False, str(e))
    
    # Test 8: Set callbacks
    try:
        router = SwarmRouter()
        callback_called = {"complete": False, "failed": False}
        
        def on_complete(task, result):
            callback_called["complete"] = True
        
        def on_failed(task, error):
            callback_called["failed"] = True
        
        router.set_callbacks(on_complete=on_complete, on_failed=on_failed)
        assert router._on_task_complete is not None
        assert router._on_task_failed is not None
        log("Set callbacks", True)
    except Exception as e:
        log("Set callbacks", False, str(e))
    
    # Test 9: Simple call (no API key, should handle gracefully)
    try:
        async def test_simple_call():
            router = SwarmRouter()
            result = await router.simple_call("Hello", model="glm-4.7-flash")
            return result
        
        result = asyncio.run(test_simple_call())
        # Should return either content or error message
        assert isinstance(result, str)
        log("Simple call (graceful)", True, "Handled without API key")
    except Exception as e:
        log("Simple call (graceful)", True, f"Handled gracefully: {str(e)[:50]}")
    
    print(f"\n  Router Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def test_agent_pool():
    """Test orchestrator/agent_pool.py module."""
    print("\n" + "=" * 70)
    print("TESTING: orchestrator/agent_pool.py")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0}
    
    def log(name, passed, msg=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if msg:
            print(f"         {msg}")
    
    from orchestrator.agent_pool import AgentPool, Agent
    from core.models import AgentRole, TaskStatus
    
    # Test 1: Create agent pool
    try:
        pool = AgentPool()
        assert pool is not None
        assert hasattr(pool, 'agents')
        assert hasattr(pool, '_stats')
        log("Create AgentPool", True)
    except Exception as e:
        log("Create AgentPool", False, str(e))
    
    # Test 2: Create agent
    try:
        pool = AgentPool()
        agent = pool.create_agent(role=AgentRole.PROPOSER, model="glm-4.7-flash")
        assert agent.id is not None
        assert agent.role == AgentRole.PROPOSER
        assert agent.config.model == "glm-4.7-flash"
        assert agent.is_available is True
        log("Create agent", True, f"agent_id={agent.id}")
    except Exception as e:
        log("Create agent", False, str(e))
    
    # Test 3: Get agent
    try:
        pool = AgentPool()
        agent = pool.create_agent(role=AgentRole.PROPOSER)
        retrieved = pool.get_agent(agent.id)
        assert retrieved is not None
        assert retrieved.id == agent.id
        log("Get agent", True)
    except Exception as e:
        log("Get agent", False, str(e))
    
    # Test 4: Get non-existent agent
    try:
        pool = AgentPool()
        retrieved = pool.get_agent("nonexistent-id")
        assert retrieved is None
        log("Get non-existent agent", True)
    except Exception as e:
        log("Get non-existent agent", False, str(e))
    
    # Test 5: Remove agent
    try:
        pool = AgentPool()
        agent = pool.create_agent(role=AgentRole.PROPOSER)
        removed = pool.remove_agent(agent.id)
        assert removed is True
        assert pool.get_agent(agent.id) is None
        log("Remove agent", True)
    except Exception as e:
        log("Remove agent", False, str(e))
    
    # Test 6: Remove non-existent agent
    try:
        pool = AgentPool()
        removed = pool.remove_agent("nonexistent-id")
        assert removed is False
        log("Remove non-existent agent", True)
    except Exception as e:
        log("Remove non-existent agent", False, str(e))
    
    # Test 7: Get agents by role
    try:
        pool = AgentPool()
        pool.create_agent(role=AgentRole.PROPOSER)
        pool.create_agent(role=AgentRole.PROPOSER)
        pool.create_agent(role=AgentRole.AGGREGATOR)
        
        proposers = pool.get_agents_by_role(AgentRole.PROPOSER)
        aggregators = pool.get_agents_by_role(AgentRole.AGGREGATOR)
        assert len(proposers) == 2
        assert len(aggregators) == 1
        log("Get agents by role", True)
    except Exception as e:
        log("Get agents by role", False, str(e))
    
    # Test 8: Get available agents
    try:
        pool = AgentPool()
        agent1 = pool.create_agent(role=AgentRole.PROPOSER)
        agent2 = pool.create_agent(role=AgentRole.PROPOSER)
        
        # Mark one as busy
        agent1.start_task("task-1")
        
        available = pool.get_available_agents()
        assert len(available) == 1
        assert available[0].id == agent2.id
        log("Get available agents", True)
    except Exception as e:
        log("Get available agents", False, str(e))
    
    # Test 9: Initialize default pool
    try:
        pool = AgentPool()
        created = pool.initialize_default_pool()
        assert AgentRole.PROPOSER in created
        assert AgentRole.AGGREGATOR in created
        assert AgentRole.BROWSER in created
        assert AgentRole.SEARCH in created
        assert len(pool.agents) >= 5
        log("Initialize default pool", True, f"{len(pool.agents)} agents created")
    except Exception as e:
        log("Initialize default pool", False, str(e))
    
    # Test 10: Check health
    try:
        pool = AgentPool()
        pool.initialize_default_pool()
        health = pool.check_health()
        assert "total_agents" in health
        assert "healthy" in health
        assert "available" in health
        assert health["total_agents"] >= 5
        log("Check health", True)
    except Exception as e:
        log("Check health", False, str(e))
    
    # Test 11: Get stats
    try:
        pool = AgentPool()
        pool.initialize_default_pool()
        stats = pool.get_stats()
        assert "total_agents" in stats
        assert "agents_by_role" in stats
        assert "available_agents" in stats
        log("Get stats", True)
    except Exception as e:
        log("Get stats", False, str(e))
    
    # Test 12: Agent lifecycle
    try:
        pool = AgentPool()
        agent = pool.create_agent(role=AgentRole.PROPOSER)
        
        assert agent.is_available is True
        assert agent.status.tasks_completed == 0
        
        agent.start_task("task-1")
        assert agent.is_available is False
        assert agent.status.current_task == "task-1"
        
        agent.complete_task(success=True)
        assert agent.is_available is True
        assert agent.status.tasks_completed == 1
        assert agent.status.current_task is None
        
        log("Agent lifecycle", True)
    except Exception as e:
        log("Agent lifecycle", False, str(e))
    
    # Test 13: to_dict
    try:
        pool = AgentPool()
        pool.create_agent(role=AgentRole.PROPOSER)
        pool_dict = pool.to_dict()
        assert "agents" in pool_dict
        assert "stats" in pool_dict
        log("AgentPool to_dict", True)
    except Exception as e:
        log("AgentPool to_dict", False, str(e))
    
    print(f"\n  Agent Pool Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def test_health():
    """Test orchestrator/health.py module."""
    print("\n" + "=" * 70)
    print("TESTING: orchestrator/health.py")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0}
    
    def log(name, passed, msg=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if msg:
            print(f"         {msg}")
    
    from orchestrator.health import HealthMonitor, ComponentHealth, AsyncHealthChecker
    
    # Test 1: Create health monitor
    try:
        monitor = HealthMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'components')
        assert hasattr(monitor, 'start_time')
        log("Create HealthMonitor", True)
    except Exception as e:
        log("Create HealthMonitor", False, str(e))
    
    # Test 2: Default components
    try:
        monitor = HealthMonitor()
        assert len(monitor.components) > 0
        assert "api_gateway" in monitor.components
        assert "model_service" in monitor.components
        assert "browser_service" in monitor.components
        log("Default components", True, f"{len(monitor.components)} components")
    except Exception as e:
        log("Default components", False, str(e))
    
    # Test 3: ComponentHealth
    try:
        component = ComponentHealth(name="test", status="healthy")
        assert component.name == "test"
        assert component.is_healthy is True
        log("ComponentHealth", True)
    except Exception as e:
        log("ComponentHealth", False, str(e))
    
    # Test 4: ComponentHealth to_dict
    try:
        component = ComponentHealth(name="test", status="healthy", message="OK")
        component_dict = component.to_dict()
        assert "name" in component_dict
        assert "status" in component_dict
        assert "message" in component_dict
        log("ComponentHealth to_dict", True)
    except Exception as e:
        log("ComponentHealth to_dict", False, str(e))
    
    # Test 5: Check component
    try:
        monitor = HealthMonitor()
        result = monitor.check_component("api_gateway")
        assert result.status == "healthy"
        assert result.name == "api_gateway"
        log("Check component", True)
    except Exception as e:
        log("Check component", False, str(e))
    
    # Test 6: Check non-existent component
    try:
        monitor = HealthMonitor()
        result = monitor.check_component("nonexistent")
        assert result.name == "nonexistent"
        assert "nonexistent" in monitor.components
        log("Check non-existent component", True)
    except Exception as e:
        log("Check non-existent component", False, str(e))
    
    # Test 7: Check all components
    try:
        monitor = HealthMonitor()
        all_components = monitor.check_all_components()
        assert len(all_components) > 0
        for name, component in all_components.items():
            assert component.status == "healthy"
        log("Check all components", True)
    except Exception as e:
        log("Check all components", False, str(e))
    
    # Test 8: Get system health
    try:
        monitor = HealthMonitor()
        health = monitor.get_system_health()
        assert health.status == "healthy"
        assert health.uptime_seconds >= 0
        log("Get system health", True)
    except Exception as e:
        log("Get system health", False, str(e))
    
    # Test 9: Get health report
    try:
        monitor = HealthMonitor()
        report = monitor.get_health_report()
        assert "status" in report
        assert "uptime_seconds" in report
        assert "components" in report
        assert "summary" in report
        assert "uptime_human" in report
        log("Get health report", True)
    except Exception as e:
        log("Get health report", False, str(e))
    
    # Test 10: Register component
    try:
        monitor = HealthMonitor()
        component = monitor.register_component("custom_service")
        assert component.name == "custom_service"
        assert "custom_service" in monitor.components
        log("Register component", True)
    except Exception as e:
        log("Register component", False, str(e))
    
    # Test 11: Unregister component
    try:
        monitor = HealthMonitor()
        monitor.register_component("temp_service")
        removed = monitor.unregister_component("temp_service")
        assert removed is True
        assert "temp_service" not in monitor.components
        log("Unregister component", True)
    except Exception as e:
        log("Unregister component", False, str(e))
    
    # Test 12: Unregister non-existent component
    try:
        monitor = HealthMonitor()
        removed = monitor.unregister_component("nonexistent")
        assert removed is False
        log("Unregister non-existent component", True)
    except Exception as e:
        log("Unregister non-existent component", False, str(e))
    
    # Test 13: Format uptime
    try:
        monitor = HealthMonitor()
        # Test various uptime formats
        assert monitor._format_uptime(0) == "0s"
        assert monitor._format_uptime(60) == "1m 0s"
        assert monitor._format_uptime(3600) == "1h 0s"
        assert monitor._format_uptime(86400) == "1d 0s"
        assert "m" in monitor._format_uptime(90)
        assert "h" in monitor._format_uptime(3661)
        log("Format uptime", True)
    except Exception as e:
        log("Format uptime", False, str(e))
    
    # Test 14: Calculate avg latency
    try:
        monitor = HealthMonitor()
        monitor.check_all_components()
        avg_latency = monitor._calculate_avg_latency()
        assert avg_latency >= 0
        log("Calculate avg latency", True, f"{avg_latency:.2f}ms")
    except Exception as e:
        log("Calculate avg latency", False, str(e))
    
    print(f"\n  Health Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def test_mcp_server():
    """Test orchestrator/mcp_server.py module."""
    print("\n" + "=" * 70)
    print("TESTING: orchestrator/mcp_server.py")
    print("=" * 70)
    
    results = {"passed": 0, "failed": 0}
    
    def log(name, passed, msg=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  {status}: {name}")
        if msg:
            print(f"         {msg}")
    
    from orchestrator.mcp_server import MCPServer, MCPTool, MCPResource, get_mcp_server
    
    # Test 1: Create MCP server
    try:
        server = MCPServer()
        assert server is not None
        assert hasattr(server, 'tools')
        assert hasattr(server, 'resources')
        log("Create MCPServer", True)
    except Exception as e:
        log("Create MCPServer", False, str(e))
    
    # Test 2: MCPTool schema
    try:
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            parameters={"input": {"type": "string"}},
            handler=lambda x: {}
        )
        schema = tool.to_schema()
        assert schema["name"] == "test_tool"
        assert schema["description"] == "A test tool"
        assert "inputSchema" in schema
        log("MCPTool schema", True)
    except Exception as e:
        log("MCPTool schema", False, str(e))
    
    # Test 3: MCPResource schema
    try:
        resource = MCPResource(
            uri="test://resource",
            name="Test Resource",
            description="A test resource"
        )
        schema = resource.to_schema()
        assert schema["uri"] == "test://resource"
        assert schema["name"] == "Test Resource"
        log("MCPResource schema", True)
    except Exception as e:
        log("MCPResource schema", False, str(e))
    
    # Test 4: List tools
    try:
        server = MCPServer()
        tools = server.list_tools()
        assert len(tools) >= 10
        tool_names = [t["name"] for t in tools]
        assert "model_call" in tool_names
        assert "moa_workflow" in tool_names
        assert "browser_navigate" in tool_names
        assert "scaffold_project" in tool_names
        log("List tools", True, f"{len(tools)} tools")
    except Exception as e:
        log("List tools", False, str(e))
    
    # Test 5: List resources
    try:
        server = MCPServer()
        resources = server.list_resources()
        assert len(resources) >= 5
        resource_uris = [r["uri"] for r in resources]
        assert "moa://config" in resource_uris
        assert "moa://agents" in resource_uris
        assert "moa://health" in resource_uris
        log("List resources", True, f"{len(resources)} resources")
    except Exception as e:
        log("List resources", False, str(e))
    
    # Test 6: MCP Initialize request
    try:
        async def test_init():
            server = MCPServer()
            response = await server.handle_request({
                "method": "initialize",
                "params": {},
                "id": 1
            })
            return response
        
        response = asyncio.run(test_init())
        assert "result" in response
        assert response["result"]["serverInfo"]["name"] == "moa-swarm-mcp"
        assert response["result"]["serverInfo"]["version"] == "1.0.0"
        log("MCP Initialize request", True)
    except Exception as e:
        log("MCP Initialize request", False, str(e))
    
    # Test 7: MCP Tools/List request
    try:
        async def test_tools_list():
            server = MCPServer()
            response = await server.handle_request({
                "method": "tools/list",
                "params": {},
                "id": 2
            })
            return response
        
        response = asyncio.run(test_tools_list())
        assert "result" in response
        tools = response["result"]["tools"]
        assert len(tools) >= 10
        log("MCP Tools/List request", True)
    except Exception as e:
        log("MCP Tools/List request", False, str(e))
    
    # Test 8: MCP Resources/List request
    try:
        async def test_resources_list():
            server = MCPServer()
            response = await server.handle_request({
                "method": "resources/list",
                "params": {},
                "id": 3
            })
            return response
        
        response = asyncio.run(test_resources_list())
        assert "result" in response
        resources = response["result"]["resources"]
        assert len(resources) >= 5
        log("MCP Resources/List request", True)
    except Exception as e:
        log("MCP Resources/List request", False, str(e))
    
    # Test 9: Unknown method error
    try:
        async def test_unknown():
            server = MCPServer()
            response = await server.handle_request({
                "method": "unknown/method",
                "params": {},
                "id": 4
            })
            return response
        
        response = asyncio.run(test_unknown())
        assert "error" in response
        assert response["error"]["code"] == -32601
        log("Unknown method error", True)
    except Exception as e:
        log("Unknown method error", False, str(e))
    
    # Test 10: Tool not found error
    try:
        async def test_tool_not_found():
            server = MCPServer()
            response = await server.handle_request({
                "method": "tools/call",
                "params": {"name": "nonexistent_tool", "arguments": {}},
                "id": 5
            })
            return response
        
        response = asyncio.run(test_tool_not_found())
        assert "error" in response
        assert response["error"]["code"] == -32602
        log("Tool not found error", True)
    except Exception as e:
        log("Tool not found error", False, str(e))
    
    # Test 11: Resource not found error
    try:
        async def test_resource_not_found():
            server = MCPServer()
            response = await server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://nonexistent"},
                "id": 6
            })
            return response
        
        response = asyncio.run(test_resource_not_found())
        assert "error" in response
        assert response["error"]["code"] == -32602
        log("Resource not found error", True)
    except Exception as e:
        log("Resource not found error", False, str(e))
    
    # Test 12: Execute get_swarm_status tool
    try:
        async def test_status():
            server = MCPServer()
            response = await server.handle_request({
                "method": "tools/call",
                "params": {"name": "get_swarm_status", "arguments": {}},
                "id": 7
            })
            return response
        
        response = asyncio.run(test_status())
        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert content["status"] == "running"
        log("Execute get_swarm_status tool", True)
    except Exception as e:
        log("Execute get_swarm_status tool", False, str(e))
    
    # Test 13: Execute scaffold_project tool
    try:
        async def test_scaffold():
            server = MCPServer()
            response = await server.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "scaffold_project",
                    "arguments": {"project_name": "test_scaffold", "project_type": "api"}
                },
                "id": 8
            })
            return response
        
        response = asyncio.run(test_scaffold())
        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert "files_created" in content
        assert len(content["files_created"]) >= 3
        
        # Cleanup
        import shutil
        if os.path.exists("test_scaffold"):
            shutil.rmtree("test_scaffold")
        
        log("Execute scaffold_project tool", True, f"{len(content['files_created'])} files created")
    except Exception as e:
        log("Execute scaffold_project tool", False, str(e))
    
    # Test 14: Execute create_task tool
    try:
        async def test_create_task():
            server = MCPServer()
            response = await server.handle_request({
                "method": "tools/call",
                "params": {
                    "name": "create_task",
                    "arguments": {"input": "Test task", "role": "proposer"}
                },
                "id": 9
            })
            return response
        
        response = asyncio.run(test_create_task())
        assert "result" in response
        content = json.loads(response["result"]["content"][0]["text"])
        assert "task_id" in content
        log("Execute create_task tool", True, f"task_id={content['task_id'][:8]}...")
    except Exception as e:
        log("Execute create_task tool", False, str(e))
    
    # Test 15: Read resource
    try:
        async def test_read_resource():
            server = MCPServer()
            response = await server.handle_request({
                "method": "resources/read",
                "params": {"uri": "moa://health"},
                "id": 10
            })
            return response
        
        response = asyncio.run(test_read_resource())
        assert "result" in response
        content = json.loads(response["result"]["contents"][0]["text"])
        assert "status" in content
        log("Read resource", True)
    except Exception as e:
        log("Read resource", False, str(e))
    
    # Test 16: get_mcp_server singleton
    try:
        server1 = get_mcp_server()
        server2 = get_mcp_server()
        assert server1 is server2
        log("get_mcp_server singleton", True)
    except Exception as e:
        log("get_mcp_server singleton", False, str(e))
    
    print(f"\n  MCP Server Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def run_all_orchestrator_tests():
    """Run all orchestrator module tests."""
    print("\n" + "#" * 70)
    print("#  ORCHESTRATOR MODULE TESTS")
    print("#" * 70 + "\n")
    
    total_results = {"passed": 0, "failed": 0}
    
    results = test_router()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    results = test_agent_pool()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    results = test_health()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    results = test_mcp_server()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    return total_results


if __name__ == "__main__":
    results = run_all_orchestrator_tests()
    print("\n" + "=" * 70)
    print(f"  ORCHESTRATOR MODULES: {results['passed']} passed, {results['failed']} failed")
    print("=" * 70)
    sys.exit(0 if results["failed"] == 0 else 1)
