"""Tests for Manager module."""
import pytest
from unittest.mock import Mock, MagicMock, patch
import hashlib
import sys

# Mock ML modules at import
sys.modules['spacy'] = Mock()
sys.modules['transformers'] = Mock()
sys.modules['sentence_transformers'] = Mock()


class TestManager:
    """Test cases for Manager class."""
    
    @pytest.fixture
    def manager(self, mock_evaluation_processor, mock_note_dao, mock_source_dao, 
                mock_fehner_processor, mock_translator):
        """Create Manager instance with mocked dependencies."""
        from manager import Manager
        
        manager = Manager(
            evaluation_processor=mock_evaluation_processor,
            note_dao=mock_note_dao,
            source_dao=mock_source_dao,
            fehner_processor=mock_fehner_processor,
            translator=mock_translator,
            neo4j_service=None,
        )
        return manager
    
    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.evaluation_processor is not None
        assert manager.note_dao is not None
        assert manager.source_dao is not None
        assert manager.fehner_processor is not None
        assert manager.translator is not None
    
    def test_resolve_text_hash(self, manager):
        """Test text hash generation."""
        text = "test text"
        expected_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        result = manager._resolve_text_hash(text)
        assert result == expected_hash
    
    def test_count_words(self, manager):
        """Test word counting."""
        # Test with content only
        result = manager._count_words("Hello world this is a test")
        assert result == 6
        
        # Test with empty content
        result = manager._count_words("")
        assert result == 0
        
        # Test with title (should not count)
        result = manager._count_words("Hello world", title="Test Title")
        assert result == 2  # Only content is counted
    
    def test_format_processing_time(self, manager):
        """Test processing time formatting."""
        # Milliseconds
        assert manager._format_processing_time(0.5) == "500 ms"
        assert manager._format_processing_time(0.05) == "50 ms"
        
        # Seconds
        assert "seconds" in manager._format_processing_time(1.5)
        assert "seconds" in manager._format_processing_time(30)
        
        # Minutes
        assert "minute" in manager._format_processing_time(60)
        assert "minutes" in manager._format_processing_time(120)
        
        # Hours
        assert "hour" in manager._format_processing_time(3600)
    
    def test_process_already_processed(self, manager, mock_note_dao):
        """Test that already processed text is skipped."""
        from tests.helpers import create_mock_note
        
        # Setup
        existing_note = create_mock_note(id=1)
        mock_note_dao.get_by_hash.return_value = existing_note
        
        # Execute
        result = manager.process("Title", "Content", 1, "english")
        
        # Assert
        assert result is not None
        assert result.id == 1
        mock_note_dao.get_by_hash.assert_called_once()
    
    def test_get_visible_sources(self, manager, mock_source_dao):
        """Test getting visible sources."""
        from tests.helpers import create_mock_source
        
        # Setup
        hidden_source = create_mock_source(id=2, is_hidden=True)
        visible_source = create_mock_source(id=1, is_hidden=False)
        mock_source_dao.get_all.return_value = [visible_source, hidden_source]
        
        # Execute
        result = manager.get_visible_sources()
        
        # Assert
        assert len(result) == 1
        assert result[0].id == 1
    
    def test_get_sources_with_ratings(self, manager, mock_source_dao, mock_note_dao):
        """Test getting sources with ratings."""
        from tests.helpers import create_mock_source, create_mock_note
        
        # Setup
        source = create_mock_source(id=1, is_hidden=False)
        mock_source_dao.get_all.return_value = [source]
        mock_note_dao.get_by_source_id.return_value = [
            create_mock_note(total_score=0.3),
            create_mock_note(total_score=0.5),
        ]
        
        # Execute
        result = manager.get_sources_with_ratings()
        
        # Assert
        assert source in result
        assert result[source] == 0.4  # (0.3 + 0.5) / 2
