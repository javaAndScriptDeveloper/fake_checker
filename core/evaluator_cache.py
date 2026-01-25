"""Caching layer for expensive evaluation computations.

This module provides memoization and caching for expensive operations
like text embeddings, ML model outputs, and similarity calculations.
"""
from typing import Dict, Tuple, Any, Optional, Callable
from functools import wraps, lru_cache
from dataclasses import dataclass
import hashlib
import time
from threading import Lock
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheStats:
    """Track cache statistics."""
    
    def __init__(self):
        self.hits: int = 0
        self.misses: int = 0
        self.total_time_saved: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    def record_hit(self, time_saved: float = 0.0):
        """Record a cache hit."""
        self.hits += 1
        self.total_time_saved += time_saved
    
    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
    
    def reset(self):
        """Reset statistics."""
        self.hits = 0
        self.misses = 0
        self.total_time_saved = 0.0


@dataclass
class CacheEntry:
    """A cached entry with metadata."""
    value: Any
    timestamp: float
    size: int
    compute_time: float


class TimedCache:
    """Thread-safe cache with TTL and statistics.
    
    This cache supports:
    - Time-to-live (TTL) expiration
    - Thread-safe operations
    - Statistics tracking
    - Size-based eviction
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[float] = None):
        """Initialize cache.
        
        Args:
            max_size: Maximum number of entries
            ttl_seconds: Optional time-to-live in seconds
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._stats = CacheStats()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats.record_miss()
                return None
            
            entry = self._cache[key]
            
            # Check TTL
            if self._ttl_seconds and (time.time() - entry.timestamp) > self._ttl_seconds:
                del self._cache[key]
                self._stats.record_miss()
                return None
            
            self._stats.record_hit()
            logger.debug(f"Cache hit for key: {key[:8]}...")
            return entry.value
    
    def set(self, key: str, value: Any, compute_time: float = 0.0) -> None:
        """Set value in cache."""
        with self._lock:
            # Calculate size (approximate)
            size = len(str(value))
            
            # Evict if full (simple FIFO)
            if len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"Cache eviction: {oldest_key[:8]}...")
            
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                size=size,
                compute_time=compute_time
            )
            logger.debug(f"Cache set: {key[:8]}...")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._stats.reset()
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'entries': len(self._cache),
                'hits': self._stats.hits,
                'misses': self._stats.misses,
                'hit_rate': self._stats.hit_rate,
                'total_time_saved': self._stats.total_time_saved,
            }


# Global caches
# Use separate caches for different types of data to avoid conflicts
_embedding_cache: Optional[TimedCache] = None
_similarity_cache: Optional[TimedCache] = None
_sentiment_cache: Optional[TimedCache] = None


def get_embedding_cache() -> TimedCache:
    """Get or create embedding cache (long TTL)."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = TimedCache(max_size=500, ttl_seconds=3600)  # 1 hour
    return _embedding_cache


def get_similarity_cache() -> TimedCache:
    """Get or create similarity cache (medium TTL)."""
    global _similarity_cache
    if _similarity_cache is None:
        _similarity_cache = TimedCache(max_size=1000, ttl_seconds=600)  # 10 minutes
    return _similarity_cache


def get_sentiment_cache() -> TimedCache:
    """Get or create sentiment cache (short TTL)."""
    global _sentiment_cache
    if _sentiment_cache is None:
        _sentiment_cache = TimedCache(max_size=2000, ttl_seconds=300)  # 5 minutes
    return _sentiment_cache


def clear_all_caches() -> None:
    """Clear all global caches."""
    global _embedding_cache, _similarity_cache, _sentiment_cache
    
    if _embedding_cache:
        _embedding_cache.clear()
    if _similarity_cache:
        _similarity_cache.clear()
    if _sentiment_cache:
        _sentiment_cache.clear()
    
    logger.info("All caches cleared")


def cached_embedding(func: Callable) -> Callable:
    """Decorator for caching embedding computations.
    
    Args:
        func: Function that returns an embedding
        
    Returns:
        Decorated function with caching
    """
    @wraps(func)
    def wrapper(text: str, *args, **kwargs):
        cache = get_embedding_cache()
        key = hashlib.md5(text.encode()).hexdigest()
        
        # Try cache
        result = cache.get(key)
        if result is not None:
            return result
        
        # Compute
        start = time.perf_counter()
        result = func(text, *args, **kwargs)
        elapsed = time.perf_counter() - start
        
        # Cache result
        cache.set(key, result, compute_time=elapsed)
        
        return result
    
    return wrapper


def cached_similarity(func: Callable) -> Callable:
    """Decorator for caching similarity computations.
    
    Args:
        func: Function that returns similarity score
        
    Returns:
        Decorated function with caching
    """
    @wraps(func)
    def wrapper(text1: str, text2: str, *args, **kwargs):
        cache = get_similarity_cache()
        # Sort texts to ensure order-independent caching
        texts = sorted([text1, text2])
        key = hashlib.md5((texts[0] + texts[1]).encode()).hexdigest()
        
        # Try cache
        result = cache.get(key)
        if result is not None:
            return result
        
        # Compute
        start = time.perf_counter()
        result = func(text1, text2, *args, **kwargs)
        elapsed = time.perf_counter() - start
        
        # Cache result
        cache.set(key, result, compute_time=elapsed)
        
        return result
    
    return wrapper


def get_all_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches."""
    stats = {}
    
    if _embedding_cache:
        stats['embedding'] = _embedding_cache.get_stats()
    
    if _similarity_cache:
        stats['similarity'] = _similarity_cache.get_stats()
    
    if _sentiment_cache:
        stats['sentiment'] = _sentiment_cache.get_stats()
    
    return stats
