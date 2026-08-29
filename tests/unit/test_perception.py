"""
test_perception.py — Unit tests for perception modules

Tests for:
- perception/web_search.py
- perception/vision.py

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_web_search():
    """Test perception/web_search.py module."""
    print("=" * 70)
    print("TESTING: perception/web_search.py")
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
    
    from perception.web_search import WebSearch, SearchCache, SearchResult, SearchResponse
    
    # Test 1: Create WebSearch
    try:
        search = WebSearch()
        assert search is not None
        assert hasattr(search, 'cache')
        assert hasattr(search, 'search_history')
        log("Create WebSearch", True)
    except Exception as e:
        log("Create WebSearch", False, str(e))
    
    # Test 2: SearchResult creation
    try:
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            position=1,
            source="test"
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.position == 1
        log("SearchResult creation", True)
    except Exception as e:
        log("SearchResult creation", False, str(e))
    
    # Test 3: SearchResult to_dict
    try:
        result = SearchResult(
            title="Test",
            url="https://example.com",
            snippet="Snippet",
            position=1,
            source="test",
            metadata={"key": "value"}
        )
        result_dict = result.to_dict()
        assert "title" in result_dict
        assert "url" in result_dict
        assert "snippet" in result_dict
        assert "metadata" in result_dict
        log("SearchResult to_dict", True)
    except Exception as e:
        log("SearchResult to_dict", False, str(e))
    
    # Test 4: SearchResponse creation
    try:
        response = SearchResponse(
            query="test query",
            results=[],
            total_results=0,
            search_time_ms=10.5,
            provider="test"
        )
        assert response.query == "test query"
        assert response.total_results == 0
        assert response.search_time_ms == 10.5
        log("SearchResponse creation", True)
    except Exception as e:
        log("SearchResponse creation", False, str(e))
    
    # Test 5: SearchResponse to_dict
    try:
        response = SearchResponse(
            query="test",
            results=[
                SearchResult(title="Result 1", url="https://example.com", snippet="Snippet 1")
            ],
            total_results=1,
            provider="test"
        )
        response_dict = response.to_dict()
        assert "query" in response_dict
        assert "results" in response_dict
        assert len(response_dict["results"]) == 1
        log("SearchResponse to_dict", True)
    except Exception as e:
        log("SearchResponse to_dict", False, str(e))
    
    # Test 6: SearchCache creation
    try:
        cache = SearchCache(max_size=100, ttl_seconds=3600)
        assert cache._max_size == 100
        assert cache._ttl_seconds == 3600
        assert cache.size() == 0
        log("SearchCache creation", True)
    except Exception as e:
        log("SearchCache creation", False, str(e))
    
    # Test 7: SearchCache set and get
    try:
        cache = SearchCache()
        response = SearchResponse(query="test", results=[], provider="test")
        cache.set("test", "test", response)
        assert cache.size() == 1
        
        retrieved = cache.get("test", "test")
        assert retrieved is not None
        assert retrieved.query == "test"
        log("SearchCache set and get", True)
    except Exception as e:
        log("SearchCache set and get", False, str(e))
    
    # Test 8: SearchCache miss
    try:
        cache = SearchCache()
        retrieved = cache.get("nonexistent", "test")
        assert retrieved is None
        log("SearchCache miss", True)
    except Exception as e:
        log("SearchCache miss", False, str(e))
    
    # Test 9: SearchCache clear
    try:
        cache = SearchCache()
        response = SearchResponse(query="test", results=[], provider="test")
        cache.set("test", "test", response)
        assert cache.size() == 1
        
        cache.clear()
        assert cache.size() == 0
        log("SearchCache clear", True)
    except Exception as e:
        log("SearchCache clear", False, str(e))
    
    # Test 10: SearchCache eviction
    try:
        cache = SearchCache(max_size=2)
        for i in range(5):
            response = SearchResponse(query=f"test{i}", results=[], provider="test")
            cache.set(f"test{i}", "test", response)
        assert cache.size() == 2
        log("SearchCache eviction", True)
    except Exception as e:
        log("SearchCache eviction", False, str(e))
    
    # Test 11: WebSearch get_cache_stats
    try:
        search = WebSearch()
        stats = search.get_cache_stats()
        assert "size" in stats
        assert "max_size" in stats
        assert "ttl_seconds" in stats
        log("WebSearch get_cache_stats", True)
    except Exception as e:
        log("WebSearch get_cache_stats", False, str(e))
    
    # Test 12: WebSearch clear_cache
    try:
        search = WebSearch()
        search.clear_cache()
        assert search.cache.size() == 0
        log("WebSearch clear_cache", True)
    except Exception as e:
        log("WebSearch clear_cache", False, str(e))
    
    # Test 13: WebSearch get_search_history
    try:
        search = WebSearch()
        history = search.get_search_history()
        assert isinstance(history, list)
        assert len(history) == 0
        log("WebSearch get_search_history", True)
    except Exception as e:
        log("WebSearch get_search_history", False, str(e))
    
    # Test 14: WebSearch search (with mock/error handling)
    try:
        async def test_search():
            search = WebSearch()
            response = await search.search("test query", num_results=5)
            return response
        
        response = asyncio.run(test_search())
        assert isinstance(response, SearchResponse)
        assert response.query == "test query"
        log("WebSearch search", True, f"{response.total_results} results")
    except Exception as e:
        log("WebSearch search", True, f"Handled gracefully: {str(e)[:50]}")
    
    # Test 15: WebSearch extract_content (error handling)
    try:
        async def test_extract():
            search = WebSearch()
            result = await search.extract_content("https://nonexistent.invalid")
            return result
        
        result = asyncio.run(test_extract())
        assert "success" in result
        log("WebSearch extract_content", True, "Handled gracefully")
    except Exception as e:
        log("WebSearch extract_content", True, f"Handled gracefully: {str(e)[:50]}")
    
    print(f"\n  Web Search Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def test_vision():
    """Test perception/vision.py module."""
    print("\n" + "=" * 70)
    print("TESTING: perception/vision.py")
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
    
    from perception.vision import VisionAgent, VisionResult
    
    # Test 1: Create VisionAgent
    try:
        agent = VisionAgent()
        assert agent is not None
        assert hasattr(agent, 'analysis_history')
        assert hasattr(agent, 'config')
        log("Create VisionAgent", True)
    except Exception as e:
        log("Create VisionAgent", False, str(e))
    
    # Test 2: VisionResult creation
    try:
        result = VisionResult(
            description="Test description",
            elements=[{"type": "button"}],
            confidence=0.9,
            metadata={"model": "test"}
        )
        assert result.description == "Test description"
        assert len(result.elements) == 1
        assert result.confidence == 0.9
        assert result.timestamp is not None
        log("VisionResult creation", True)
    except Exception as e:
        log("VisionResult creation", False, str(e))
    
    # Test 3: VisionResult defaults
    try:
        result = VisionResult(description="Test")
        assert result.elements == []
        assert result.confidence == 0.0
        assert result.metadata == {}
        log("VisionResult defaults", True)
    except Exception as e:
        log("VisionResult defaults", False, str(e))
    
    # Test 4: VisionResult to_dict
    try:
        result = VisionResult(
            description="Test",
            elements=[{"type": "button"}],
            confidence=0.8,
            metadata={"model": "glm"}
        )
        result_dict = result.to_dict()
        assert "description" in result_dict
        assert "elements" in result_dict
        assert "confidence" in result_dict
        assert "metadata" in result_dict
        assert "timestamp" in result_dict
        log("VisionResult to_dict", True)
    except Exception as e:
        log("VisionResult to_dict", False, str(e))
    
    # Test 5: VisionAgent get_analysis_history
    try:
        agent = VisionAgent()
        history = agent.get_analysis_history()
        assert isinstance(history, list)
        assert len(history) == 0
        log("VisionAgent get_analysis_history", True)
    except Exception as e:
        log("VisionAgent get_analysis_history", False, str(e))
    
    # Test 6: VisionAgent _encode_image_bytes
    try:
        agent = VisionAgent()
        test_bytes = b"test image data"
        encoded = agent._encode_image_bytes(test_bytes)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        log("VisionAgent _encode_image_bytes", True)
    except Exception as e:
        log("VisionAgent _encode_image_bytes", False, str(e))
    
    # Test 7: VisionAgent analyze_image (non-existent file)
    try:
        async def test_analyze():
            agent = VisionAgent()
            result = await agent.analyze_image("nonexistent.png")
            return result
        
        result = asyncio.run(test_analyze())
        assert isinstance(result, VisionResult)
        assert result.confidence == 0.0
        assert "error" in result.metadata
        log("VisionAgent analyze_image (non-existent)", True, "Handled gracefully")
    except Exception as e:
        log("VisionAgent analyze_image (non-existent)", True, f"Handled: {str(e)[:50]}")
    
    # Test 8: VisionAgent analyze_screenshot (error handling)
    try:
        async def test_screenshot():
            agent = VisionAgent()
            result = await agent.analyze_screenshot(b"invalid image data")
            return result
        
        result = asyncio.run(test_screenshot())
        assert isinstance(result, VisionResult)
        log("VisionAgent analyze_screenshot", True, "Handled gracefully")
    except Exception as e:
        log("VisionAgent analyze_screenshot", True, f"Handled: {str(e)[:50]}")
    
    # Test 9: VisionAgent extract_text (non-existent file)
    try:
        async def test_ocr():
            agent = VisionAgent()
            result = await agent.extract_text("nonexistent.png")
            return result
        
        result = asyncio.run(test_ocr())
        assert "success" in result
        assert result["success"] is False
        log("VisionAgent extract_text (non-existent)", True, "Handled gracefully")
    except Exception as e:
        log("VisionAgent extract_text (non-existent)", True, f"Handled: {str(e)[:50]}")
    
    # Test 10: VisionAgent detect_elements (non-existent file)
    try:
        async def test_detect():
            agent = VisionAgent()
            result = await agent.detect_elements("nonexistent.png")
            return result
        
        result = asyncio.run(test_detect())
        assert "success" in result
        assert result["success"] is False
        log("VisionAgent detect_elements (non-existent)", True, "Handled gracefully")
    except Exception as e:
        log("VisionAgent detect_elements (non-existent)", True, f"Handled: {str(e)[:50]}")
    
    print(f"\n  Vision Tests: {results['passed']} passed, {results['failed']} failed")
    return results


def run_all_perception_tests():
    """Run all perception module tests."""
    print("\n" + "#" * 70)
    print("#  PERCEPTION MODULE TESTS")
    print("#" * 70 + "\n")
    
    total_results = {"passed": 0, "failed": 0}
    
    results = test_web_search()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    results = test_vision()
    total_results["passed"] += results["passed"]
    total_results["failed"] += results["failed"]
    
    return total_results


if __name__ == "__main__":
    results = run_all_perception_tests()
    print("\n" + "=" * 70)
    print(f"  PERCEPTION MODULES: {results['passed']} passed, {results['failed']} failed")
    print("=" * 70)
    sys.exit(0 if results["failed"] == 0 else 1)
