"""Messianism detection evaluator using sentence-transformers."""
import time

from sentence_transformers import SentenceTransformer, util

from config.paths import MESSIAH_FILE
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation, load_json_phrases
from utils.logger import get_logger

logger = get_logger(__name__)


class Messianism(Evaluation):

    def __init__(self):
        self._model = None
        self._messiah_phrases = None
        self._messiah_embs = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-mpnet-base-v2')
        return self._model

    @property
    def messiah_phrases(self):
        if self._messiah_phrases is None:
            self._messiah_phrases = load_json_phrases(MESSIAH_FILE)
        return self._messiah_phrases

    @property
    def messiah_embs(self):
        if self._messiah_embs is None:
            self._messiah_embs = self.model.encode(self.messiah_phrases, convert_to_tensor=True)
        return self._messiah_embs

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        text = evaluation_context.data
        text_emb = self.model.encode(text, convert_to_tensor=True)

        messiah_score = float(util.cos_sim(text_emb, self.messiah_embs).max())

        evaluation_context.messianism_raw_result = messiah_score
        evaluation_context.messianism = messiah_score
