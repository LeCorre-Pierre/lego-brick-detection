"""
Unit tests for ImageCache.
"""

import pytest
from pathlib import Path
from PyQt6.QtGui import QPixmap
from src.utils.image_cache import ImageCache


class TestImageCache:
    """Test image caching functionality."""
    
    @pytest.fixture
    def temp_image_dir(self, tmp_path):
        """Create temporary directory for test images."""
        image_dir = tmp_path / "brick_images"
        image_dir.mkdir()
        return image_dir
    
    @pytest.fixture
    def cache(self, temp_image_dir):
        """Create ImageCache instance for testing."""
        return ImageCache(temp_image_dir, max_size=10, image_size=(48, 48))
    
    def test_cache_initialization(self, cache, temp_image_dir):
        """Test cache initializes correctly."""
        assert cache._image_dir == temp_image_dir
        assert cache._max_size == 10
        assert cache._image_size == (48, 48)
        assert len(cache._cache) == 0
    
    def test_get_image_returns_placeholder_for_missing_image(self, cache):
        """Test placeholder is returned when image file doesn't exist."""
        pixmap = cache.get_image("3005")
        
        assert not pixmap.isNull()
        assert pixmap.width() == 48
        assert pixmap.height() == 48
        assert len(cache._cache) == 1
    
    def test_placeholder_generation_is_consistent(self, cache):
        """Test that same part number generates same placeholder."""
        pixmap1 = cache.get_image("3005")
        cache.clear_cache()
        pixmap2 = cache.get_image("3005")
        
        # Placeholders should have same dimensions
        assert pixmap1.width() == pixmap2.width()
        assert pixmap1.height() == pixmap2.height()
    
    def test_different_part_numbers_generate_different_placeholders(self, cache):
        """Test different part numbers generate visually distinct placeholders."""
        pixmap1 = cache.get_image("3005")
        pixmap2 = cache.get_image("3001")
        
        # Both should be valid
        assert not pixmap1.isNull()
        assert not pixmap2.isNull()
        
        # They should be cached separately
        assert len(cache._cache) == 2
    
    def test_cache_lru_eviction(self, cache):
        """Test LRU eviction when cache exceeds max size."""
        # Fill cache beyond max size
        for i in range(12):
            cache.get_image(f"part_{i}")
        
        # Cache should not exceed max size
        assert len(cache._cache) <= 10
        
        # Oldest items should be evicted
        assert "part_0" not in cache._cache
        assert "part_1" not in cache._cache
    
    def test_cache_hit_moves_to_end(self, cache):
        """Test that accessing cached item moves it to end (LRU)."""
        # Add items
        cache.get_image("part_1")
        cache.get_image("part_2")
        cache.get_image("part_3")
        
        # Access first item again
        cache.get_image("part_1")
        
        # part_1 should now be at the end (most recently used)
        assert list(cache._cache.keys())[-1] == "part_1"
    
    def test_preload_images(self, cache):
        """Test preloading multiple images."""
        part_numbers = ["3005", "3001", "3004"]
        
        cache.preload_images(part_numbers)
        
        assert len(cache._cache) == 3
        for part_number in part_numbers:
            assert part_number in cache._cache
    
    def test_clear_cache(self, cache):
        """Test clearing the cache."""
        cache.get_image("3005")
        cache.get_image("3001")
        
        cache.clear_cache()
        
        assert len(cache._cache) == 0
        assert len(cache._placeholder_cache) == 0
    
    def test_get_cache_size(self, cache):
        """Test getting cache size."""
        assert cache.get_cache_size() == 0
        
        cache.get_image("3005")
        assert cache.get_cache_size() == 1
        
        cache.get_image("3001")
        assert cache.get_cache_size() == 2
    
    def test_placeholder_cache_separate_from_main_cache(self, cache):
        """Test that placeholder cache doesn't count toward main cache size."""
        # Generate placeholders
        cache.get_image("3005")
        cache.get_image("3001")
        
        # Both should be in cache
        assert cache.get_cache_size() == 2
        # Placeholders are also cached but in separate dict
        assert len(cache._placeholder_cache) == 2
