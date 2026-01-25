"""Tests for Translation module."""
import pytest
from unittest.mock import Mock, patch


class TestTranslator:
    """Test cases for Translator class."""
    
    @pytest.fixture
    def translator(self):
        """Create translator instance."""
        from translation import Translator
        return Translator()
    
    def test_initialization(self, translator):
        """Test translator initialization."""
        assert translator is not None
        assert len(translator.supported_translations_list) == 2
        assert translator.supported_translations_list[0]["label"] == "English"
        assert translator.supported_translations_list[1]["label"] == "Ukrainian"
    
    @patch('translation.GoogleTranslator')
    def test_translate_to_english_success(self, mock_translator_class, translator):
        """Test successful translation to English."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.translate.return_value = "Translated text"
        mock_translator_class.return_value = mock_instance
        
        # Execute
        result = translator.translate_to_english("Hola mundo", "spanish")
        
        # Assert
        assert result == "Translated text"
        mock_translator_class.assert_called_once_with(source="spanish", target="english")
        mock_instance.translate.assert_called_once_with("Hola mundo")
    
    @patch('translation.GoogleTranslator')
    def test_translate_to_english_error(self, mock_translator_class, translator):
        """Test translation error handling."""
        # Setup mock to raise exception
        mock_instance = Mock()
        mock_instance.translate.side_effect = Exception("Network error")
        mock_translator_class.return_value = mock_instance
        
        # Execute
        result = translator.translate_to_english("Test", "english")
        
        # Assert
        assert "Translation Error" in result
    
    def test_translate_empty_text(self, translator):
        """Test translation with empty text."""
        result = translator.translate_to_english("", "english")
        assert result == ""
    
    def test_translate_none_language(self, translator):
        """Test translation with None language."""
        result = translator.translate_to_english("Test", None)
        # Should handle gracefully
        assert result is not None
