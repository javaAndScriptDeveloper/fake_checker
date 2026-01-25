"""Test helper utilities for mocking and common operations."""
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from datetime import datetime


def create_mock_note(
    id: int = 1,
    content: str = "Test content",
    source_id: int = 1,
    total_score: float = 0.5,
    is_propaganda: bool = False,
    hash: str = "test_hash",
    **kwargs
):
    """Create a comprehensive mock Note object."""
    note = Mock()
    note.id = id
    note.content = content
    note.source_id = source_id
    note.total_score = total_score
    note.is_propaganda = is_propaganda
    note.hash = hash
    note.sentimental_score = kwargs.get('sentimental_score', 0.5)
    note.sentimental_score_raw = kwargs.get('sentimental_score_raw', 0.5)
    note.sentimental_score_coeff = kwargs.get('sentimental_score_coeff', 0.0)
    note.triggered_keywords = kwargs.get('triggered_keywords', 0.0)
    note.triggered_keywords_raw = kwargs.get('triggered_keywords_raw', 0.0)
    note.triggered_keywords_coeff = kwargs.get('triggered_keywords_coeff', 0.0)
    note.triggered_topics = kwargs.get('triggered_topics', 0.0)
    note.triggered_topics_raw = kwargs.get('triggered_topics_raw', 0.0)
    note.triggered_topics_coeff = kwargs.get('triggered_topics_coeff', 0.0)
    note.text_simplicity_deviation = kwargs.get('text_simplicity_deviation', 0.5)
    note.text_simplicity_deviation_raw = kwargs.get('text_simplicity_deviation_raw', 0.5)
    note.text_simplicity_deviation_coeff = kwargs.get('text_simplicity_deviation_coeff', 0.0)
    note.confidence_factor = kwargs.get('confidence_factor', 50.0)
    note.confidence_factor_raw = kwargs.get('confidence_factor_raw', 0.5)
    note.confidence_factor_coeff = kwargs.get('confidence_factor_coeff', 0.0)
    note.clickbait = kwargs.get('clickbait', 0.0)
    note.clickbait_raw = kwargs.get('clickbait_raw', 0.0)
    note.clickbait_coeff = kwargs.get('clickbait_coeff', 0.0)
    note.subjective = kwargs.get('subjective', 0.5)
    note.subjective_raw = kwargs.get('subjective_raw', 0.5)
    note.subjective_coeff = kwargs.get('subjective_coeff', 0.0)
    note.call_to_action = kwargs.get('call_to_action', 0.0)
    note.call_to_action_raw = kwargs.get('call_to_action_raw', 0.0)
    note.call_to_action_coeff = kwargs.get('call_to_action_coeff', 0.0)
    note.repeated_take = kwargs.get('repeated_take', 0.0)
    note.repeated_take_raw = kwargs.get('repeated_take_raw', 0.0)
    note.repeated_take_coeff = kwargs.get('repeated_take_coeff', 0.0)
    note.repeated_note = kwargs.get('repeated_note', 0.0)
    note.repeated_note_raw = kwargs.get('repeated_note_raw', 0.0)
    note.repeated_note_coeff = kwargs.get('repeated_note_coeff', 0.0)
    note.messianism = kwargs.get('messianism', 0.0)
    note.messianism_raw = kwargs.get('messianism_raw', 0.0)
    note.messianism_coeff = kwargs.get('messianism_coeff', 0.0)
    note.opposition_to_opponents = kwargs.get('opposition_to_opponents', 0.0)
    note.opposition_to_opponents_raw = kwargs.get('opposition_to_opponents_raw', 0.0)
    note.opposition_to_opponents_coeff = kwargs.get('opposition_to_opponents_coeff', 0.0)
    note.generalization_of_opponents = kwargs.get('generalization_of_opponents', 0.0)
    note.generalization_of_opponents_raw = kwargs.get('generalization_of_opponents_raw', 0.0)
    note.generalization_of_opponents_coeff = kwargs.get('generalization_of_opponents_coeff', 0.0)
    note.reason = kwargs.get('reason', '')
    note.amount_of_propaganda_scores = kwargs.get('amount_of_propaganda_scores', 0.0)
    note.fehner_type = kwargs.get('fehner_type', 'A')
    note.created_at = kwargs.get('created_at', datetime.now())
    note.updated_at = kwargs.get('updated_at', datetime.now())
    note.reposted_from_source_id = kwargs.get('reposted_from_source_id', None)
    return note


def create_mock_source(
    id: int = 1,
    name: str = "Test Source",
    external_id: str = "1",
    platform: str = "telegram",
    rating: float = 0.5,
    is_hidden: bool = False,
    **kwargs
):
    """Create a comprehensive mock Source object."""
    source = Mock()
    source.id = id
    source.name = name
    source.external_id = external_id
    source.platform = platform
    source.rating = rating
    source.is_hidden = is_hidden
    return source


