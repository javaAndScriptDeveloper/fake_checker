"""Shared pytest fixtures and configuration."""
import sys
from unittest.mock import Mock, MagicMock
import pytest

# Mock ML modules BEFORE any imports
spacy_mock = Mock()
spacy_nlp_mock = Mock()
mock_token = Mock(pos_=Mock(return_value='NOUN'), lemma_=Mock(return_value='test'))
spacy_nlp_mock.return_value = [mock_token]
spacy_mock.load = Mock(return_value=spacy_nlp_mock)
spacy_mock.cli = Mock()
sys.modules['spacy'] = spacy_mock

# Mock transformers pipeline to return proper structures
sys.modules['transformers'] = Mock()

# Mock sentence_transformers
sentence_transformers_mock = Mock()
util_mock = Mock()
max_mock = Mock(return_value=0.5)
cos_sim_mock = Mock(return_value=max_mock)
util_mock.cos_sim = cos_sim_mock
sentence_transformers_mock.SentenceTransformer = MagicMock()
sentence_transformers_mock.util = util_mock
sys.modules['sentence_transformers'] = sentence_transformers_mock

# Mock textstat
textstat_mock = Mock()
textstat_mock.flesch_reading_ease = Mock(return_value=50.0)
sys.modules['textstat'] = textstat_mock

# Mock sklearn modules
sklearn_mock = Mock()
naive_bayes_mock = Mock()
MultinomialNB_mock = MagicMock()
BernoulliNB_mock = MagicMock()
sklearn_mock.naive_bayes = naive_bayes_mock
naive_bayes_mock.MultinomialNB = MultinomialNB_mock
naive_bayes_mock.BernoulliNB = BernoulliNB_mock
feature_extraction_mock = Mock()
text_mock = Mock()
TfidfVectorizer_mock = MagicMock()
feature_extraction_mock.text = text_mock
text_mock.TfidfVectorizer = TfidfVectorizer_mock
sklearn_mock.feature_extraction = feature_extraction_mock
metrics_mock = Mock()
pairwise_mock = Mock()
cosine_similarity_mock = MagicMock()
metrics_mock.pairwise = pairwise_mock
pairwise_mock.cosine_similarity = cosine_similarity_mock
sklearn_mock.metrics = metrics_mock
model_selection_mock = Mock()
cross_val_score_mock = MagicMock()
model_selection_mock.cross_val_score = cross_val_score_mock
sklearn_mock.model_selection = model_selection_mock
sys.modules['sklearn'] = sklearn_mock
sys.modules['sklearn.naive_bayes'] = naive_bayes_mock
sys.modules['sklearn.feature_extraction'] = feature_extraction_mock
sys.modules['sklearn.feature_extraction.text'] = text_mock
sys.modules['sklearn.metrics'] = metrics_mock
sys.modules['sklearn.metrics.pairwise'] = pairwise_mock
sys.modules['sklearn.model_selection'] = model_selection_mock

# Mock textblob
sys.modules['textblob'] = Mock()


@pytest.fixture
def mock_note_dao():
    dao = Mock()
    dao.get_by_hash = Mock(return_value=None)
    dao.get_by_source_id = Mock(return_value=[])
    dao.get_all = Mock(return_value=[])
    dao.save = Mock()
    dao.update = Mock()
    dao.delete = Mock()
    return dao


@pytest.fixture
def mock_source_dao():
    dao = Mock()
    dao.get_by_id = Mock(return_value=None)
    dao.get_by_external_id = Mock(return_value=None)
    dao.get_all = Mock(return_value=[])
    dao.save = Mock()
    dao.update = Mock()
    dao.delete = Mock()
    return dao


@pytest.fixture
def mock_evaluation_processor():
    processor = Mock()
    processor.evaluate = Mock()
    return processor


@pytest.fixture
def mock_fehner_processor():
    processor = Mock()
    processor.calculate_fehner_score = Mock(return_value=0.5)
    processor.calculate_similarity_score = Mock(return_value=0.7)
    return processor


@pytest.fixture
def mock_translator():
    translator = Mock()
    translator.translate_to_english = Mock(return_value="translated text")
    return translator


@pytest.fixture(autouse=True)
def mock_note_static_methods(monkeypatch):
    from dal.dal import Note
    monkeypatch.setattr(Note, 'get_all_sentimental_scores', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_triggered_keywords', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_triggered_topics', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_text_simplicity_deviations', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_confidence_factors', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_clickbait_scores', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_subjectivity_scores', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_call_to_action_scores', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_repeated_takes', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_repeated_notes', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_messianism', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_opposition_to_opponents', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_generalization_of_opponents', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_sentimental_scores_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_triggered_keywords_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_triggered_topics_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_text_simplicity_deviations_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_confidence_factors_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_clickbait_scores_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_subjectivity_scores_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_call_to_action_scores_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_repeated_takes_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_repeated_notes_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_messianism_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_opposition_to_opponents_raw', Mock(return_value=[]))
    monkeypatch.setattr(Note, 'get_all_generalization_of_opponents_raw', Mock(return_value=[]))


@pytest.fixture(autouse=True)
def disable_coldstart():
    from manager import Manager
    original_coldstart = Manager.coldstart
    Manager.coldstart = lambda self, path: None
    yield
    Manager.coldstart = original_coldstart


@pytest.fixture(autouse=True)
def patch_evaluation_classes(monkeypatch):
    """Patch evaluation classes to return proper pipeline results."""
    from processors.evaluation_processor import SentimentalAnalysis, TriggerTopics
    
    # Mock SentimentalAnalysis pipeline
    class MockSentimentPipeline:
        def __call__(self, text_list):
            return [{'score': 0.7, 'label': 'POSITIVE'}]
    
    SentimentalAnalysis._pipeline = MockSentimentPipeline()
    
    # Mock TriggerTopics classifier
    class MockClassifier:
        def __call__(self, *args, **kwargs):
            return {'labels': ['politics', 'non political'], 'scores': [0.5, 0.5]}
    
    TriggerTopics._classifier = MockClassifier()
