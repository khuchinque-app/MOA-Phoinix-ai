"""
run_all_tests.py — Main test runner for all unit tests

Runs all unit tests and provides a comprehensive summary.

Usage:
    python tests/run_all_tests.py

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.unit.test_core import run_all_core_tests
from tests.unit.test_orchestrator import run_all_orchestrator_tests
from tests.unit.test_action import run_all_action_tests
from tests.unit.test_perception import run_all_perception_tests
from tests.unit.test_utils import run_all_utils_tests


def main():
    """Run all tests and print summary."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#  MoA SWARM ARCHITECTURE - COMPREHENSIVE UNIT TESTS" + " " * 17 + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)
    print(f"\n  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    all_results = {}
    
    # Run all test suites
    test_suites = [
        ("Core Modules", run_all_core_tests),
        ("Orchestrator Modules", run_all_orchestrator_tests),
        ("Action Modules", run_all_action_tests),
        ("Perception Modules", run_all_perception_tests),
        ("Utils Modules", run_all_utils_tests),
    ]
    
    for suite_name, suite_func in test_suites:
        try:
            results = suite_func()
            all_results[suite_name] = results
        except Exception as e:
            print(f"\n❌ {suite_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            all_results[suite_name] = {"passed": 0, "failed": 1}
    
    # Calculate totals
    total_passed = sum(r["passed"] for r in all_results.values())
    total_failed = sum(r["failed"] for r in all_results.values())
    total_tests = total_passed + total_failed
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print()
    
    for suite_name, results in all_results.items():
        status = "✅" if results["failed"] == 0 else "❌"
        print(f"  {status} {suite_name:30s} {results['passed']:4d} passed, {results['failed']:4d} failed")
    
    print()
    print("-" * 70)
    print(f"  {'TOTAL':30s} {total_passed:4d} passed, {total_failed:4d} failed")
    print(f"  {'TOTAL TESTS':30s} {total_tests:4d}")
    print(f"  {'PASS RATE':30s} {(total_passed/total_tests*100):6.1f}%")
    print(f"  {'TIME':30s} {elapsed_time:.2f}s")
    print("-" * 70)
    
    if total_failed == 0:
        print("\n  🎉 ALL TESTS PASSED! 🎉\n")
    else:
        print(f"\n  ⚠️  {total_failed} TEST(S) FAILED ⚠️\n")
    
    print("=" * 70)
    print(f"  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
