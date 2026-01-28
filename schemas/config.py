"""Pydantic schemas for configuration validation."""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DatabaseConfigSchema(BaseModel):
    """Schema for PostgreSQL database configuration."""

    host: str = Field(default="localhost", min_length=1)
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = Field(default="fake_checker", min_length=1)
    user: str = Field(default="postgres", min_length=1)
    password: str = Field(default="", min_length=0)

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = {"extra": "forbid"}


class Neo4jConfigSchema(BaseModel):
    """Schema for Neo4j database configuration."""

    uri: str = Field(default="bolt://localhost:7687", min_length=1)
    user: str = Field(default="neo4j", min_length=1)
    password: str = Field(default="", min_length=0)
    database: str = Field(default="neo4j", min_length=1)

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        if not v.startswith(("bolt://", "neo4j://", "neo4j+s://", "bolt+s://")):
            raise ValueError("URI must start with bolt://, neo4j://, neo4j+s://, or bolt+s://")
        return v

    model_config = {"extra": "forbid"}


class AppConfigSchema(BaseModel):
    """Schema for application configuration."""

    # Similarity threshold for text comparison
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)

    # Average news simplicity baseline
    average_news_simplicity: float = Field(default=50.0, ge=0.0, le=100.0)

    # OpenAI configuration
    openai_api_key: Optional[str] = Field(default=None)
    is_chatgpt_processor_enabled: bool = Field(default=False)

    # Logging
    log_level: str = Field(default="INFO")

    # Propaganda threshold
    propaganda_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    model_config = {"extra": "forbid"}


class FullConfigSchema(BaseModel):
    """Complete configuration schema combining all config sections."""

    database: DatabaseConfigSchema = Field(default_factory=DatabaseConfigSchema)
    neo4j: Neo4jConfigSchema = Field(default_factory=Neo4jConfigSchema)
    app: AppConfigSchema = Field(default_factory=AppConfigSchema)

    model_config = {"extra": "forbid"}
