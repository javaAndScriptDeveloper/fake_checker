"""Base evaluator class and shared utilities."""
import json
from abc import ABC, abstractmethod
from pathlib import Path

import spacy

from processors.evaluation_context import EvaluationContext
from utils.logger import get_logger

logger = get_logger(__name__)

# Lazy load spacy model to prevent hanging during imports
_nlp = None


def get_nlp():
    """Get or create the spacy model (lazy loading)."""
    global _nlp
    if _nlp is None:
        try:
            nlp = spacy.load('en_core_web_sm')
        except OSError:
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load('en_core_web_sm')
        _nlp = nlp
    return _nlp


class Evaluation(ABC):

    @abstractmethod
    def evaluate(self, evaluation_context: EvaluationContext):
        pass


def load_json_phrases(file_path: Path, key: str = "phrases") -> list:
    """Load a list of phrases/keywords from a JSON configuration file.

    Args:
        file_path: Path to the JSON file.
        key: Top-level key in the JSON to read from.

    Returns:
        List of phrases/keywords, or empty list on failure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(key, [])
    except Exception as e:
        logger.error(f"Could not load data from {file_path}: {e}", exc_info=True)
        return []


def recalculate_coefficient(get_all_scores):
    """Recalculate the importance coefficient for a given metric.

    Computes the fraction of historical scores that are above the historical average.
    Returns 1 when no historical data exists.
    """
    all_scores = get_all_scores()
    if len(all_scores) == 0:
        return 1
    scores_sum = sum(all_scores)
    average = scores_sum / len(all_scores)
    threshold_counter = sum(1 for score in all_scores if score >= average)
    return threshold_counter / len(all_scores)


def get_historical_average(get_all_scores):
    """Calculate the historical average for a specific metric across all notes.

    Returns 0.3 as default threshold when no historical data is available.
    """
    all_scores = get_all_scores()
    if len(all_scores) == 0:
        return 0.3
    return sum(all_scores) / len(all_scores)


def calculate_amount_of_propaganda_by_scores(context: EvaluationContext):
    """Count how many evaluation dimensions score above their historical average."""
    from dal.dal import Note

    counter = 0
    total_checks = 0

    # Map raw results to their corresponding historical average functions
    checks = [
        (context.sentimental_analysis_raw_result, Note.get_all_sentimental_scores_raw),
        (context.trigger_keywords_raw_result, Note.get_all_triggered_keywords_raw),
        (context.trigger_topics_raw_result, Note.get_all_triggered_topics_raw),
        (context.text_simplicity_deviation_raw_result, Note.get_all_text_simplicity_deviations_raw),
        (context.confidence_factor_raw_result, Note.get_all_confidence_factors_raw),
        (context.clickbait_raw_result, Note.get_all_clickbait_scores_raw),
        (context.subjective_raw_result, Note.get_all_subjectivity_scores_raw),
        (context.call_to_action_raw_result, Note.get_all_call_to_action_scores_raw),
        (context.repeated_take_raw_result, Note.get_all_repeated_takes_raw),
        (context.repeated_note_raw_result, Note.get_all_repeated_notes_raw),
        (context.messianism_raw_result, Note.get_all_messianism_raw),
        (context.opposition_to_opponents_raw_result, Note.get_all_opposition_to_opponents_raw),
        (context.generalization_of_opponents_raw_result, Note.get_all_generalization_of_opponents_raw),
    ]

    for raw_result, avg_fn in checks:
        if raw_result is not None:
            total_checks += 1
            if raw_result > get_historical_average(avg_fn):
                counter += 1

    if total_checks > 0:
        context.amount_of_propaganda_scores = counter / total_checks
    else:
        context.amount_of_propaganda_scores = 0
