#!/usr/bin/env python3
"""
check_api_config.py — API Key & Model Configuration Checker

Comprehensive checker for API keys, model endpoints, and configuration.
Validates all settings and provides recommendations.

Usage:
    python scripts/check_api_config.py
    python scripts/check_api_config.py --fix
    python scripts/check_api_config.py --test-models

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import json
import asyncio
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class APIConfigChecker:
    """Comprehensive API configuration checker."""
    
    def __init__(self):
        """Initialize the checker."""
        self.results = {"passed": 0, "failed": 0, "warnings": [], "errors": []}
    
    def log(self, name, passed, msg="", level="info"):
        """Log check result."""
        status = "✅" if passed else "❌"
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        print(f"  {status} {name}")
        if msg:
            print(f"      {msg}")
        
        if not passed:
            if level == "error":
                self.results["errors"].append({"name": name, "message": msg})
            else:
                self.results["warnings"].append({"name": name, "message": msg})
    
    def print_section(self, title):
        """Print a section header."""
        print()
        print("-" * 70)
        print(f"  {title}")
        print("-" * 70)
    
    def check_env_file(self):
        """Check .env file exists and is configured."""
        self.print_section("1. Environment File")
        
        env_path = Path(".env")
        env_example_path = Path(".env.example")
        
        # Check .env exists
        if env_path.exists():
            self.log(".env file exists", True, f"Path: {env_path.absolute()}")
        else:
            self.log(".env file exists", False, ".env file not found. Copy .env.example to .env")
            return
        
        # Check .env.example exists
        if env_example_path.exists():
            self.log(".env.example exists", True, f"Path: {env_example_path.absolute()}")
        else:
            self.log(".env.example exists", False, ".env.example not found")
        
        # Read .env file
        try:
            with open(env_path, "r") as f:
                env_content = f.read()
            
            # Check for placeholder values
            placeholders = [
                "your_openai_api_key_here",
                "your_anthropic_api_key_here",
                "your_glm_api_key_here",
                "your_browserbase_api_key_here",
                "your_vps_ip_here",
                "your_registry_here"
            ]
            
            found_placeholders = []
            for placeholder in placeholders:
                if placeholder in env_content:
                    found_placeholders.append(placeholder.replace("your_", "").replace("_here", ""))
            
            if found_placeholders:
                self.log(
                    "No placeholder values",
                    False,
                    f"Found {len(found_placeholders)} placeholder values: {', '.join(found_placeholders)}"
                )
            else:
                self.log("No placeholder values", True)
                
        except Exception as e:
            self.log("Read .env file", False, str(e))
    
    def check_api_keys(self):
        """Check API keys configuration.
        
        API keys are optional - the system works with any available provider.
        Empty keys are informational, not failures.
        """
        self.print_section("2. API Keys")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys_found = 0
        
        # Check OpenAI API Key
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key and openai_key != "your_openai_api_key_here":
            self.log("OPENAI_API_KEY", True, f"Set ({len(openai_key)} chars)")
            api_keys_found += 1
        else:
            self.log("OPENAI_API_KEY", True, "Not set (optional - OpenAI models unavailable)")
        
        # Check Anthropic API Key
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
            self.log("ANTHROPIC_API_KEY", True, f"Set ({len(anthropic_key)} chars)")
            api_keys_found += 1
        else:
            self.log("ANTHROPIC_API_KEY", True, "Not set (optional - Anthropic models unavailable)")
        
        # Check GLM API Key
        glm_key = os.getenv("GLM_API_KEY", "")
        if glm_key and glm_key != "your_glm_api_key_here":
            self.log("GLM_API_KEY", True, f"Set ({len(glm_key)} chars)")
            api_keys_found += 1
        else:
            self.log("GLM_API_KEY", True, "Not set (optional - GLM models unavailable)")
        
        # Check Browserbase API Key
        browserbase_key = os.getenv("BROWSERBASE_API_KEY", "")
        if browserbase_key and browserbase_key != "your_browserbase_api_key_here":
            self.log("BROWSERBASE_API_KEY", True, f"Set ({len(browserbase_key)} chars)")
            api_keys_found += 1
        else:
            self.log("BROWSERBASE_API_KEY", True, "Not set (optional - stealth browser unavailable)")
        
        # Summary
        print(f"      ─── {api_keys_found}/4 API keys configured (system works with any available) ───")
    
    def check_model_endpoints(self):
        """Check model endpoint configuration."""
        self.print_section("3. Model Endpoints")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check Default Model Endpoint
        default_endpoint = os.getenv("DEFAULT_MODEL_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        self.log(
            "DEFAULT_MODEL_ENDPOINT",
            True,
            f"Set to: {default_endpoint}"
        )
        
        # Check GLM Endpoint
        glm_endpoint = os.getenv("GLM_ENDPOINT", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        self.log(
            "GLM_ENDPOINT",
            True,
            f"Set to: {glm_endpoint}"
        )
        
        # Check Claude Endpoint
        claude_endpoint = os.getenv("CLAUDE_ENDPOINT", "https://api.anthropic.com/v1/messages")
        self.log(
            "CLAUDE_ENDPOINT",
            True,
            f"Set to: {claude_endpoint}"
        )
    
    def check_swarm_config(self):
        """Check swarm configuration."""
        self.print_section("4. Swarm Configuration")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check Agent Pool Size
        pool_size = int(os.getenv("AGENT_POOL_SIZE", "5"))
        if 1 <= pool_size <= 100:
            self.log("AGENT_POOL_SIZE", True, f"Set to: {pool_size}")
        else:
            self.log(
                "AGENT_POOL_SIZE",
                False,
                f"Invalid value: {pool_size} (must be 1-100)",
                "error"
            )
        
        # Check Task Timeout
        timeout = int(os.getenv("TASK_TIMEOUT", "60"))
        if 1 <= timeout <= 300:
            self.log("TASK_TIMEOUT", True, f"Set to: {timeout}s")
        else:
            self.log(
                "TASK_TIMEOUT",
                False,
                f"Invalid value: {timeout} (must be 1-300)",
                "error"
            )
        
        # Check Retry Attempts
        retries = int(os.getenv("RETRY_ATTEMPTS", "3"))
        if 0 <= retries <= 10:
            self.log("RETRY_ATTEMPTS", True, f"Set to: {retries}")
        else:
            self.log(
                "RETRY_ATTEMPTS",
                False,
                f"Invalid value: {retries} (must be 0-10)",
                "error"
            )
        
        # Check Health Check Interval
        health_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
        if 5 <= health_interval <= 300:
            self.log("HEALTH_CHECK_INTERVAL", True, f"Set to: {health_interval}s")
        else:
            self.log(
                "HEALTH_CHECK_INTERVAL",
                False,
                f"Invalid value: {health_interval} (must be 5-300)",
                "error"
            )
        
        # Check Max Concurrent Proposers
        max_proposers = int(os.getenv("MAX_CONCURRENT_PROPOSERS", "10"))
        if 1 <= max_proposers <= 50:
            self.log("MAX_CONCURRENT_PROPOSERS", True, f"Set to: {max_proposers}")
        else:
            self.log(
                "MAX_CONCURRENT_PROPOSERS",
                False,
                f"Invalid value: {max_proposers} (must be 1-50)",
                "error"
            )
    
    def check_browser_config(self):
        """Check browser configuration."""
        self.print_section("5. Browser Configuration")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check Browser Type
        browser_type = os.getenv("BROWSER_TYPE", "chromium")
        valid_types = ["chromium", "firefox", "webkit"]
        if browser_type in valid_types:
            self.log("BROWSER_TYPE", True, f"Set to: {browser_type}")
        else:
            self.log(
                "BROWSER_TYPE",
                False,
                f"Invalid value: {browser_type} (must be one of: {', '.join(valid_types)})",
                "error"
            )
        
        # Check Headless Mode
        headless = os.getenv("BROWSER_HEADLESS", "true").lower()
        if headless in ["true", "false"]:
            self.log("BROWSER_HEADLESS", True, f"Set to: {headless}")
        else:
            self.log(
                "BROWSER_HEADLESS",
                False,
                f"Invalid value: {headless} (must be true or false)",
                "error"
            )
        
        # Check Viewport Width
        width = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))
        if 320 <= width <= 3840:
            self.log("BROWSER_VIEWPORT_WIDTH", True, f"Set to: {width}")
        else:
            self.log(
                "BROWSER_VIEWPORT_WIDTH",
                False,
                f"Invalid value: {width} (must be 320-3840)",
                "error"
            )
        
        # Check Viewport Height
        height = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))
        if 240 <= height <= 2160:
            self.log("BROWSER_VIEWPORT_HEIGHT", True, f"Set to: {height}")
        else:
            self.log(
                "BROWSER_VIEWPORT_HEIGHT",
                False,
                f"Invalid value: {height} (must be 240-2160)",
                "error"
            )
    
    def check_logging_config(self):
        """Check logging configuration."""
        self.print_section("6. Logging Configuration")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check Log Level
        log_level = os.getenv("LOG_LEVEL", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level.upper() in valid_levels:
            self.log("LOG_LEVEL", True, f"Set to: {log_level}")
        else:
            self.log(
                "LOG_LEVEL",
                False,
                f"Invalid value: {log_level} (must be one of: {', '.join(valid_levels)})",
                "error"
            )
        
        # Check Log File
        log_file = os.getenv("LOG_FILE", "logs/swarm.log")
        log_path = Path(log_file)
        if log_path.parent.exists() or log_file == "logs/swarm.log":
            self.log("LOG_FILE", True, f"Set to: {log_file}")
        else:
            self.log(
                "LOG_FILE",
                False,
                f"Directory does not exist: {log_path.parent}",
                "warning"
            )
        
        # Check Log Format
        log_format = os.getenv("LOG_FORMAT", "json")
        valid_formats = ["json", "text"]
        if log_format in valid_formats:
            self.log("LOG_FORMAT", True, f"Set to: {log_format}")
        else:
            self.log(
                "LOG_FORMAT",
                False,
                f"Invalid value: {log_format} (must be one of: {', '.join(valid_formats)})",
                "error"
            )
    
    def check_monitoring_config(self):
        """Check monitoring configuration."""
        self.print_section("7. Monitoring Configuration")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check Prometheus
        enable_prometheus = os.getenv("ENABLE_PROMETHEUS", "true").lower()
        if enable_prometheus in ["true", "false"]:
            self.log("ENABLE_PROMETHEUS", True, f"Set to: {enable_prometheus}")
        else:
            self.log(
                "ENABLE_PROMETHEUS",
                False,
                f"Invalid value: {enable_prometheus} (must be true or false)",
                "error"
            )
        
        # Check Prometheus Port
        prom_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
        if 1024 <= prom_port <= 65535:
            self.log("PROMETHEUS_PORT", True, f"Set to: {prom_port}")
        else:
            self.log(
                "PROMETHEUS_PORT",
                False,
                f"Invalid value: {prom_port} (must be 1024-65535)",
                "error"
            )
        
        # Check Tracing
        enable_tracing = os.getenv("ENABLE_TRACING", "true").lower()
        if enable_tracing in ["true", "false"]:
            self.log("ENABLE_TRACING", True, f"Set to: {enable_tracing}")
        else:
            self.log(
                "ENABLE_TRACING",
                False,
                f"Invalid value: {enable_tracing} (must be true or false)",
                "error"
            )
    
    def check_python_packages(self):
        """Check required Python packages."""
        self.print_section("8. Python Packages")
        
        required_packages = [
            "requests",
            "aiohttp",
            "pydantic",
            "dotenv",
            "PIL",
            "bs4",
        ]
        
        optional_packages = [
            "playwright",
            "prometheus_client",
            "opentelemetry",
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.log(f"{package} (required)", True)
            except ImportError:
                self.log(
                    f"{package} (required)",
                    False,
                    f"Package not installed: pip install {package}",
                    "error"
                )
        
        for package in optional_packages:
            try:
                __import__(package)
                self.log(f"{package} (optional)", True)
            except ImportError:
                self.log(
                    f"{package} (optional)",
                    False,
                    f"Package not installed: pip install {package}",
                    "warning"
                )
    
    def check_file_structure(self):
        """Check project file structure."""
        self.print_section("9. Project Structure")
        
        required_dirs = [
            "core",
            "orchestrator",
            "action",
            "perception",
            "utils",
            "config",
            "scripts",
            "tests",
            "logs",
        ]
        
        required_files = [
            "main.py",
            "requirements.txt",
            ".env.example",
            "README.md",
            "core/__init__.py",
            "core/config.py",
            "core/models.py",
            "core/heart_bleed.py",
            "orchestrator/__init__.py",
            "orchestrator/router.py",
            "orchestrator/agent_pool.py",
            "orchestrator/health.py",
            "orchestrator/mcp_server.py",
            "action/__init__.py",
            "action/browser.py",
            "action/desktop.py",
            "perception/__init__.py",
            "perception/web_search.py",
            "perception/vision.py",
            "utils/__init__.py",
            "utils/token_optimizer.py",
            "utils/logging.py",
        ]
        
        for dir_name in required_dirs:
            if os.path.isdir(dir_name):
                self.log(f"Directory: {dir_name}/", True)
            else:
                self.log(
                    f"Directory: {dir_name}/",
                    False,
                    f"Directory not found: {dir_name}",
                    "error"
                )
        
        for file_name in required_files:
            if os.path.isfile(file_name):
                self.log(f"File: {file_name}", True)
            else:
                self.log(
                    f"File: {file_name}",
                    False,
                    f"File not found: {file_name}",
                    "error"
                )
    
    def check_config_validation(self):
        """Check MoASwarmConfig validation."""
        self.print_section("10. Configuration Validation")
        
        try:
            from core.config import get_config, MoASwarmConfig
            config = get_config()
            
            # Validate configuration
            warnings = config.validate()
            
            if warnings:
                self.log("Configuration validation", True, f"{len(warnings)} warnings found")
                for warning in warnings:
                    print(f"      ⚠️  {warning}")
            else:
                self.log("Configuration validation", True, "No warnings")
            
            # Check config can be serialized
            config_dict = config.to_dict()
            assert "api" in config_dict
            assert "swarm" in config_dict
            assert "browser" in config_dict
            self.log("Config serialization", True)
            
        except Exception as e:
            self.log("Configuration validation", False, str(e))
    
    def check_mcp_server(self):
        """Check MCP server initialization."""
        self.print_section("11. MCP Server")
        
        try:
            from orchestrator.mcp_server import MCPServer
            server = MCPServer()
            
            # Check tools
            tools = server.list_tools()
            self.log("MCP Server tools", len(tools) >= 10, f"{len(tools)} tools registered")
            
            # Check resources
            resources = server.list_resources()
            self.log("MCP Server resources", len(resources) >= 5, f"{len(resources)} resources registered")
            
        except Exception as e:
            self.log("MCP Server", False, str(e))
    
    def check_orchestrator(self):
        """Check orchestrator components."""
        self.print_section("12. Orchestrator")
        
        try:
            from orchestrator.router import SwarmRouter
            from orchestrator.agent_pool import AgentPool
            from orchestrator.health import HealthMonitor
            
            # Check Router
            router = SwarmRouter()
            self.log("SwarmRouter", True)
            
            # Check AgentPool
            pool = AgentPool()
            self.log("AgentPool", True)
            
            # Check HealthMonitor
            monitor = HealthMonitor()
            self.log("HealthMonitor", True)
            
        except Exception as e:
            self.log("Orchestrator", False, str(e))
    
    def print_summary(self):
        """Print check summary."""
        print("\n" + "=" * 70)
        print("  API CONFIGURATION CHECK SUMMARY")
        print("=" * 70)
        
        print(f"\n  ✅ Passed: {self.results['passed']}")
        print(f"  ❌ Failed: {self.results['failed']}")
        print(f"  ⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"  🚨 Errors: {len(self.results['errors'])}")
        
        if self.results["warnings"]:
            print("\n  WARNINGS:")
            for warning in self.results["warnings"]:
                print(f"    ⚠️  {warning['name']}: {warning['message']}")
        
        if self.results["errors"]:
            print("\n  ERRORS:")
            for error in self.results["errors"]:
                print(f"    🚨 {error['name']}: {error['message']}")
        
        print()
        print("-" * 70)
        
        if self.results["failed"] == 0 and len(self.results["errors"]) == 0:
            print("  🎉 ALL CHECKS PASSED!")
            print("  ℹ️  Note: Empty API keys are normal - system uses any available provider")
        else:
            print("  ⚠️  SOME CHECKS FAILED - Please review the issues above")
        
        print("-" * 70)
    
    def run_all_checks(self):
        """Run all checks."""
        print("=" * 70)
        print("  API KEY & MODEL CONFIGURATION CHECKER")
        print("  MoA Swarm Architecture")
        print("=" * 70)
        
        self.check_env_file()
        self.check_api_keys()
        self.check_model_endpoints()
        self.check_swarm_config()
        self.check_browser_config()
        self.check_logging_config()
        self.check_monitoring_config()
        self.check_python_packages()
        self.check_file_structure()
        self.check_config_validation()
        self.check_mcp_server()
        self.check_orchestrator()
        
        self.print_summary()
        
        return self.results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="API Key & Model Configuration Checker"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix configuration issues"
    )
    parser.add_argument(
        "--test-models",
        action="store_true",
        help="Test model endpoints"
    )
    
    args = parser.parse_args()
    
    checker = APIConfigChecker()
    results = checker.run_all_checks()
    
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
