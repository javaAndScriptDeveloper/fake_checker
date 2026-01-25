"""Tests for Dependency Injection module."""
import pytest
from unittest.mock import Mock, patch
import os

from core.dependency_injection import (
    ServiceContainer,
    DatabaseConfig,
    Neo4jConfig,
    AppConfig,
    ConfigurationError,
    get_container,
    reset_container,
)


class TestDatabaseConfig:
    """Test cases for DatabaseConfig."""
    
    def test_default_initialization(self):
        """Test default database configuration."""
        config = DatabaseConfig()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.name == "fake_checker"
        assert config.user == "postgres"
        assert config.password == "password"
    
    def test_custom_initialization(self):
        """Test custom database configuration."""
        config = DatabaseConfig(
            host="custom-host",
            port=5433,
            name="custom_db",
            user="custom_user",
            password="custom_pass"
        )
        
        assert config.host == "custom-host"
        assert config.port == 5433
        assert config.name == "custom_db"
        assert config.user == "custom_user"
        assert config.password == "custom_pass"
    
    def test_from_env(self):
        """Test loading configuration from environment variables."""
        with patch.dict(os.environ, {
            'DB_HOST': 'env-host',
            'DB_PORT': '5434',
            'DB_NAME': 'env_db',
            'DB_USER': 'env_user',
            'DB_PASSWORD': 'env_pass'
        }):
            config = DatabaseConfig.from_env()
            
            assert config.host == 'env-host'
            assert config.port == 5434
            assert config.name == 'env_db'
            assert config.user == 'env_user'
            assert config.password == 'env_pass'
    
    def test_connection_string(self):
        """Test generating connection string."""
        config = DatabaseConfig(
            user="testuser",
            password="testpass",
            host="testhost",
            port=5432,
            name="testdb"
        )
        
        expected = "postgresql://testuser:testpass@testhost:5432/testdb"
        assert config.connection_string == expected


class TestNeo4jConfig:
    """Test cases for Neo4jConfig."""
    
    def test_default_initialization(self):
        """Test default Neo4j configuration."""
        config = Neo4jConfig()
        
        assert config.uri == "bolt://localhost:7687"
        assert config.user == "neo4j"
        assert config.password == "your_strong_password"
        assert config.database == "neo4j"
    
    def test_custom_initialization(self):
        """Test custom Neo4j configuration."""
        config = Neo4jConfig(
            uri="bolt://custom:7687",
            user="custom_user",
            password="custom_pass",
            database="custom_db"
        )
        
        assert config.uri == "bolt://custom:7687"
        assert config.user == "custom_user"
        assert config.password == "custom_pass"
        assert config.database == "custom_db"
    
    def test_from_env(self):
        """Test loading Neo4j config from environment."""
        with patch.dict(os.environ, {
            'NEO4J_URI': 'bolt://env-host:7687',
            'NEO4J_USER': 'env_user',
            'NEO4J_PASSWORD': 'env_pass',
            'NEO4J_DATABASE': 'env_db'
        }):
            config = Neo4jConfig.from_env()
            
            assert config.uri == 'bolt://env-host:7687'
            assert config.user == 'env_user'
            assert config.password == 'env_pass'
            assert config.database == 'env_db'


class TestAppConfig:
    """Test cases for AppConfig."""
    
    def test_default_initialization(self):
        """Test default application configuration."""
        config = AppConfig()
        
        assert config.similarity_threshold == 0.85
        assert config.average_news_simplicity == 50.0
        assert config.openai_api_key is None
        assert config.is_chatgpt_processor_enabled is False
        assert config.log_level == "INFO"
    
    def test_custom_initialization(self):
        """Test custom application configuration."""
        config = AppConfig(
            similarity_threshold=0.9,
            average_news_simplicity=75.0,
            openai_api_key="test-key",
            is_chatgpt_processor_enabled=True,
            log_level="DEBUG"
        )
        
        assert config.similarity_threshold == 0.9
        assert config.average_news_simplicity == 75.0
        assert config.openai_api_key == "test-key"
        assert config.is_chatgpt_processor_enabled is True
        assert config.log_level == "DEBUG"
    
    def test_from_dict(self):
        """Test loading configuration from dictionary."""
        config_dict = {
            'similarity_threshold': 0.95,
            'average_news_simplicity': 80.0,
            'openai_api_key': 'dict-key',
            'is_chatgpt_processor_enabled': True
        }
        
        config = AppConfig.from_dict(config_dict)
        
        assert config.similarity_threshold == 0.95
        assert config.average_news_simplicity == 80.0
        assert config.openai_api_key == 'dict-key'
        assert config.is_chatgpt_processor_enabled is True
        # Note: log_level not in from_dict, so stays default
        assert config.log_level == 'INFO'
    
    def test_invalid_similarity_threshold_low(self):
        """Test validation of low similarity threshold."""
        with pytest.raises(ConfigurationError) as exc_info:
            AppConfig(similarity_threshold=-0.1)
        
        assert "similarity_threshold" in str(exc_info.value)
    
    def test_invalid_similarity_threshold_high(self):
        """Test validation of high similarity threshold."""
        with pytest.raises(ConfigurationError) as exc_info:
            AppConfig(similarity_threshold=1.5)
        
        assert "similarity_threshold" in str(exc_info.value)
    
    def test_invalid_simplicity_low(self):
        """Test validation of low simplicity value."""
        with pytest.raises(ConfigurationError) as exc_info:
            AppConfig(average_news_simplicity=-10.0)
        
        assert "average_news_simplicity" in str(exc_info.value)
    
    def test_invalid_simplicity_high(self):
        """Test validation of high simplicity value."""
        with pytest.raises(ConfigurationError) as exc_info:
            AppConfig(average_news_simplicity=150.0)
        
        assert "average_news_simplicity" in str(exc_info.value)


