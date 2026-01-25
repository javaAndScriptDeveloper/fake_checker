"""Dependency Injection Container for the application.

This module provides a centralized way to manage dependencies,
allowing for easier testing and configuration management.
"""
from typing import Optional, TypeVar, Type, Callable, Dict, Any
from dataclasses import dataclass
import os
from pathlib import Path

T = TypeVar('T')


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "fake_checker"
    user: str = "postgres"
    password: str = "password"
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            name=os.getenv('DB_NAME', 'fake_checker'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
        )
    
    @property
    def connection_string(self) -> str:
        """Get SQLAlchemy connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class Neo4jConfig:
    """Neo4j configuration."""
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "your_strong_password"
    database: str = "neo4j"
    
    @classmethod
    def from_env(cls) -> 'Neo4jConfig':
        """Load configuration from environment variables."""
        return cls(
            uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            user=os.getenv('NEO4J_USER', 'neo4j'),
            password=os.getenv('NEO4J_PASSWORD', 'your_strong_password'),
            database=os.getenv('NEO4J_DATABASE', 'neo4j'),
        )


@dataclass
class AppConfig:
    """Application configuration."""
    similarity_threshold: float = 0.85
    average_news_simplicity: float = 50.0
    openai_api_key: Optional[str] = None
    is_chatgpt_processor_enabled: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration."""
        if not 0 <= self.similarity_threshold <= 1:
            raise ConfigurationError(
                f"similarity_threshold must be between 0 and 1, got {self.similarity_threshold}"
            )
        if not 0 <= self.average_news_simplicity <= 100:
            raise ConfigurationError(
                f"average_news_simplicity must be between 0 and 100, got {self.average_news_simplicity}"
            )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """Load configuration from dictionary (e.g., YAML file)."""
        return cls(
            similarity_threshold=config_dict.get('similarity_threshold', 0.85),
            average_news_simplicity=config_dict.get('average_news_simplicity', 50.0),
            openai_api_key=config_dict.get('openai_api_key'),
            is_chatgpt_processor_enabled=config_dict.get('is_chatgpt_processor_enabled', False),
        )


class ServiceContainer:
    """Dependency injection container for application services.
    
    This container manages the lifecycle of all services and provides
    lazy initialization to avoid loading heavy resources (ML models, DB connections)
    until they're actually needed.
    """
    
    def __init__(self):
        """Initialize empty container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, bool] = {}
        
        # Configuration
        self._db_config: Optional[DatabaseConfig] = None
        self._neo4j_config: Optional[Neo4jConfig] = None
        self._app_config: Optional[AppConfig] = None
    
    def configure_database(self, config: DatabaseConfig) -> 'ServiceContainer':
        """Configure database settings."""
        self._db_config = config
        return self
    
    def configure_neo4j(self, config: Neo4jConfig) -> 'ServiceContainer':
        """Configure Neo4j settings."""
        self._neo4j_config = config
        return self
    
    def configure_app(self, config: AppConfig) -> 'ServiceContainer':
        """Configure application settings."""
        self._app_config = config
        return self
    
    def register_factory(self, name: str, factory: Callable[[], T], singleton: bool = True) -> 'ServiceContainer':
        """Register a factory function for creating services.
        
        Args:
            name: Service name
            factory: Factory function that creates the service
            singleton: Whether to cache the created service (default: True)
        """
        self._factories[name] = factory
        self._singletons[name] = singleton
        return self
    
    def register_instance(self, name: str, instance: T) -> 'ServiceContainer':
        """Register an existing service instance.
        
        Args:
            name: Service name
            instance: Service instance
        """
        self._services[name] = instance
        return self
    
    def get(self, name: str) -> Optional[T]:
        """Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        # Return cached instance if available
        if name in self._services:
            return self._services[name]
        
        # Create from factory if available
        if name in self._factories:
            instance = self._factories[name]()
            
            # Cache if singleton
            if self._singletons.get(name, True):
                self._services[name] = instance
            
            return instance
        
        return None
    
    def get_or_raise(self, name: str) -> T:
        """Get a service by name, raise if not found.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not found
        """
        instance = self.get(name)
        if instance is None:
            raise KeyError(f"Service '{name}' not registered in container")
        return instance
    
    @property
    def db_config(self) -> DatabaseConfig:
        """Get database configuration."""
        if self._db_config is None:
            self._db_config = DatabaseConfig.from_env()
        return self._db_config
    
    @property
    def neo4j_config(self) -> Neo4jConfig:
        """Get Neo4j configuration."""
        if self._neo4j_config is None:
            self._neo4j_config = Neo4jConfig.from_env()
        return self._neo4j_config
    
    @property
    def app_config(self) -> AppConfig:
        """Get application configuration."""
        if self._app_config is None:
            # Try to load from YAML
            from config.config import config as config_dict
            self._app_config = AppConfig.from_dict(config_dict)
        return self._app_config
    
    def clear_cache(self) -> None:
        """Clear all cached service instances.
        
        This is useful for testing or re-initialization.
        """
        self._services.clear()


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get or create the global service container.
    
    Returns:
        Global ServiceContainer instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset the global container.
    
    This is useful for testing.
    """
    global _container
    _container = None
