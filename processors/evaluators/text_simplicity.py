"""Text simplicity evaluator using Flesch reading ease score."""
import time

import textstat

from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class TextSimplicity(Evaluation):

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        grade_level = textstat.flesch_reading_ease(evaluation_context.data)
        evaluation_context.text_simplicity_deviation = grade_level / 100
        evaluation_context.text_simplicity_deviation_raw_result = evaluation_context.text_simplicity_deviation
        end_time = time.perf_counter()
        evaluation_context.text_simplicity_deviation_execution_time = end_time - start_time
