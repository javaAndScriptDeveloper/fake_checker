"""Trigger keywords detection evaluator."""
import json
import time

from config.paths import TRIGGER_KEYWORDS_FILE
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class TriggerKeywords(Evaluation):

    def parse_config(self):
        with open(TRIGGER_KEYWORDS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get("language", {}).get("english", [])

    def count_and_divide(self, data, words_to_count):
        all_words = data.split()
        word_counts = {word: all_words.count(word) for word in words_to_count}
        total_word_count = sum(word_counts.values())
        return 1 if total_word_count > 1 else 0

    def evaluate(self, evaluation_context: EvaluationContext):
        trigger_keywords = self.parse_config()
        start_time = time.perf_counter()
        evaluation_context.trigger_keywords_result = self.count_and_divide(evaluation_context.data, trigger_keywords)
        evaluation_context.trigger_keywords_raw_result = evaluation_context.trigger_keywords_result
        end_time = time.perf_counter()
        evaluation_context.trigger_keywords_execution_time = end_time - start_time
