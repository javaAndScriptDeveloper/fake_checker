"""Tests for Enums module."""
import pytest
from enums import PLATFORM_TYPE, FEHNER_TYPE


class TestEnums:
    """Test cases for enums."""
    
    def test_platform_type_values(self):
        """Test PLATFORM_TYPE enum values."""
        assert PLATFORM_TYPE.TELEGRAM.value == "telegram"
        assert PLATFORM_TYPE.TWITCH.value == "twitch"
    
    def test_platform_type_from_string(self):
        """Test creating PLATFORM_TYPE from string."""
        assert PLATFORM_TYPE("telegram") == PLATFORM_TYPE.TELEGRAM
        assert PLATFORM_TYPE("twitch") == PLATFORM_TYPE.TWITCH
    
    def test_fehner_type_values(self):
        """Test FEHNER_TYPE enum values."""
        assert FEHNER_TYPE.A.value == "A"
        assert FEHNER_TYPE.B.value == "B"
    
    def test_fehner_type_from_string(self):
        """Test creating FEHNER_TYPE from string."""
        assert FEHNER_TYPE("A") == FEHNER_TYPE.A
        assert FEHNER_TYPE("B") == FEHNER_TYPE.B
    
    def test_invalid_enum_value(self):
        """Test that invalid enum values raise ValueError."""
        with pytest.raises(ValueError):
            PLATFORM_TYPE("invalid")
