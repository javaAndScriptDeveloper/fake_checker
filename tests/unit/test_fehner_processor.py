"""Tests for FehnerProcessor module."""
import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys

# Mock ML modules at import
sys.modules['sklearn'] = Mock()
sys.modules['sklearn.feature_extraction'] = Mock()
sys.modules['sklearn.feature_extraction.text'] = Mock()


class TestFehnerProcessor:
    """Test cases for FehnerProcessor class."""
    
    @pytest.fixture
    def processor(self, mock_note_dao):
        """Create FehnerProcessor instance."""
        from processors.fehner_processor import FehnerProcessor
        return FehnerProcessor(mock_note_dao)
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor.note_dao is not None
    
    @patch('processors.fehner_processor.TfidfVectorizer')
    @patch('processors.fehner_processor.cosine_similarity')
    def test_calculate_similarity_score(self, mock_cos_sim, mock_vectorizer, processor):
        """Test similarity score calculation."""
        # Setup mocks
        mock_vectorizer.return_value = Mock(
            fit_transform=Mock(return_value=Mock())
        )
        mock_cos_sim.return_value = np.array([[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]])
        
        # Simple text with repeated phrases
        text = "This is a test. This is another test. The test is good."
        
        score = processor.calculate_similarity_score(text)
        
        assert 0 <= score <= 1
        assert isinstance(score, (float, np.floating))
    
    @patch('processors.fehner_processor.TfidfVectorizer')
    @patch('processors.fehner_processor.cosine_similarity')
    def test_calculate_similarity_score_single_sentence(self, mock_cos_sim, mock_vectorizer, processor):
        """Test similarity score with single sentence."""
        # Setup mocks
        mock_vectorizer.return_value = Mock(
            fit_transform=Mock(return_value=Mock())
        )
        mock_cos_sim.return_value = np.array([[1.0]])
        
        text = "This is a single sentence."
        
        score = processor.calculate_similarity_score(text)
        
        assert score == 0.0  # No similarity to compare
    
    @patch('processors.fehner_processor.TfidfVectorizer')
    @patch('processors.fehner_processor.cosine_similarity')
    def test_calculate_similarity_score_empty(self, mock_cos_sim, mock_vectorizer, processor):
        """Test similarity score with empty text."""
        # Setup mocks
        mock_vectorizer.return_value = Mock(
            fit_transform=Mock(return_value=Mock(shape=(0, 5000)))
        )
        mock_cos_sim.return_value = np.array([[]])
        
        text = ""
        
        score = processor.calculate_similarity_score(text)
        
        assert score == 0.0
    
    def test_calculate_fehner_score(self, processor, mock_note_dao):
        """Test overall Fehner score calculation."""
        from tests.helpers import create_mock_note
        
        # Setup
        notes = [
            create_mock_note(id=1, fehner_type='A'),
            create_mock_note(id=2, fehner_type='A'),
            create_mock_note(id=3, fehner_type='B'),
        ]
        mock_note_dao.get_notes.return_value = notes
        
        # Execute
        score = processor.calculate_fehner_score()
        
        # Assert - 2 out of 3 are type A
        assert score == 2/3
    
    def test_calculate_fehner_score_empty(self, processor, mock_note_dao):
        """Test Fehner score with no notes."""
        mock_note_dao.get_notes.return_value = []
        
        score = processor.calculate_fehner_score()
        
        assert score == 0