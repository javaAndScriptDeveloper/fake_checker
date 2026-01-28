"""Sentiment analysis evaluator using HuggingFace transformers."""
import time

from transformers import pipeline as hf_pipeline

from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class SentimentalAnalysis(Evaluation):
    _pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = hf_pipeline("sentiment-analysis")
        return self._pipeline

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        sentiment_pipeline = self.pipeline
        result = sentiment_pipeline([evaluation_context.data])[0]
        evaluation_context.sentimental_analysis_result = result['score']
        evaluation_context.sentimental_analysis_raw_result = evaluation_context.sentimental_analysis_result
        end_time = time.perf_counter()
        evaluation_context.sentimental_analysis_execution_time = end_time - start_time
