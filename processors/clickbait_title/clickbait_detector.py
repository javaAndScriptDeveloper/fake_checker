"""Clickbait detection using a Naive Bayes classifier with model persistence.

The trained model and vocabulary are cached to disk using joblib to avoid
retraining on every application startup.
"""
from pathlib import Path

import joblib
import numpy as np
from sklearn.naive_bayes import MultinomialNB

from config.paths import CLICKBAIT_MODEL_FILE, MODELS_DIR
from processors.clickbait_title.features import (
    top_30_words, stop_words, lexical, pos_tags, interpunction,
    avg_char_num, ttr_normalized, num_words, long_words, q_words_counts,
)
from processors.clickbait_title.helpers import get_data
from utils.logger import get_logger

logger = get_logger(__name__)

# Path for the saved top_words vocabulary
_TOP_WORDS_FILE = MODELS_DIR / "clickbait_top_words.joblib"

# Model version - bump this when training data or features change to force retraining
_MODEL_VERSION = 1
_MODEL_VERSION_FILE = MODELS_DIR / "clickbait_model_version.txt"

# Training data paths (relative to project root)
_CLICKBAIT_DIR = Path(__file__).parent
_NON_CLICKBAIT_DATA = _CLICKBAIT_DIR / "non_clickbait_data.txt"
_CLICKBAIT_DATA = _CLICKBAIT_DIR / "clickbait_data.txt"


def _get_saved_version() -> int:
    """Read the saved model version from disk."""
    try:
        if _MODEL_VERSION_FILE.exists():
            return int(_MODEL_VERSION_FILE.read_text().strip())
    except (ValueError, OSError):
        pass
    return 0


def _save_version(version: int) -> None:
    """Write the model version to disk."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    _MODEL_VERSION_FILE.write_text(str(version))


def prepare_model():
    """Prepares and trains the clickbait detection model."""
    non_clickbait_headlines = get_data(str(_NON_CLICKBAIT_DATA))
    clickbait_headlines = get_data(str(_CLICKBAIT_DATA))
    all_headlines = non_clickbait_headlines + clickbait_headlines

    non_cb_labels = [0] * len(non_clickbait_headlines)
    cb_labels = [1] * len(clickbait_headlines)
    all_labels = non_cb_labels + cb_labels

    top_words = top_30_words(all_headlines)

    all_features = np.concatenate(
        (
            stop_words(all_headlines),
            pos_tags(all_headlines),
            lexical(all_headlines, top_words),
            interpunction(all_headlines),
            np.array(avg_char_num(all_headlines)).reshape(len(all_headlines), 1),
            np.array(ttr_normalized(all_headlines)).reshape(len(all_headlines), 1),
            np.array(num_words(all_headlines)).reshape(len(all_headlines), 1),
            np.array(long_words(all_headlines)).reshape(len(all_headlines), 1),
            q_words_counts(all_headlines),
        ),
        axis=1,
    )

    model = MultinomialNB()
    model.fit(all_features, all_labels)

    return model, top_words


def _save_model(model, top_words) -> None:
    """Persist the trained model and vocabulary to disk."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, CLICKBAIT_MODEL_FILE)
    joblib.dump(top_words, _TOP_WORDS_FILE)
    _save_version(_MODEL_VERSION)
    logger.info(f"Clickbait model saved to {CLICKBAIT_MODEL_FILE} (version {_MODEL_VERSION})")


def _load_model():
    """Load a previously saved model and vocabulary from disk."""
    if (
        CLICKBAIT_MODEL_FILE.exists()
        and _TOP_WORDS_FILE.exists()
        and _get_saved_version() == _MODEL_VERSION
    ):
        model = joblib.load(CLICKBAIT_MODEL_FILE)
        top_words = joblib.load(_TOP_WORDS_FILE)
        logger.info(f"Clickbait model loaded from {CLICKBAIT_MODEL_FILE} (version {_MODEL_VERSION})")
        return model, top_words
    return None, None


# Lazy load model - only prepare when needed
_model = None
_top_words = None


def _get_model():
    """Get or create the model (lazy loading with disk persistence)."""
    global _model, _top_words
    if _model is None:
        # Try loading from disk first
        _model, _top_words = _load_model()
        if _model is None:
            # Train and persist
            logger.info("Training clickbait model (no cached model found)...")
            _model, _top_words = prepare_model()
            _save_model(_model, _top_words)
    return _model, _top_words


def is_clickbait(text):
    """Determines if a given text is clickbait using the trained model."""
    model, top_words = _get_model()

    text_features = np.concatenate(
        (
            stop_words([text]),
            pos_tags([text]),
            lexical([text], top_words),
            interpunction([text]),
            np.array(avg_char_num([text])).reshape(1, 1),
            np.array(ttr_normalized([text])).reshape(1, 1),
            np.array(num_words([text])).reshape(1, 1),
            np.array(long_words([text])).reshape(1, 1),
            q_words_counts([text]),
        ),
        axis=1,
    )

    return model.predict(text_features)
