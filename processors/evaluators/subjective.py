"""Subjectivity analysis evaluator using TextBlob."""
import time

from textblob import TextBlob

from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class Subjective(Evaluation):

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        blob = TextBlob(evaluation_context.data)
        evaluation_context.subjective_result = blob.sentiment.subjectivity
        evaluation_context.subjective_raw_result = evaluation_context.subjective_result
        end_time = time.perf_counter()
        evaluation_context.subjective_execution_time = end_time - start_time
