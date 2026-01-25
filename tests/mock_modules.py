"""Mock all heavy ML/DB modules for testing."""
import sys
from unittest.mock import MagicMock, Mock

# Mock all ML modules before any imports
sys.modules['spacy'] = MagicMock()
sys.modules['spacy.cli'] = MagicMock()
sys.modules['spacy.cli.download'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['transformers.pipeline'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['textblob'] = MagicMock()
sys.modules['textblob.TextBlob'] = MagicMock()

# Mock sklearn comprehensively
sklearn_mock = MagicMock()
sys.modules['sklearn'] = sklearn_mock
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.naive_bayes'] = MagicMock()
sys.modules['sklearn.naive_bayes.MultinomialNB'] = Mock(return_value=MagicMock())
sys.modules['sklearn.naive_bayes'].MultinomialNB = Mock(return_value=MagicMock())

# Mock textstat
textstat_mock = MagicMock()
textstat_mock.flesch_reading_ease = Mock(return_value=50.0)
sys.modules['textstat'] = textstat_mock

# Mock nltk
nltk_mock = MagicMock()
nltk_mock.download = Mock()
nltk_mock.word_tokenize = Mock(return_value=['test'])
nltk_mock.pos_tag = Mock(return_value=[('test', 'NN')])
nltk_mock.corpus = MagicMock()
nltk_mock.corpus.stopwords = MagicMock()
nltk_mock.corpus.stopwords.words = Mock(return_value=[])
sys.modules['nltk'] = nltk_mock
sys.modules['nltk.corpus'] = nltk_mock.corpus
sys.modules['nltk.corpus.stopwords'] = nltk_mock.corpus.stopwords
