"""Tests for EvaluationProcessor module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock all ML modules at import time


class TestEvaluationContext:
    """Test cases for EvaluationContext."""
    
    @pytest.fixture
    def mock_note_dao(self):
        """Mock NoteDao."""
        dao = Mock()
        dao.get_by_source_id = Mock(return_value=[])
        return dao
    
    @pytest.fixture
    def context(self, mock_note_dao):
        """Create EvaluationContext."""
        from processors.evaluation_processor import EvaluationContext
        return EvaluationContext("test content", 1, mock_note_dao)
    
    def test_context_initialization(self, context):
        """Test context initialization."""
        assert context.data == "test content"
        assert context.source_id == 1
        assert context.title is None
        assert context.total_score == 0
        assert context.is_propaganda is False
    
    def test_context_scores_initialized(self, context):
        """Test that all scores are initialized."""
        scores = [
            'sentimental_analysis_result',
            'trigger_keywords_result',
            'trigger_topics_result',
            'text_simplicity_deviation',
            'confidence_factor',
            'clickbait_result',
            'subjective_result',
            'call_to_action_result',
            'repeated_take_result',
            'repeated_note_result',
            'messianism',
            'opposition_to_opponents',
            'generalization_of_opponents',
        ]
        
        for score in scores:
            assert hasattr(context, score)
            # Most should be initialized to 0
            value = getattr(context, score)
            assert isinstance(value, (int, float))


class TestTextSimplicityEvaluator:
    """Test cases for TextSimplicity evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator."""
        from processors.evaluation_processor import TextSimplicity
        return TextSimplicity()
    
    def test_evaluate(self, evaluator):
        """Test text simplicity evaluation."""
        from processors.evaluation_processor import EvaluationContext
        from tests.helpers import create_mock_evaluation_context
        
        context = create_mock_evaluation_context(
            data="This is a simple test sentence.",
            source_id=1,
        )
        
        evaluator.evaluate(context)
        
        assert context.text_simplicity_deviation is not None
        assert context.text_simplicity_deviation_execution_time >= 0


class TestSubjectiveEvaluator:
    """Test cases for Subjective evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator."""
        from processors.evaluation_processor import Subjective
        return Subjective()
    
    @patch('processors.evaluation_processor.TextBlob')
    def test_evaluate(self, mock_blob_class, evaluator):
        """Test subjective evaluation."""
        # Setup mock
        mock_blob = Mock()
        mock_blob.sentiment.subjectivity = 0.6
        mock_blob_class.return_value = mock_blob
        
        from tests.helpers import create_mock_evaluation_context
        context = create_mock_evaluation_context(
            data="I think this is amazing!",
            source_id=1,
        )
        
        # Execute
        evaluator.evaluate(context)
        
        # Assert
        assert context.subjective_result == 0.6
        assert context.subjective_execution_time >= 0


class TestTriggerKeywordsEvaluator:
    """Test cases for TriggerKeywords evaluator."""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator."""
        from processors.evaluation_processor import TriggerKeywords
        return TriggerKeywords()
    
    @patch('processors.evaluation_processor.open')
    def test_evaluate(self, mock_open, evaluator):
        """Test trigger keywords evaluation."""
        # Setup mock for file reading
        import json
        mock_file = Mock()
        mock_file.read.return_value = json.dumps({
            "language": {
                "english": ["threat", "destroy", "enemy"]
            }
        })
        mock_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_open.return_value.__exit__ = Mock(return_value=False)
        
        from tests.helpers import create_mock_evaluation_context
        context = create_mock_evaluation_context(
            data="The enemy will destroy us! The enemy is a threat!",
            source_id=1,
        )
        
        # Execute
        evaluator.evaluate(context)
        
        # Assert - should detect keywords
        assert context.trigger_keywords_result in [0, 1]
        assert context.trigger_keywords_execution_time >= 0


class TestEvaluationProcessor:
    """Test cases for EvaluationProcessor."""
    
    @pytest.fixture
    def processor(self, mock_note_dao):
        """Create EvaluationProcessor."""
        from processors.evaluation_processor import EvaluationProcessor
        return EvaluationProcessor(mock_note_dao)
    
    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor.note_dao is not None
        assert len(processor.evaluations) > 0
    
    def test_evaluate_creates_context(self, processor):
        """Test that evaluate creates and returns context."""
        # Execute
        context = processor.evaluate("Test Title", "Test content", 1)
        
        # Assert
        assert context.data == "Test content"
        assert context.source_id == 1
        assert context.title == "Test Title"
    
    def test_evaluate_runs_all_evaluators(self, processor):
        """Test that evaluate runs all evaluators."""
        # Mock all evaluators
        for evaluator in processor.evaluations:
            evaluator.evaluate = Mock()
        
        # Execute
        context = processor.evaluate("Title", "Content", 1)
        
        # Assert - all evaluators were called
        for evaluator in processor.evaluations:
            evaluator.evaluate.assert_called_once()
    
    def test_calculate_total_score(self, processor):
        """Test total score calculation."""
        context = processor.evaluate("Title", "Content", 1)
        
        assert context.total_score >= 0
        assert isinstance(context.total_score, (int, float))
