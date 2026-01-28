"""Generalization of opponents detection evaluator using sentence-transformers."""
import time

from sentence_transformers import SentenceTransformer, util

from config.paths import GENERALIZATION_OF_OPPONENTS_FILE
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation, load_json_phrases
from utils.logger import get_logger

logger = get_logger(__name__)


class GeneralizationOfOpponents(Evaluation):

    def __init__(self):
        self._model = None
        self._phrases = None
        self._embs = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-mpnet-base-v2')
        return self._model

    @property
    def phrases(self):
        if self._phrases is None:
            self._phrases = load_json_phrases(GENERALIZATION_OF_OPPONENTS_FILE)
        return self._phrases

    @property
    def embs(self):
        if self._embs is None:
            self._embs = self.model.encode(self.phrases, convert_to_tensor=True)
        return self._embs

    def evaluate(self, evaluation_context: EvaluationContext):
        text = evaluation_context.data
        text_emb = self.model.encode(text, convert_to_tensor=True)

        score = float(util.cos_sim(text_emb, self.embs).max())

        evaluation_context.generalization_of_opponents = score
        evaluation_context.generalization_of_opponents_raw_result = score
