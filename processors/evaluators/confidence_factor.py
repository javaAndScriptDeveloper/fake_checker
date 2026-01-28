"""Confidence factor evaluator based on historical source scores."""
import time

from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class ConfidenceFactor(Evaluation):

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        notes = evaluation_context.note_dao.get_by_source_id(evaluation_context.source_id)
        if notes:
            total_scores = [note.total_score for note in notes]
            evaluation_context.confidence_factor = (sum(total_scores) / len(total_scores)) / 100
        else:
            evaluation_context.confidence_factor = 0
        end_time = time.perf_counter()
        evaluation_context.confidence_factor_raw_result = evaluation_context.confidence_factor
        evaluation_context.confidence_factor_execution_time = end_time - start_time
