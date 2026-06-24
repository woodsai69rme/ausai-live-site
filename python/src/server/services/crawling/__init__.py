"""
Crawling Services Package

This package contains services for web crawling, document processing, 
and related orchestration operations.
"""

from .crawling_service import (
    CrawlingService,
    CrawlOrchestrationService,
    get_active_orchestration,
    register_orchestration,
    unregister_orchestration
)

# Temporarily disabled - files not yet implemented
# from .enhanced_crawling_service import (
#     EnhancedCrawlingService,
#     EnhancedCrawlOrchestrationService
# )
# from .agentql_service import AgentQLService
# from .agentql_orchestrator import AgentQLOrchestrator

from .code_extraction_service import CodeExtractionService
from .document_storage_operations import DocumentStorageOperations
from .progress_mapper import ProgressMapper

# Export strategies
from .strategies.batch import BatchCrawlStrategy
from .strategies.recursive import RecursiveCrawlStrategy
from .strategies.single_page import SinglePageCrawlStrategy
from .strategies.sitemap import SitemapCrawlStrategy
# from .strategies.agentql_enhanced import AgentQLEnhancedStrategy  # Not implemented

# Export helpers
from .helpers.url_handler import URLHandler
from .helpers.site_config import SiteConfig

__all__ = [
    "CrawlingService",
    "CrawlOrchestrationService",
    # "EnhancedCrawlingService",
    # "EnhancedCrawlOrchestrationService",
    # "AgentQLService",
    # "AgentQLOrchestrator",
    "CodeExtractionService",
    "DocumentStorageOperations",
    "ProgressMapper",
    "BatchCrawlStrategy",
    "RecursiveCrawlStrategy",
    "SinglePageCrawlStrategy",
    "SitemapCrawlStrategy",
    # "AgentQLEnhancedStrategy",
    "URLHandler",
    "SiteConfig",
    "get_active_orchestration",
    "register_orchestration",
    "unregister_orchestration"
]
