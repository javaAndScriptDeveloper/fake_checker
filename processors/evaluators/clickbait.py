"""Clickbait detection evaluator."""
import time

from processors.clickbait_title.clickbait_detector import is_clickbait
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class ClickBait(Evaluation):

    def evaluate(self, evaluation_context: EvaluationContext):
        if evaluation_context.title is None:
            evaluation_context.clickbait_result = 0
            return
        start_time = time.perf_counter()
        evaluation_context.clickbait_result = float(is_clickbait(evaluation_context.title)[0])
        evaluation_context.clickbait_raw_result = evaluation_context.clickbait_result
        end_time = time.perf_counter()
        evaluation_context.clickbait_execution_time = end_time - start_time
