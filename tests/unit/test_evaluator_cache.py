"""Tests for Evaluator Cache module."""
import pytest
import time
from unittest.mock import Mock, patch

from core.evaluator_cache import (
    CacheStats,
    TimedCache,
    CacheEntry,
    get_embedding_cache,
    get_similarity_cache,
    get_sentiment_cache,
    clear_all_caches,
    get_all_cache_stats,
    cached_embedding,
    cached_similarity,
)


class TestCacheStats:
    """Test cases for CacheStats."""
    
    def test_initialization(self):
        """Test stats initialization."""
        stats = CacheStats()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_time_saved == 0.0
    
    def test_record_hit(self):
        """Test recording a cache hit."""
        stats = CacheStats()
        
        stats.record_hit(0.5)
        
        assert stats.hits == 1
        assert stats.total_time_saved == 0.5
    
    def test_record_multiple_hits(self):
        """Test recording multiple hits."""
        stats = CacheStats()
        
        stats.record_hit(0.3)
        stats.record_hit(0.2)
        
        assert stats.hits == 2
        assert stats.total_time_saved == 0.5
    
    def test_record_miss(self):
        """Test recording a cache miss."""
        stats = CacheStats()
        
        stats.record_miss()
        
        assert stats.misses == 1
    
    def test_hit_rate(self):
        """Test hit rate calculation."""
        stats = CacheStats()
        
        # No requests yet
        assert stats.hit_rate == 0.0
        
        # Some hits, no misses
        for _ in range(10):
            stats.record_hit()
        assert stats.hit_rate == 100.0
        
        # Mix of hits and misses
        stats.record_miss()  # 10 hits, 1 miss
        assert 90.9 < stats.hit_rate < 91.0  # Approximately 90.9%
    
    def test_reset(self):
        """Test resetting stats."""
        stats = CacheStats()
        
        stats.record_hit(0.5)
        stats.record_miss()
        
        stats.reset()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_time_saved == 0.0


