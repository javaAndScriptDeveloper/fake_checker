"""Tests for DAL (Data Access Layer) module."""
import pytest


class TestNote:
    """Test cases for Note model."""
    
    def test_note_initialization(self):
        """Test Note object initialization."""
        from dal.dal import Note
        note = Note(
            content="Test content",
            source_id=1,
        )
        assert note.content == "Test content"
        assert note.source_id == 1
        # Note: SQLAlchemy defaults are database-level, not Python-level
        # These will be set when saved to database
        assert note.total_score is None
        assert note.confidence_factor is None


class TestSource:
    """Test cases for Source model."""
    
    def test_source_initialization(self):
        """Test Source object initialization."""
        from dal.dal import Source
        source = Source(
            external_id="123",
            platform="telegram",
            name="Test Source",
        )
        assert source.external_id == "123"
        assert source.platform == "telegram"
        assert source.name == "Test Source"
        assert source.rating is None
        assert source.is_hidden is None
