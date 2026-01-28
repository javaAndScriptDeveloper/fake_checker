"""Custom exceptions for the Propaganda Checker application.

This module defines a hierarchy of exceptions for different error scenarios,
enabling precise error handling and informative error messages throughout
the application.
"""
from typing import Optional, Any


class PropagandaCheckerError(Exception):
    """Base exception for all Propaganda Checker errors.

    All custom exceptions in the application should inherit from this class
    to enable catching all application-specific errors with a single except clause.
    """

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(PropagandaCheckerError):
    """Raised when there is a configuration-related error.

    Examples:
        - Missing required configuration file
        - Invalid configuration values
        - Environment variables not set
    """

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details=details)
        self.config_key = config_key


class EvaluationError(PropagandaCheckerError):
    """Raised when an evaluation process fails.

    Examples:
        - ML model inference failure
        - Invalid input data format
        - Evaluator initialization failure
    """

    def __init__(
        self,
        message: str,
        evaluator_name: Optional[str] = None,
        input_data: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if evaluator_name:
            details["evaluator"] = evaluator_name
        if input_data:
            # Truncate for logging
            details["input_preview"] = input_data[:100] + "..." if len(input_data) > 100 else input_data
        super().__init__(message, details=details)
        self.evaluator_name = evaluator_name


class DatabaseError(PropagandaCheckerError):
    """Raised when a database operation fails.

    Examples:
        - Connection failure
        - Query execution error
        - Transaction rollback
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        db_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if db_type:
            details["database"] = db_type
        super().__init__(message, details=details)
        self.operation = operation
        self.db_type = db_type


class PostgresError(DatabaseError):
    """Raised when a PostgreSQL-specific error occurs."""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(message, operation=operation, db_type="postgresql", **kwargs)


class Neo4jError(DatabaseError):
    """Raised when a Neo4j-specific error occurs."""

    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(message, operation=operation, db_type="neo4j", **kwargs)


class ModelError(PropagandaCheckerError):
    """Raised when there is an ML model-related error.

    Examples:
        - Model file not found
        - Model loading failure
        - Incompatible model version
        - Inference failure
    """

    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if model_name:
            details["model"] = model_name
        if model_path:
            details["path"] = str(model_path)
        super().__init__(message, details=details)
        self.model_name = model_name
        self.model_path = model_path


class TranslationError(PropagandaCheckerError):
    """Raised when text translation fails.

    Examples:
        - Unsupported language
        - Translation API failure
        - Rate limiting
    """

    def __init__(
        self,
        message: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if source_lang:
            details["source_language"] = source_lang
        if target_lang:
            details["target_language"] = target_lang
        super().__init__(message, details=details)
        self.source_lang = source_lang
        self.target_lang = target_lang


class ValidationError(PropagandaCheckerError):
    """Raised when input validation fails.

    Examples:
        - Invalid note content
        - Missing required fields
        - Data type mismatch
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs,
    ):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)[:50]  # Truncate for logging
        super().__init__(message, details=details)
        self.field = field
        self.value = value
