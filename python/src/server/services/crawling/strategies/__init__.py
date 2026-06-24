"""
Crawling Strategies

This module contains different crawling strategies for various URL types.
"""

from .batch import BatchCrawlStrategy
from .recursive import RecursiveCrawlStrategy
from .single_page import SinglePageCrawlStrategy
from .sitemap import SitemapCrawlStrategy
# from .agentql_enhanced import AgentQLEnhancedStrategy  # Not yet implemented

__all__ = [
    'BatchCrawlStrategy',
    'RecursiveCrawlStrategy',
    'SinglePageCrawlStrategy',
    'SitemapCrawlStrategy',
    # 'AgentQLEnhancedStrategy'  # Not yet implemented
]