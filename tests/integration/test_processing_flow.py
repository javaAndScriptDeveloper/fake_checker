"""Integration tests for processing flow."""
import pytest
from unittest.mock import Mock, patch
import sys

# Mock ML modules at import
sys.modules['spacy'] = Mock()
sys.modules['transformers'] = Mock()
sys.modules['sentence_transformers'] = Mock()


class TestProcessingFlowIntegration:
    """Integration tests for complete processing flow."""
    
    @pytest.fixture
    def mock_evaluation_processor(self):
        """Mock EvaluationProcessor."""
        from tests.helpers import create_mock_evaluation_context
        
        processor = Mock()
        
        context = create_mock_evaluation_context(
            data="This is test content for analysis",
            source_id=1,
            total_score=0.4,
            is_propaganda=False,
            sentimental_analysis_result=0.5,
        )
        
        processor.evaluate = Mock(return_value=context)
        return processor
    
    @pytest.fixture
    def mock_fehner_processor(self):
        """Mock FehnerProcessor."""
        processor = Mock()
        processor.process = Mock()
        processor.calculate_fehner_score = Mock(return_value=0.5)
        return processor
    
    @pytest.fixture
    def mock_translator(self):
        """Mock Translator."""
        translator = Mock()
        translator.translate_to_english = Mock(side_effect=lambda x, y: x)
        translator.supported_translations_list = [
            {"label": "English", "value": "english"}
        ]
        return translator
    
    @pytest.fixture
    def integration_manager(self, mock_evaluation_processor, mock_fehner_processor, 
                             mock_translator, mock_note_dao, mock_source_dao):
        """Create Manager for integration testing."""
        from manager import Manager
        return Manager(
            evaluation_processor=mock_evaluation_processor,
            note_dao=mock_note_dao,
            source_dao=mock_source_dao,
            fehner_processor=mock_fehner_processor,
            translator=mock_translator,
            neo4j_service=None,
        )
    
    def test_full_processing_flow(self, integration_manager, mock_note_dao):
        """Test complete processing flow from input to result."""
        from tests.helpers import create_mock_note
        
        # Setup
        mock_note_dao.get_by_hash.return_value = None
        mock_note_dao.save = Mock(return_value=create_mock_note(id=1))
        
        # Execute
        result = integration_manager.process(
            title="Test Title",
            text="This is test content for analysis",
            source_id=1,
            language="english"
        )
        
        # Assert
        assert result is not None
        assert result.content == "This is test content for analysis"
        assert result.source_id == 1
        
        # Verify processing was called
        integration_manager.evaluation_processor.evaluate.assert_called_once()
        integration_manager.fehner_processor.process.assert_called_once()
    
    def test_processing_duplicate_skipped(self, integration_manager, mock_note_dao):
        """Test that duplicate content is skipped."""
        from tests.helpers import create_mock_note
        
        # Setup
        existing_note = create_mock_note(id=1, content="existing", source_id=1)
        mock_note_dao.get_by_hash.return_value = existing_note
        
        # Execute
        result = integration_manager.process(
            title="Test",
            text="existing",
            source_id=1,
            language="english"
        )
        
        # Assert
        assert result.id == 1
        assert result.content == "existing"
        
        # Evaluation should not be called for duplicates
        integration_manager.evaluation_processor.evaluate.assert_not_called()