"""
Web Search Integration
Optional component for retrieving information from the web
"""

import os
import yaml
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import time


class WebSearch:
    """Web search integration for RAG knowledge augmentation"""
    
    def __init__(self, config_path: str = "config/rag_config.yaml"):
        """Initialize web search client"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.ws_config = self.config['web_search']
        self.enabled = self.ws_config.get('enabled', False)
        
        if not self.enabled:
            print("Web search is disabled in configuration")
            return
        
        self.api_key = self.ws_config.get('api_key', '')
        self.max_results = self.ws_config.get('max_results', 3)
        self.search_language = self.ws_config.get('search_language', 'ar')
        
        # Cache directory
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize API client
        if self.api_key:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                print("Tavily web search initialized")
            except ImportError:
                print("Tavily not installed. Install with: pip install tavily-python")
                self.enabled = False
            except Exception as e:
                print(f"Error initializing Tavily: {e}")
                self.enabled = False
        else:
            print("No API key provided for web search")
            self.enabled = False
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for a query"""
        return hashlib.md5(query.encode('utf-8')).hexdigest()
    
    def _get_cached_results(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached search results"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            # Check if cache is recent (< 7 days)
            age_days = (time.time() - cache_file.stat().st_mtime) / 86400
            if age_days < 7:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        return None
    
    def _cache_results(self, query: str, results: Dict[str, Any]) -> None:
        """Cache search results"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def search(
        self,
        query: str,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Search the web for relevant information
        
        Args:
            query: Search query
            use_cache: Whether to use cached results
        
        Returns:
            List of search results with content and metadata
        """
        if not self.enabled:
            return []
        
        # Check cache first
        if use_cache:
            cached = self._get_cached_results(query)
            if cached:
                print(f"Using cached results for: {query[:50]}...")
                return cached.get('results', [])
        
        try:
            # Perform search
            print(f"Searching web for: {query[:50]}...")
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=self.max_results,
                include_domains=[],  # Add trusted Islamic law domains
                exclude_domains=[]
            )
            
            # Format results
            formatted_results = []
            for result in response.get('results', []):
                formatted_results.append({
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'score': result.get('score', 0.0),
                    'source_type': 'web_search'
                })
            
            # Cache results
            if use_cache:
                self._cache_results(query, {'results': formatted_results})
            
            return formatted_results
        
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def format_for_rag(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for RAG context
        
        Args:
            results: List of search results
        
        Returns:
            Formatted string for inclusion in prompt
        """
        if not results:
            return ""
        
        formatted = "# معلومات من البحث على الإنترنت:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"## مصدر {i}: {result['title']}\n"
            formatted += f"{result['content']}\n"
            formatted += f"المصدر: {result['url']}\n\n"
        
        return formatted
    
    def clear_cache(self) -> None:
        """Clear all cached search results"""
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            print("Search cache cleared")


if __name__ == "__main__":
    # Test web search
    search = WebSearch()
    
    if search.enabled:
        results = search.search("علم المواريث في الإسلام")
        print(f"Found {len(results)} results")
        
        if results:
            formatted = search.format_for_rag(results[:2])
            print(formatted[:500])
    else:
        print("Web search not available")
