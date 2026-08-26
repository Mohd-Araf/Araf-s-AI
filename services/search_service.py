"""
Search Service for Araf's Assistant.
Performs live web searches using DuckDuckGo and structures citations.
"""
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Keywords triggering web search heuristic
SEARCH_TRIGGER_KEYWORDS = [
    'latest', 'today', 'current', 'news', 'weather', 'price', 'release', 'update',
    'score', 'match', 'election', 'who is', 'when did', 'version',
    'আজকের', 'বর্তমান', 'খবর', 'দাম', 'আপডেট', 'সর্বশেষ', 'আজকে', 'রিলিজ'
]

def should_search_web(query: str, manual_override: bool = None) -> bool:
    """
    Determines if web search is needed based on query semantics or user override.
    """
    if manual_override is not None:
        return manual_override

    query_lower = query.lower()
    
    # Check keyword triggers
    for kw in SEARCH_TRIGGER_KEYWORDS:
        if kw in query_lower:
            return True
            
    # Check for specific year patterns (e.g. 2025, 2026)
    if re.search(r'\b202[4-9]\b', query):
        return True

    return False

def search_web(query: str, max_results: int = 4) -> Tuple[str, List[Dict[str, str]]]:
    """
    Executes a web search and returns:
    1. Formatted search context string for the AI prompt.
    2. Structured list of citation dictionaries [{title, url, snippet}].
    """
    citations = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return "", []

            context_lines = []
            for i, r in enumerate(results, 1):
                title = r.get('title', 'Untitled')
                url = r.get('href', '')
                snippet = r.get('body', '')
                
                citations.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
                context_lines.append(f"[{i}] Title: {title}\nURL: {url}\nSnippet: {snippet}\n")

            context_str = "\n".join(context_lines)
            return context_str, citations

    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}. Falling back to empty search context.")
        return "", []
