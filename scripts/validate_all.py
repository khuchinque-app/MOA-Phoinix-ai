#!/usr/bin/env python3
"""
validate_all.py — Comprehensive Validation Script

Runs all validation checks:
1. API key and model configuration
2. MCP server connection
3. Unit tests
4. System health check

Usage:
    python scripts/validate_all.py
    python scripts/validate_all.py --verbose
    python scripts/validate_all.py --quick

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import asyncio
import argparse
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_header():
    """Print validation header."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#  MoA SWARM ARCHITECTURE - COMPREHENSIVE VALIDATION" + " " * 17 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    print(f"\n  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


async def run_mcp_tests(verbose=False):
    """Run MCP connection tests."""
    print_section("MCP SERVER CONNECTION TEST")
    
    from scripts.test_mcp_connection import MCPConnectionTester
    tester = MCPConnectionTester(verbose=verbose)
    results = await tester.run_all_tests()
    return results


def run_api_config_check():
    """Run API configuration checks."""
    print_section("API KEY & MODEL CONFIGURATION CHECK")
    
    from scripts.check_api_config import APIConfigChecker
    checker = APIConfigChecker()
    results = checker.run_all_checks()
    return results


def run_unit_tests():
    """Run unit tests."""
    print_section("UNIT TESTS")
    
    from tests.unit.test_core import run_all_core_tests
    from tests.unit.test_orchestrator import run_all_orchestrator_tests
    from tests.unit.test_action import run_all_action_tests
    from tests.unit.test_perception import run_all_perception_tests
    from tests.unit.test_utils import run_all_utils_tests
    
    total_results = {"passed": 0, "failed": 0}
    
    test_suites = [
        ("Core", run_all_core_tests),
        ("Orchestrator", run_all_orchestrator_tests),
        ("Action", run_all_action_tests),
        ("Perception", run_all_perception_tests),
        ("Utils", run_all_utils_tests),
    ]
    
    for name, func in test_suites:
        try:
            results = func()
            total_results["passed"] += results["passed"]
            total_results["failed"] += results["failed"]
        except Exception as e:
            print(f"\n❌ {name} tests failed: {e}")
            total_results["failed"] += 1
    
    return total_results


def run_system_health_check():
    """Run system health check."""
    print_section("SYSTEM HEALTH CHECK")
    
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
    
    # Check Python version
    try:
        import sys
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        log("Python version", True, f"Python {version}")
    except Exception as e:
        log("Python version", False, str(e))
    
    # Check current directory
    try:
        cwd = os.getcwd()
        log("Working directory", True, cwd)
    except Exception as e:
        log("Working directory", False, str(e))
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        log("Disk space", free_gb > 1, f"{free_gb:.2f} GB free")
    except Exception as e:
        log("Disk space", False, str(e))
    
    # Check required directories
    try:
        required_dirs = ["core", "orchestrator", "action", "perception", "utils", "config", "scripts", "tests", "logs"]
        missing = [d for d in required_dirs if not os.path.isdir(d)]
        log("Project structure", len(missing) == 0, f"Missing: {', '.join(missing)}" if missing else "All directories present")
    except Exception as e:
        log("Project structure", False, str(e))
    
    return results


def print_final_summary(results):
    """Print final validation summary."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#  VALIDATION SUMMARY" + " " * 49 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    
    print("\n  Results:")
    print("  " + "-" * 66)
    
    for name, result in results.items():
        status = "✅" if result["failed"] == 0 else "❌"
        total = result["passed"] + result["failed"]
        print(f"  {status} {name:30s} {result['passed']:4d}/{total:4d} passed")
    
    print("  " + "-" * 66)
    
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_tests = total_passed + total_failed
    
    print(f"  {'TOTAL':30s} {total_passed:4d}/{total_tests:4d} passed")
    print(f"  {'PASS RATE':30s} {(total_passed/total_tests*100):6.1f}%")
    
    print()
    
    if total_failed == 0:
        print("  🎉 ALL VALIDATIONS PASSED! 🎉")
    else:
        print(f"  ⚠️  {total_failed} VALIDATION(S) FAILED")
    
    print()
    print("=" * 70)
    print(f"  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MoA Swarm Architecture - Comprehensive Validation"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick validation (skip unit tests)"
    )
    parser.add_argument(
        "--skip-mcp",
        action="store_true",
        help="Skip MCP connection tests"
    )
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip API configuration check"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip unit tests"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    start_time = time.time()
    all_results = {}
    
    # Run API config check
    if not args.skip_api:
        try:
            results = run_api_config_check()
            all_results["API Configuration"] = {
                "passed": results["passed"],
                "failed": results["failed"]
            }
        except Exception as e:
            print(f"\n❌ API Configuration check failed: {e}")
            all_results["API Configuration"] = {"passed": 0, "failed": 1}
    
    # Run MCP tests
    if not args.skip_mcp:
        try:
            results = await run_mcp_tests(verbose=args.verbose)
            all_results["MCP Connection"] = results
        except Exception as e:
            print(f"\n❌ MCP Connection test failed: {e}")
            all_results["MCP Connection"] = {"passed": 0, "failed": 1}
    
    # Run unit tests
    if not args.skip_tests and not args.quick:
        try:
            results = run_unit_tests()
            all_results["Unit Tests"] = results
        except Exception as e:
            print(f"\n❌ Unit tests failed: {e}")
            all_results["Unit Tests"] = {"passed": 0, "failed": 1}
    
    # Run system health check
    try:
        results = run_system_health_check()
        all_results["System Health"] = results
    except Exception as e:
        print(f"\n❌ System health check failed: {e}")
        all_results["System Health"] = {"passed": 0, "failed": 1}
    
    # Print final summary
    elapsed_time = time.time() - start_time
    print_final_summary(all_results)
    
    print(f"\n  Total time: {elapsed_time:.2f}s")
    
    total_failed = sum(r["failed"] for r in all_results.values())
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