class TestServiceContainer:
    """Test cases for ServiceContainer."""
    
    def test_initialization(self):
        """Test container initialization."""
        container = ServiceContainer()
        
        assert container._services == {}
        assert container._factories == {}
        assert container._singletons == {}
    
    def test_register_factory(self):
        """Test registering a factory function."""
        container = ServiceContainer()
        
        def create_service():
            return "service-instance"
        
        container.register_factory('test_service', create_service)
        
        assert 'test_service' in container._factories
        assert container._singletons['test_service'] is True
    
    def test_get_from_factory(self):
        """Test getting service from factory."""
        container = ServiceContainer()
        
        def create_service():
            return "service-instance"
        
        container.register_factory('test_service', create_service)
        service = container.get('test_service')
        
        assert service == "service-instance"
        assert 'test_service' in container._services  # Cached
    
    def test_singleton_caching(self):
        """Test that singleton services are cached."""
        container = ServiceContainer()
        call_count = [0]
        
        def create_service():
            call_count[0] += 1
            return f"service-{call_count[0]}"
        
        container.register_factory('test_service', create_service, singleton=True)
        
        # Get multiple times
        service1 = container.get('test_service')
        service2 = container.get('test_service')
        
        assert service1 == service2
        assert call_count[0] == 1  # Factory only called once
    
    def test_non_singleton_no_caching(self):
        """Test that non-singleton services are not cached."""
        container = ServiceContainer()
        call_count = [0]
        
        def create_service():
            call_count[0] += 1
            return f"service-{call_count[0]}"
        
        container.register_factory('test_service', create_service, singleton=False)
        
        # Get multiple times
        service1 = container.get('test_service')
        service2 = container.get('test_service')
        
        assert service1 != service2
        assert call_count[0] == 2  # Factory called each time
    
    def test_register_instance(self):
        """Test registering an existing instance."""
        container = ServiceContainer()
        instance = "existing-instance"
        
        container.register_instance('test_service', instance)
        service = container.get('test_service')
        
        assert service == instance
    
    def test_get_nonexistent(self):
        """Test getting non-existent service."""
        container = ServiceContainer()
        service = container.get('nonexistent')
        
        assert service is None
    
    def test_get_or_raise(self):
        """Test get_or_raise with existing service."""
        container = ServiceContainer()
        
        def create_service():
            return "service-instance"
        
        container.register_factory('test_service', create_service)
        service = container.get_or_raise('test_service')
        
        assert service == "service-instance"
    
    def test_get_or_raise_nonexistent(self):
        """Test get_or_raise with non-existent service."""
        container = ServiceContainer()
        
        with pytest.raises(KeyError) as exc_info:
            container.get_or_raise('nonexistent')
        
        assert "nonexistent" in str(exc_info.value)
    
    def test_clear_cache(self):
        """Test clearing service cache."""
        container = ServiceContainer()
        
        def create_service():
            return "service-instance"
        
        container.register_factory('test_service', create_service)
        container.get('test_service')  # Populate cache
        
        assert 'test_service' in container._services
        
        container.clear_cache()
        
        assert 'test_service' not in container._services


class TestGlobalContainer:
    """Test cases for global container functions."""
    
    def test_get_container(self):
        """Test getting global container."""
        from core.dependency_injection import reset_container
        
        reset_container()
        container1 = get_container()
        container2 = get_container()
        
        # Should return same instance
        assert container1 is container2
    
    def test_reset_container(self):
        """Test resetting global container."""
        from core.dependency_injection import reset_container, _container
        
        container1 = get_container()
        reset_container()
        container2 = get_container()
        
        # Should return different instances after reset
        assert container1 is not container2
