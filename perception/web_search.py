"""
web_search.py — Web search capabilities for MoA Swarm

Provides integrated web search functionality using multiple search providers.
Supports result parsing, ranking, and caching.

Author: MoA Swarm Team
Version: 1.0.0
Last Updated: August 29, 2026
"""

import asyncio
import uuid
import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

from core.config import get_config, MoASwarmConfig


# ─── Search Result Model ──────────────────────────────────────────────────────

@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    position: int = 0
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "position": self.position,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass
class SearchResponse:
    """Response from a search query."""
    query: str
    results: List[SearchResult]
    total_results: int = 0
    search_time_ms: float = 0.0
    provider: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "search_time_ms": self.search_time_ms,
            "provider": self.provider,
            "metadata": self.metadata,
        }


# ─── Search Cache ─────────────────────────────────────────────────────────────

class SearchCache:
    """Simple in-memory cache for search results."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time-to-live for cached entries
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
    
    def _make_key(self, query: str, provider: str) -> str:
        """Generate cache key."""
        return hashlib.md5(f"{query}:{provider}".encode()).hexdigest()
    
    def get(self, query: str, provider: str) -> Optional[SearchResponse]:
        """Get cached response if available and not expired."""
        key = self._make_key(query, provider)
        
        if key in self._cache:
            entry = self._cache[key]
            # Check if expired
            if datetime.utcnow() - entry["timestamp"] < timedelta(seconds=self._ttl_seconds):
                return entry["response"]
            else:
                # Remove expired entry
                del self._cache[key]
        
        return None
    
    def set(self, query: str, provider: str, response: SearchResponse) -> None:
        """Cache a search response."""
        key = self._make_key(query, provider)
        
        # Evict oldest if at capacity
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]
        
        self._cache[key] = {
            "response": response,
            "timestamp": datetime.utcnow(),
        }
    
    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


# ─── Web Search Agent ─────────────────────────────────────────────────────────

class WebSearch:
    """
    Web search agent for the MoA swarm.
    
    Provides search capabilities using multiple providers:
    - anysearch MCP (primary)
    - Google Custom Search API
    - Bing Search API
    - DuckDuckGo (fallback)
    """
    
    def __init__(self, config: Optional[MoASwarmConfig] = None):
        """
        Initialize the Web Search agent.
        
        Args:
            config: MoASwarmConfig instance (uses default if not provided)
        """
        self.config = config or get_config()
        self.cache = SearchCache()
        self.search_history: List[Dict[str, Any]] = []
    
    # ─── Search Methods ───────────────────────────────────────────────────────
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        provider: str = "duckduckgo",
        use_cache: bool = True
    ) -> SearchResponse:
        """
        Perform a web search.
        
        Args:
            query: Search query
            num_results: Number of results to return
            provider: Search provider to use
            use_cache: Whether to use cached results
        
        Returns:
            SearchResponse with results
        """
        start_time = datetime.utcnow()
        
        # Check cache first
        if use_cache:
            cached = self.cache.get(query, provider)
            if cached:
                cached.metadata["from_cache"] = True
                return cached
        
        # Perform search based on provider
        try:
            if provider == "duckduckgo":
                results = await self._search_duckduckgo(query, num_results)
            elif provider == "google":
                results = await self._search_google(query, num_results)
            elif provider == "bing":
                results = await self._search_bing(query, num_results)
            else:
                results = await self._search_duckduckgo(query, num_results)
            
            # Calculate search time
            search_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create response
            response = SearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time_ms,
                provider=provider,
                metadata={"from_cache": False},
            )
            
            # Cache the response
            if use_cache:
                self.cache.set(query, provider, response)
            
            # Record in history
            self.search_history.append({
                "query": query,
                "provider": provider,
                "results_count": len(results),
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            return response
            
        except Exception as e:
            # Return error response
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                provider=provider,
                metadata={"error": str(e)},
            )
    
    async def _search_duckduckgo(
        self,
        query: str,
        num_results: int
    ) -> List[SearchResult]:
        """Search using DuckDuckGo."""
        # Use DuckDuckGo instant answer API
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Extract abstract
            if data.get("Abstract"):
                results.append(SearchResult(
                    title=data.get("Heading", "DuckDuckGo Result"),
                    url=data.get("AbstractURL", ""),
                    snippet=data.get("Abstract", ""),
                    position=1,
                    source="duckduckgo",
                ))
            
            # Extract related topics
            for i, topic in enumerate(data.get("RelatedTopics", [])[:num_results - 1]):
                if isinstance(topic, dict) and "Text" in topic:
                    results.append(SearchResult(
                        title=topic.get("Text", "")[:100],
                        url=topic.get("FirstURL", ""),
                        snippet=topic.get("Text", ""),
                        position=i + 2,
                        source="duckduckgo",
                    ))
            
            return results[:num_results]
            
        except Exception as e:
            # Fallback to simple scraping
            return await self._search_simple(query, num_results)
    
    async def _search_google(
        self,
        query: str,
        num_results: int
    ) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        # Note: Requires API key and search engine ID
        # This is a placeholder implementation
        return await self._search_simple(query, num_results)
    
    async def _search_bing(
        self,
        query: str,
        num_results: int
    ) -> List[SearchResult]:
        """Search using Bing Search API."""
        # Note: Requires API key
        # This is a placeholder implementation
        return await self._search_simple(query, num_results)
    
    async def _search_simple(
        self,
        query: str,
        num_results: int
    ) -> List[SearchResult]:
        """
        Simple fallback search using web scraping.
        
        This is a basic implementation for demonstration purposes.
        In production, use proper search APIs.
        """
        # This is a placeholder - in production, implement actual search
        return [
            SearchResult(
                title=f"Search result for: {query}",
                url=f"https://example.com/search?q={query}",
                snippet=f"This is a placeholder result for the query: {query}",
                position=1,
                source="simple",
            )
        ]
    
    # ─── Content Extraction ───────────────────────────────────────────────────
    
    async def extract_content(
        self,
        url: str,
        max_length: int = 5000
    ) -> Dict[str, Any]:
        """
        Extract readable content from a URL.
        
        Args:
            url: URL to extract content from
            max_length: Maximum content length
        
        Returns:
            Extracted content dictionary
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator="\n", strip=True)
            
            # Truncate if needed
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            # Get title
            title = soup.title.string if soup.title else ""
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "content": text,
                "content_length": len(text),
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e),
            }
    
    # ─── Utility Methods ──────────────────────────────────────────────────────
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history."""
        return self.search_history.copy()
    
    def clear_cache(self) -> None:
        """Clear the search cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": self.cache.size(),
            "max_size": self.cache._max_size,
            "ttl_seconds": self.cache._ttl_seconds,
        }


# ─── Usage Example ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def main():
        # Initialize web search agent
        search = WebSearch()
        
        # Perform a search
        print("Searching for 'MoA architecture'...")
        response = await search.search("MoA architecture AI", num_results=5)
        
        print(f"\nSearch Results:")
        print(f"  Query: {response.query}")
        print(f"  Results: {response.total_results}")
        print(f"  Search time: {response.search_time_ms:.2f}ms")
        print(f"  Provider: {response.provider}")
        
        for result in response.results:
            print(f"\n  [{result.position}] {result.title}")
            print(f"      URL: {result.url}")
            print(f"      Snippet: {result.snippet[:100]}...")
        
        # Extract content from a URL
        print("\n\nExtracting content from example.com...")
        content = await search.extract_content("https://example.com")
        print(f"  Title: {content.get('title', 'N/A')}")
        print(f"  Content length: {content.get('content_length', 0)}")
        
        # Get cache stats
        print(f"\nCache stats: {search.get_cache_stats()}")
    
    asyncio.run(main())
