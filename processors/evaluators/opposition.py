"""Opposition to opponents detection evaluator using sentence-transformers."""
import time

from sentence_transformers import SentenceTransformer, util

from config.paths import OPPOSITION_TO_OPPONENTS_FILE
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation, load_json_phrases
from utils.logger import get_logger

logger = get_logger(__name__)


class OppositionToOpponents(Evaluation):

    def __init__(self):
        self._model = None
        self._opposition_phrases = None
        self._embs = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-mpnet-base-v2')
        return self._model

    @property
    def opposition_phrases(self):
        if self._opposition_phrases is None:
            self._opposition_phrases = load_json_phrases(OPPOSITION_TO_OPPONENTS_FILE)
        return self._opposition_phrases

    @property
    def embs(self):
        if self._embs is None:
            self._embs = self.model.encode(self.opposition_phrases, convert_to_tensor=True)
        return self._embs

    def evaluate(self, evaluation_context: EvaluationContext):
        text = evaluation_context.data
        text_emb = self.model.encode(text, convert_to_tensor=True)

        score = float(util.cos_sim(text_emb, self.embs).max())

        evaluation_context.opposition_to_opponents_raw_result = score
        evaluation_context.opposition_to_opponents = score
