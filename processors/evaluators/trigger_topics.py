"""Trigger topics detection evaluator using zero-shot classification."""
import json
import time

from transformers import pipeline as hf_pipeline

from config.paths import TRIGGER_TOPICS_FILE
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation


class TriggerTopics(Evaluation):
    _classifier = None

    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = hf_pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        return self._classifier

    def parse_config(self):
        with open(TRIGGER_TOPICS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get("topics", [])

    def resolve_topics(self, text) -> list:
        topics = self.parse_config()
        result = self.classifier(text, ["politics", "non political"])
        sum_value = 0
        for topic in topics:
            position = result['labels'].index(topic)
            sum_value += result['scores'][position]
        return sum_value

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        evaluation_context.trigger_topics_result = self.resolve_topics(evaluation_context.data)
        evaluation_context.trigger_topics_raw_result = evaluation_context.trigger_topics_result
        end_time = time.perf_counter()
        evaluation_context.trigger_topics_execution_time = end_time - start_time
