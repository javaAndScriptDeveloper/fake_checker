"""Centralized path configuration for the application.

This module provides consistent path resolution for all file and directory
references throughout the codebase, eliminating hardcoded absolute paths.
"""
from pathlib import Path

# Project root directory (parent of config/)
PROJECT_ROOT = Path(__file__).parent.parent

# Configuration directory
CONFIG_DIR = PROJECT_ROOT / "config"

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
COLDSTART_DIR = DATA_DIR / "coldstart"

# Models directory
MODELS_DIR = PROJECT_ROOT / "models"

# Configuration files
TRIGGER_KEYWORDS_FILE = CONFIG_DIR / "trigger_keywords.json"
TRIGGER_TOPICS_FILE = CONFIG_DIR / "trigger_topics.json"
CALL_TO_ACTION_FILE = CONFIG_DIR / "call_to_action_keywords.json"
MESSIAH_FILE = CONFIG_DIR / "messiah.json"
OPPOSITION_TO_OPPONENTS_FILE = CONFIG_DIR / "opposition_to_opponents.json"
GENERALIZATION_OF_OPPONENTS_FILE = CONFIG_DIR / "generalization_of_opponents.json"

# Clickbait model files
CLICKBAIT_MODEL_FILE = MODELS_DIR / "clickbait_model.joblib"
CLICKBAIT_VECTORIZER_FILE = MODELS_DIR / "clickbait_vectorizer.joblib"


def ensure_dirs_exist() -> None:
    """Create required directories if they don't exist."""
    for dir_path in [DATA_DIR, COLDSTART_DIR, MODELS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
