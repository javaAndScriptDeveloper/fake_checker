"""Core functionality for the propaganda detection system.

This package provides:
- Dependency injection container
- Caching layer for expensive operations
- Optimized manager implementation
"""

from core.dependency_injection import (
    ServiceContainer,
    DatabaseConfig,
    Neo4jConfig,
    AppConfig,
    ConfigurationError,
    get_container,
    reset_container,
)

from core.evaluator_cache import (
    TimedCache,
    CacheStats,
    get_embedding_cache,
    get_similarity_cache,
    get_sentiment_cache,
    clear_all_caches,
    get_all_cache_stats,
    cached_embedding,
    cached_similarity,
)

from core.optimized_manager import (
    OptimizedManager,
    ProcessingMetadata,
)

__all__ = [
    # Dependency Injection
    'ServiceContainer',
    'DatabaseConfig',
    'Neo4jConfig',
    'AppConfig',
    'ConfigurationError',
    'get_container',
    'reset_container',
    # Caching
    'TimedCache',
    'CacheStats',
    'get_embedding_cache',
    'get_similarity_cache',
    'get_sentiment_cache',
    'clear_all_caches',
    'get_all_cache_stats',
    'cached_embedding',
    'cached_similarity',
    # Manager
    'OptimizedManager',
    'ProcessingMetadata',
]
