"""Call-to-action detection evaluator using spaCy POS tagging."""
import time

from config.paths import CALL_TO_ACTION_FILE
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation, get_nlp, load_json_phrases
from utils.logger import get_logger

logger = get_logger(__name__)


class CallToAction(Evaluation):

    def __init__(self):
        super().__init__()
        self.cta_keywords = self._load_cta_keywords()

    def _load_cta_keywords(self):
        try:
            keywords = load_json_phrases(CALL_TO_ACTION_FILE, key="keywords")
            return set(keyword.lower() for keyword in keywords)
        except Exception as e:
            logger.error(f"Failed to load call-to-action keywords: {e}", exc_info=True)
            return set()

    def is_call_to_action_token(self, token) -> bool:
        return token.pos_ == "VERB" and token.lemma_.lower() in self.cta_keywords

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()

        text = evaluation_context.data
        doc = get_nlp()(text)

        cta_count = sum(1 for token in doc if self.is_call_to_action_token(token))
        total_verbs = sum(1 for token in doc if token.pos_ == "VERB")

        evaluation_context.call_to_action_result = (cta_count / total_verbs) if total_verbs else 0.0
        evaluation_context.call_to_action_raw_result = evaluation_context.call_to_action_result
        evaluation_context.call_to_action_execution_time = time.perf_counter() - start_time