def create_mock_evaluation_context(
    data: str = "test data",
    source_id: int = 1,
    total_score: float = 0.5,
    is_propaganda: bool = False,
    **kwargs
):
    """Create a mock EvaluationContext with all fields."""
    from processors.evaluation_processor import EvaluationContext
    
    context = EvaluationContext(
        data=data,
        source_id=source_id,
        note_dao=kwargs.get('note_dao', Mock()),
    )
    
    context.title = kwargs.get('title', 'Test Title')
    context.total_score = total_score
    context.is_propaganda = is_propaganda
    context.amount_of_propaganda_scores = kwargs.get('amount_of_propaganda_scores', 0.3)
    context.chatgpt_reason = kwargs.get('chatgpt_reason', None)
    
    # Set all evaluation results
    context.sentimental_analysis_result = kwargs.get('sentimental_analysis_result', 0.5)
    context.sentimental_analysis_raw_result = kwargs.get('sentimental_analysis_raw_result', 0.5)
    context.sentimental_analysis_coeff = kwargs.get('sentimental_analysis_coeff', 0.1)
    context.trigger_keywords_result = kwargs.get('trigger_keywords_result', 0.0)
    context.triggered_keywords_raw_result = kwargs.get('triggered_keywords_raw_result', 0.0)
    context.triggered_keywords_coeff = kwargs.get('triggered_keywords_coeff', 0.1)
    context.trigger_topics_result = kwargs.get('trigger_topics_result', 0.3)
    context.triggered_topics_raw_result = kwargs.get('triggered_topics_raw_result', 0.3)
    context.triggered_topics_coeff = kwargs.get('triggered_topics_coeff', 0.1)
    context.text_simplicity_deviation = kwargs.get('text_simplicity_deviation', 0.5)
    context.text_simplicity_deviation_raw_result = kwargs.get('text_simplicity_deviation_raw_result', 0.5)
    context.text_simplicity_deviation_coeff = kwargs.get('text_simplicity_deviation_coeff', 0.1)
    context.confidence_factor = kwargs.get('confidence_factor', 0.5)
    context.confidence_factor_raw_result = kwargs.get('confidence_factor_raw_result', 0.5)
    context.confidence_factor_coeff = kwargs.get('confidence_factor_coeff', 0.1)
    context.clickbait_result = kwargs.get('clickbait_result', 0.0)
    context.clickbait_raw_result = kwargs.get('clickbait_raw_result', 0.0)
    context.clickbait_coeff = kwargs.get('clickbait_coeff', 0.1)
    context.subjective_result = kwargs.get('subjective_result', 0.5)
    context.subjective_raw_result = kwargs.get('subjective_raw_result', 0.5)
    context.subjective_coeff = kwargs.get('subjective_coeff', 0.1)
    context.call_to_action_result = kwargs.get('call_to_action_result', 0.0)
    context.call_to_action_raw_result = kwargs.get('call_to_action_raw_result', 0.0)
    context.call_to_action_coeff = kwargs.get('call_to_action_coeff', 0.1)
    context.repeated_take_result = kwargs.get('repeated_take_result', 0.0)
    context.repeated_take_raw_result = kwargs.get('repeated_take_raw_result', 0.0)
    context.repeated_take_coeff = kwargs.get('repeated_take_coeff', 0.1)
    context.repeated_note_result = kwargs.get('repeated_note_result', 0.0)
    context.repeated_note_raw_result = kwargs.get('repeated_note_raw_result', 0.0)
    context.repeated_note_coeff = kwargs.get('repeated_note_coeff', 0.1)
    context.messianism = kwargs.get('messianism', 0.0)
    context.messianism_raw_result = kwargs.get('messianism_raw_result', 0.0)
    context.messianism_coeff = kwargs.get('messianism_coeff', 0.1)
    context.opposition_to_opponents = kwargs.get('opposition_to_opponents', 0.0)
    context.opposition_to_opponents_raw_result = kwargs.get('opposition_to_opponents_raw_result', 0.0)
    context.opposition_to_opponents_coeff = kwargs.get('opposition_to_opponents_coeff', 0.1)
    context.generalization_of_opponents = kwargs.get('generalization_of_opponents', 0.0)
    context.generalization_of_opponents_raw_result = kwargs.get('generalization_of_opponents_raw_result', 0.0)
    context.generalization_of_opponents_coeff = kwargs.get('generalization_of_opponents_coeff', 0.1)
    
    return context


class MockSQLAlchemy:
    """Mock SQLAlchemy utilities for testing."""
    
    @staticmethod
    def create_mock_query():
        """Create a mock SQLAlchemy query object."""
        mock_query = Mock()
        mock_query.all = Mock(return_value=[])
        mock_query.first = Mock(return_value=None)
        mock_query.filter_by = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        return mock_query
    
    @staticmethod
    def create_mock_session():
        """Create a mock SQLAlchemy session."""
        mock_session = Mock()
        mock_session.query = Mock(return_value=MockSQLAlchemy.create_mock_query())
        mock_session.add = Mock()
        mock_session.add_all = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.flush = Mock()
        mock_session.refresh = Mock()
        mock_session.close = Mock()
        return mock_session


def patch_spacy(nlp_mock=None):
    """Patch spacy module with mock."""
    if nlp_mock is None:
        nlp_mock = Mock()
    
    with patch('processors.evaluation_processor.nlp', nlp_mock):
        yield nlp_mock


def patch_transformers(pipeline_mock=None):
    """Patch transformers pipeline with mock."""
    if pipeline_mock is None:
        pipeline_mock = Mock(return_value=[Mock(score=0.7)])
    
    with patch('processors.evaluation_processor.pipeline', pipeline_mock):
        yield pipeline_mock
