import json
import time
from abc import ABC, abstractmethod
from transformers import pipeline
import textstat
from config import config
from dal.dal import NoteDao, Note


class EvaluationContext:

    def __init__(self, data, source_id, note_dao):
        self.data = data
        self.source_id = source_id
        self.note_dao = note_dao
        self.sentimental_analysis_result = 0
        self.sentimental_analysis_execution_time = 0
        self.trigger_keywords_result = 0
        self.trigger_keywords_execution_time = 0
        self.trigger_topics_result = 0
        self.trigger_topics_execution_time = 0
        self.clickbait_result = 0
        self.clickbait_execution_time = 0
        self.subjective_result = 0
        self.subjective_execution_time = 0
        self.text_simplicity_deviation = 0
        self.text_simplicity_deviation_execution_time = 0
        self.confidence_factor = 100
        self.confidence_factor_execution_time = 100

    def __str__(self) -> str:
        return f'sentimental_analysis_result: {self.sentimental_analysis_result},\n' \
            + f'sentimental_analysis_execution_time: {self.sentimental_analysis_execution_time},\n' \
            + f'trigger_keywords_result: {self.trigger_keywords_result},\n' \
            + f'trigger_keywords_execution_time: {self.trigger_keywords_execution_time},\n' \
            + f'trigger_topics_result: {self.trigger_topics_result},\n' \
            + f'trigger_topics_execution_time: {self.trigger_topics_execution_time},\n' \
            + f'text_simplicity_deviation: {self.text_simplicity_deviation},\n' \
            + f'text_simplicity_deviation_execution_time: {self.text_simplicity_deviation_execution_time},\n' \
            + f'clickbait: {self.clickbait_result},\n' \
            + f'clickbait_execution_time: {self.clickbait_execution_time},\n' \
            + f'subjective: {self.subjective_result},\n' \
            + f'subjective_execution_time: {self.subjective_execution_time},\n' \
            + f'confidence_factor: {self.confidence_factor}'


class Evaluation(ABC):

    @abstractmethod
    def evaluate(self, evaluation_context: EvaluationContext):
        pass


class SentimentalAnalysis(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        sentiment_pipeline = pipeline("sentiment-analysis")
        result = sentiment_pipeline([evaluation_context.data])[0]
        evaluation_context.sentimental_analysis_result = abs(-1 * result['score'])
        end_time = time.perf_counter()
        evaluation_context.sentimental_analysis_execution_time = end_time - start_time


class TriggerKeywords(Evaluation):

    def parse_config(self):
        with open('trigger_keywords.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get("language", {}).get("russian", [])

    def count_and_divide(self, data, words_to_count):
        # Split the text into words
        all_words = data.split()

        # Count occurrences of specified words
        word_counts = {word: all_words.count(word) for word in words_to_count}

        # Calculate the total number of words in the text
        total_words = len(all_words)

        # Sum the counts of all words
        total_word_count = sum(word_counts.values())

        # Divide the total word count by the total number of words
        occurrences_ratio = total_word_count / total_words

        return occurrences_ratio

    def evaluate(self, evaluation_context):
        trigger_keywords = self.parse_config()
        start_time = time.perf_counter()
        evaluation_context.trigger_keywords_result = self.count_and_divide(evaluation_context.data, trigger_keywords)
        end_time = time.perf_counter()
        evaluation_context.trigger_keywords_execution_time = end_time - start_time


class TriggerTopics(Evaluation):

    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def parse_config(self):
        with open('trigger_topics.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get("topics", [])

    def resolve_topics(self, text) -> list:
        topics = self.parse_config()
        result = self.classifier(text, topics)
        return result['labels'][0]

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        resolved_topics = self.resolve_topics(evaluation_context.data)
        evaluation_context.trigger_topics_result = 100 if len(resolved_topics) > 0 else 0
        end_time = time.perf_counter()
        evaluation_context.trigger_topics_execution_time = end_time - start_time

class ClickBait(Evaluation):

    classifier = pipeline("text-classification", model="distilbert-base-uncased")

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        evaluation_context.clickbait_result = self.classifier(evaluation_context.data)[0]['score']
        end_time = time.perf_counter()
        evaluation_context.clickbait_execution_time = end_time - start_time

class Subjective(Evaluation):

    classifier = pipeline("text-classification", model="roberta-base")

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        evaluation_context.subjective_result = self.classifier(evaluation_context.data)[0]['score']
        end_time = time.perf_counter()
        evaluation_context.subjective_execution_time = end_time - start_time

class TextSimplicity(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        grade_level = textstat.flesch_reading_ease(evaluation_context.data)
        evaluation_context.text_simplicity_deviation = abs(config.average_news_simplicity - grade_level) / 100
        end_time = time.perf_counter()
        evaluation_context.text_simplicity_deviation_execution_time = end_time - start_time


class ConfidenceFactor(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        notes = evaluation_context.note_dao.get_by_source_id(evaluation_context.source_id)
        if notes:
            total_scores = [note.total_score for note in notes]
            evaluation_context.confidence_factor = sum(total_scores) / len(total_scores)
        else:
            evaluation_context.confidence_factor = 100
        end_time = time.perf_counter()
        evaluation_context.confidence_factor_execution_time = end_time - start_time


class EvaluationProcessor:

    def __init__(self, note_dao: NoteDao):
        self.note_dao = note_dao
        self.evaluations = [SentimentalAnalysis(), TriggerKeywords(), TextSimplicity(), ConfidenceFactor(), TriggerTopics(), ClickBait(), Subjective()]

    def evaluate(self, data, source_id):
        context = EvaluationContext(data, source_id, self.note_dao)
        for i in self.evaluations:
            i.evaluate(context)
        return context


class CalculationUtils:

    def calculate_total_score(note: Note):
        return note.sentimental_score * config.sentimental_score_coeff \
            + note.triggered_keywords * config.triggered_keywords_coeff \
            + note.triggered_topics * config.triggered_topics_coeff \
            + note.text_simplicity_deviation * config.text_simplicity_deviation \
            + note.clickbait * config.clickbait_coeff \
            + note.subjective * config.subjective_coeff \
            + float(note.confidence_factor) * config.confidence_factor_coeff
