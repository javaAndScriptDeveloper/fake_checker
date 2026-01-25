"""Tests for utility modules."""
import pytest
import logging
from pathlib import Path
from utils.logger import get_logger, LOG_DIR


class TestLogger:
    """Test cases for logger utility."""
    
    def test_log_dir_exists(self):
        """Test that log directory exists."""
        assert LOG_DIR.exists()
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_module")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_get_logger_same_instance(self):
        """Test that getting same logger name returns same instance."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """Test that different names create different loggers."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"
    
    def test_logger_has_handlers(self):
        """Test that logger has configured handlers."""
        # The root logger has handlers
        import logging
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0
    
    def test_log_file_writable(self):
        """Test that log file can be written to."""
        logger = get_logger("test_writable")
        
        # This should not raise an exception
        logger.info("Test log message")
        
        # Check that log file exists and has content
        log_file = LOG_DIR / 'app.log'
        assert log_file.exists()
