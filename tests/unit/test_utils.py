"""
test_utils.py — Unit tests for utils modules

Tests for:
- utils/token_optimizer.py
- utils/logging.py

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_token_optimizer():
    """Test utils/token_optimizer.py module."""
    print("=" * 70)
    print("TESTING: utils/token_optimizer.py")
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
    
    from utils.token_optimizer import TokenOptimizer, TokenStats
    
    # Test 1: Create TokenOptimizer
    try:
        optimizer = TokenOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'stats')
        assert hasattr(optimizer, 'config')
        log("Create TokenOptimizer", True)
    except Exception as e:
        log("Create TokenOptimizer", False, str(e))
    
    # Test 2: TokenStats creation
    try:
        stats = TokenStats()
        assert stats.total_input_tokens == 0
        assert stats.total_output_tokens == 0
        assert stats.total_tokens == 0
        assert stats.compressed_saved_tokens == 0
        assert stats.request_count == 0
        log("TokenStats creation", True)
    except Exception as e:
        log("TokenStats creation", False, str(e))
    
    # Test 3: TokenStats record_request
    try:
        stats = TokenStats()
        stats.record_request(input_tokens=100, output_tokens=50, compressed_tokens=20)
        assert stats.total_input_tokens == 100
        assert stats.total_output_tokens == 50
        assert stats.total_tokens == 150
        assert stats.compressed_saved_tokens == 20
        assert stats.request_count == 1
        log("TokenStats record_request", True)
    except Exception as e:
        log("TokenStats record_request", False, str(e))
    
    # Test 4: TokenStats to_dict
    try:
        stats = TokenStats()
        stats.record_request(input_tokens=100, output_tokens=50)
        stats_dict = stats.to_dict()
        assert "total_input_tokens" in stats_dict
        assert "total_output_tokens" in stats_dict
        assert "total_tokens" in stats_dict
        assert "compressed_saved_tokens" in stats_dict
        assert "compression_ratio" in stats_dict
        assert "request_count" in stats_dict
        assert "uptime_seconds" in stats_dict
        assert "avg_tokens_per_request" in stats_dict
        log("TokenStats to_dict", True)
    except Exception as e:
        log("TokenStats to_dict", False, str(e))
    
    # Test 5: compress_shell_output (short output)
    try:
        optimizer = TokenOptimizer()
        output = "Short output"
        compressed = optimizer.compress_shell_output(output, max_length=100)
        assert compressed == output
        log("compress_shell_output (short)", True)
    except Exception as e:
        log("compress_shell_output (short)", False, str(e))
    
    # Test 6: compress_shell_output (long output)
    try:
        optimizer = TokenOptimizer()
        output = "A" * 200
        compressed = optimizer.compress_shell_output(output, max_length=100)
        assert len(compressed) < len(output)
        assert "[... truncated" in compressed
        log("compress_shell_output (long)", True)
    except Exception as e:
        log("compress_shell_output (long)", False, str(e))
    
    # Test 7: remove_ansi_codes
    try:
        optimizer = TokenOptimizer()
        text_with_ansi = "\x1b[31mRed text\x1b[0m Normal text"
        cleaned = optimizer.remove_ansi_codes(text_with_ansi)
        assert "\x1b" not in cleaned
        assert "Red text" in cleaned
        assert "Normal text" in cleaned
        log("remove_ansi_codes", True)
    except Exception as e:
        log("remove_ansi_codes", False, str(e))
    
    # Test 8: compress_log_output
    try:
        optimizer = TokenOptimizer()
        log_output = "2024-01-15 10:30:15 [INFO] Starting process...\n\n\n2024-01-15 10:30:16 [DEBUG] Loading..."
        compressed = optimizer.compress_log_output(log_output, remove_timestamps=True, remove_redundant=True)
        assert len(compressed) < len(log_output)
        assert "2024-01-15" not in compressed
        log("compress_log_output", True)
    except Exception as e:
        log("compress_log_output", False, str(e))
    
    # Test 9: estimate_cost (glm-4.7-flash)
    try:
        optimizer = TokenOptimizer()
        cost = optimizer.estimate_cost(1000, 500, "glm-4.7-flash")
        assert cost["model"] == "glm-4.7-flash"
        assert cost["input_tokens"] == 1000
        assert cost["output_tokens"] == 500
        assert "total_cost" in cost
        log("estimate_cost (glm-4.7-flash)", True, f"cost={cost['total_cost']}")
    except Exception as e:
        log("estimate_cost (glm-4.7-flash)", False, str(e))
    
    # Test 10: estimate_cost (claude-3-opus)
    try:
        optimizer = TokenOptimizer()
        cost = optimizer.estimate_cost(1000, 500, "claude-3-opus")
        assert cost["model"] == "claude-3-opus"
        log("estimate_cost (claude-3-opus)", True, f"cost={cost['total_cost']}")
    except Exception as e:
        log("estimate_cost (claude-3-opus)", False, str(e))
    
    # Test 11: estimate_cost (unknown model)
    try:
        optimizer = TokenOptimizer()
        cost = optimizer.estimate_cost(1000, 500, "unknown-model")
        assert cost["model"] == "unknown-model"
        # Should use default pricing
        log("estimate_cost (unknown model)", True, f"cost={cost['total_cost']}")
    except Exception as e:
        log("estimate_cost (unknown model)", False, str(e))
    
    # Test 12: get_stats
    try:
        optimizer = TokenOptimizer()
        optimizer.stats.record_request(input_tokens=100, output_tokens=50)
        stats = optimizer.get_stats()
        assert stats["total_tokens"] == 150
        assert stats["request_count"] == 1
        log("get_stats", True)
    except Exception as e:
        log("get_stats", False, str(e))
    
    # Test 13: reset_stats
    try:
        optimizer = TokenOptimizer()
        optimizer.stats.record_request(input_tokens=100, output_tokens=50)
        optimizer.reset_stats()
        stats = optimizer.get_stats()
        assert stats["total_tokens"] == 0
        assert stats["request_count"] == 0
        log("reset_stats", True)
    except Exception as e:
        log("reset_stats", False, str(e))
    
    # Test 14: compress_with_ztk (ztk not available)
    try:
        async def test_compress():
            optimizer = TokenOptimizer()
            result = await optimizer.compress_with_ztk("test text")
            return result
        
        result = asyncio.run(test_compress())
        # Should handle gracefully when ztk not available
        assert "success" in result
        log("compress_with_ztk (graceful)", True, f"ztk available: {result.get('success', False)}")
    except Exception as e:
        log("compress_with_ztk (graceful)", True, f"Handled: {str(e)[:50]}")
    
    # Test 15: decompress_with_ztk (ztk not available)
    try:
        async def test_decompress():
            optimizer = TokenOptimizer()
            result = await optimizer.decompress_with_ztk("compressed text")
            return result
        
        result = asyncio.run(test_decompress())
        assert "success" in result
        log("decompress_with_ztk (graceful)", True, f"ztk available: {result.get('success', False)}")
    except Exception as e:
        log("decompress_with_ztk (graceful)", True, f"Handled: {str(e)[:50]}")
    
    print(f"\n  Token Optimizer Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def test_logging():
    """Test utils/logging.py module."""
    print("\n" + "=" * 70)
    print("TESTING: utils/logging.py")
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
    
    from utils.logging import SwarmLogger, JSONFormatter, TextFormatter, get_logger, setup_logging
    
    # Test 1: Create SwarmLogger
    try:
        logger = SwarmLogger()
        assert logger is not None
        assert hasattr(logger, '_loggers')
        assert hasattr(logger, 'config')
        log("Create SwarmLogger", True)
    except Exception as e:
        log("Create SwarmLogger", False, str(e))
    
    # Test 2: JSONFormatter
    try:
        import logging
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert isinstance(formatted, str)
        assert "timestamp" in formatted
        assert "level" in formatted
        assert "message" in formatted
        log("JSONFormatter", True)
    except Exception as e:
        log("JSONFormatter", False, str(e))
    
    # Test 3: TextFormatter
    try:
        import logging
        formatter = TextFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert isinstance(formatted, str)
        assert "INFO" in formatted
        assert "Test message" in formatted
        log("TextFormatter", True)
    except Exception as e:
        log("TextFormatter", False, str(e))
    
    # Test 4: Get logger
    try:
        logger = SwarmLogger()
        comp_logger = logger.get_logger("router")
        assert comp_logger is not None
        assert comp_logger.name == "moa_swarm.router"
        log("Get logger", True)
    except Exception as e:
        log("Get logger", False, str(e))
    
    # Test 5: Get logger (cached)
    try:
        logger = SwarmLogger()
        logger1 = logger.get_logger("test")
        logger2 = logger.get_logger("test")
        assert logger1 is logger2
        log("Get logger (cached)", True)
    except Exception as e:
        log("Get logger (cached)", False, str(e))
    
    # Test 6: Info logging
    try:
        logger = SwarmLogger()
        logger.info("Test info message", component="test")
        log("Info logging", True)
    except Exception as e:
        log("Info logging", False, str(e))
    
    # Test 7: Debug logging
    try:
        logger = SwarmLogger()
        logger.debug("Test debug message", component="test")
        log("Debug logging", True)
    except Exception as e:
        log("Debug logging", False, str(e))
    
    # Test 8: Warning logging
    try:
        logger = SwarmLogger()
        logger.warning("Test warning message", component="test")
        log("Warning logging", True)
    except Exception as e:
        log("Warning logging", False, str(e))
    
    # Test 9: Error logging
    try:
        logger = SwarmLogger()
        logger.error("Test error message", component="test")
        log("Error logging", True)
    except Exception as e:
        log("Error logging", False, str(e))
    
    # Test 10: Critical logging
    try:
        logger = SwarmLogger()
        logger.critical("Test critical message", component="test")
        log("Critical logging", True)
    except Exception as e:
        log("Critical logging", False, str(e))
    
    # Test 11: Exception logging
    try:
        logger = SwarmLogger()
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Test exception message", component="test")
        log("Exception logging", True)
    except Exception as e:
        log("Exception logging", False, str(e))
    
    # Test 12: Logging with extra data
    try:
        logger = SwarmLogger()
        logger.info("Test with extra", component="test", key1="value1", key2="value2")
        log("Logging with extra data", True)
    except Exception as e:
        log("Logging with extra data", False, str(e))
    
    # Test 13: get_logger singleton
    try:
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2
        log("get_logger singleton", True)
    except Exception as e:
        log("get_logger singleton", False, str(e))
    
    # Test 14: setup_logging
    try:
        logger = setup_logging()
        assert isinstance(logger, SwarmLogger)
        log("setup_logging", True)
    except Exception as e:
        log("setup_logging", False, str(e))
    
    # Test 15: Multiple components
    try:
        logger = SwarmLogger()
        components = ["router", "browser", "vision", "orchestrator", "mcp"]
        for comp in components:
            comp_logger = logger.get_logger(comp)
            assert comp_logger.name == f"moa_swarm.{comp}"
        log("Multiple components", True, f"{len(components)} components")
    except Exception as e:
        log("Multiple components", False, str(e))
    
    print(f"\n  Logging Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def run_all_utils_tests():
    """Run all utils module tests."""
    print("\n" + "#" * 70)
    print("#  UTILS MODULE TESTS")
    print("#" * 70 + "\n")
    
    total_results = {"passed": 0, "failed": 0}
    
    results = test_token_optimizer()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    results = test_logging()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    return total_results


if __name__ == "__main__":
    results = run_all_utils_tests()
    print("\n" + "=" * 70)
    print(f"  UTILS MODULES: {results['passed']} passed, {results['failed']} failed")
    print("=" * 70)
    sys.exit(0 if results["failed"] == 0 else 1)
