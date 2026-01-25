"""Tests for Configuration module."""
import pytest
from pathlib import Path
import yaml


class TestConfigModule:
    """Test cases for configuration."""
    
    def test_config_yaml_exists(self):
        """Test that config.yaml exists."""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        assert config_path.exists()
    
    def test_config_yaml_loadable(self):
        """Test that config.yaml can be loaded."""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
        assert "similarity_threshold" in config
        assert "average_news_simplicity" in config
    
    def test_config_yaml_values(self):
        """Test config values are reasonable."""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert isinstance(config["similarity_threshold"], (int, float))
        assert 0 <= config["similarity_threshold"] <= 1
        assert isinstance(config["average_news_simplicity"], (int, float))
    
    def test_config_trigger_keywords_exists(self):
        """Test that trigger_keywords.json exists."""
        config_path = Path(__file__).parent.parent.parent / "config" / "trigger_keywords.json"
        assert config_path.exists()
    
    def test_config_trigger_topics_exists(self):
        """Test that trigger_topics.json exists."""
        config_path = Path(__file__).parent.parent.parent / "config" / "trigger_topics.json"
        assert config_path.exists()