class TestTimedCache:
    """Test cases for TimedCache."""
    
    @pytest.fixture
    def cache(self):
        """Create a test cache."""
        return TimedCache(max_size=10, ttl_seconds=None)
    
    def test_initialization(self, cache):
        """Test cache initialization."""
        assert len(cache._cache) == 0
        assert cache._max_size == 10
        assert cache._ttl_seconds is None
    
    def test_set_and_get(self, cache):
        """Test setting and getting values."""
        cache.set('key1', 'value1')
        result = cache.get('key1')
        
        assert result == 'value1'
    
    def test_get_nonexistent(self, cache):
        """Test getting non-existent key."""
        result = cache.get('nonexistent')
        
        assert result is None
    
    def test_update_existing_key(self, cache):
        """Test updating existing key."""
        cache.set('key1', 'value1')
        cache.set('key1', 'value2')
        result = cache.get('key1')
        
        assert result == 'value2'
    
    def test_eviction_fifo(self, cache):
        """Test FIFO eviction when cache is full."""
        # Fill cache to max
        for i in range(10):
            cache.set(f'key{i}', f'value{i}')
        
        assert len(cache._cache) == 10
        
        # Add one more - should evict first
        cache.set('key10', 'value10')
        
        assert len(cache._cache) == 10
        assert cache.get('key0') is None  # Evicted
        assert cache.get('key1') == 'value1'  # Still there
        assert cache.get('key10') == 'value10'  # New entry
    
    def test_ttl_expiration(self):
        """Test TTL-based expiration."""
        # Short TTL: 0.1 seconds
        cache = TimedCache(max_size=10, ttl_seconds=0.1)
        
        cache.set('key1', 'value1')
        
        # Should be available immediately
        assert cache.get('key1') == 'value1'
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        result = cache.get('key1')
        assert result is None
    
    def test_no_ttl(self):
        """Test cache without TTL."""
        cache = TimedCache(max_size=10, ttl_seconds=None)
        
        cache.set('key1', 'value1')
        
        time.sleep(0.2)
        
        # Should still be available
        assert cache.get('key1') == 'value1'
    
    def test_clear(self, cache):
        """Test clearing cache."""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        assert len(cache._cache) == 2
        
        cache.clear()
        
        assert len(cache._cache) == 0
        assert cache._stats.hits == 0
        assert cache._stats.misses == 0
    
    def test_get_stats(self, cache):
        """Test getting cache statistics."""
        cache.set('key1', 'value1')
        cache.get('key1')  # Hit
        cache.get('key2')  # Miss
        
        stats = cache.get_stats()
        
        assert stats['entries'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert 'hit_rate' in stats


class TestCacheDecorators:
    """Test cases for cache decorators."""
    
    def test_cached_embedding_decorator(self):
        """Test cached_embedding decorator."""
        from core.evaluator_cache import _embedding_cache
        
        call_count = [0]
        
        @cached_embedding
        def compute_embedding(text: str):
            call_count[0] += 1
            return f"embedding-{text}"
        
        # First call - should compute
        result1 = compute_embedding("test")
        assert result1 == "embedding-test"
        assert call_count[0] == 1
        
        # Second call - should use cache
        result2 = compute_embedding("test")
        assert result2 == "embedding-test"
        assert call_count[0] == 1  # Not incremented
    
    def test_cached_similarity_decorator(self):
        """Test cached_similarity decorator."""
        call_count = [0]
        
        @cached_similarity
        def compute_similarity(text1: str, text2: str):
            call_count[0] += 1
            return f"sim-{text1}-{text2}"
        
        # First call
        result1 = compute_similarity("text1", "text2")
        assert result1 == "sim-text1-text2"
        assert call_count[0] == 1
        
        # Same call - should use cache (order-independent)
        result2 = compute_similarity("text2", "text1")
        assert result2 == "sim-text1-text2"
        assert call_count[0] == 1
        
        # Different call - should compute
        result3 = compute_similarity("text1", "text3")
        assert result3 == "sim-text1-text3"
        assert call_count[0] == 2


class TestGlobalCaches:
    """Test cases for global cache functions."""
    
    def test_get_embedding_cache_singleton(self):
        """Test that embedding cache is singleton."""
        clear_all_caches()
        
        cache1 = get_embedding_cache()
        cache2 = get_embedding_cache()
        
        assert cache1 is cache2
    
    def test_get_similarity_cache_singleton(self):
        """Test that similarity cache is singleton."""
        clear_all_caches()
        
        cache1 = get_similarity_cache()
        cache2 = get_similarity_cache()
        
        assert cache1 is cache2
    
    def test_get_sentiment_cache_singleton(self):
        """Test that sentiment cache is singleton."""
        clear_all_caches()
        
        cache1 = get_sentiment_cache()
        cache2 = get_sentiment_cache()
        
        assert cache1 is cache2
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        emb_cache = get_embedding_cache()
        sim_cache = get_similarity_cache()
        sent_cache = get_sentiment_cache()
        
        # Populate caches
        emb_cache.set('key1', 'value1')
        sim_cache.set('key2', 'value2')
        sent_cache.set('key3', 'value3')
        
        assert len(emb_cache._cache) == 1
        assert len(sim_cache._cache) == 1
        assert len(sent_cache._cache) == 1
        
        # Clear all
        clear_all_caches()
        
        # Get new instances (or clear old ones)
        emb_cache2 = get_embedding_cache()
        sim_cache2 = get_similarity_cache()
        sent_cache2 = get_sentiment_cache()
        
        # All should be empty
        assert len(emb_cache2._cache) == 0
        assert len(sim_cache2._cache) == 0
        assert len(sent_cache2._cache) == 0
    
    def test_get_all_cache_stats(self):
        """Test getting statistics for all caches."""
        clear_all_caches()
        
        emb_cache = get_embedding_cache()
        sim_cache = get_similarity_cache()
        
        # Populate caches
        emb_cache.set('key1', 'value1')
        emb_cache.get('key1')  # Hit
        emb_cache.get('key2')  # Miss
        
        sim_cache.set('key3', 'value3')
        sim_cache.get('key3')  # Hit
        
        stats = get_all_cache_stats()
        
        assert 'embedding' in stats
        assert 'similarity' in stats
        assert stats['embedding']['hits'] == 1
        assert stats['embedding']['misses'] == 1
        assert stats['similarity']['hits'] == 1
        assert stats['similarity']['misses'] == 0
