import json
import time
from abc import ABC, abstractmethod
from typing import List

import numpy as np
import spacy
import textstat
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from transformers import pipeline

from config import config
from dal.dal import Note, NoteDao

spacy.cli.download("en_core_web_sm")
nlp = spacy.load('en_core_web_sm')


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
        self.call_to_action_result = 0
        self.call_to_action_execution_time = 0
        self.repeated_take_result = 0
        self.repeated_take_execution_time = 0
        self.repeated_note_result = 0
        self.repeated_note_execution_time = 0

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
            + f'confidence_factor: {self.confidence_factor}' \
            + f'confidence_factor_execution_time: {self.confidence_factor_execution_time}' \
            + f'call_to_action: {self.call_to_action_result}' \
            + f'call_to_action_execution_time: {self.call_to_action_execution_time}' \
            + f'repeated_take: {self.repeated_take_result}' \
            + f'repeated_take_execution_time: {self.repeated_take_execution_time}' \
            + f'repeated_note: {self.repeated_note_result}' \
            + f'repeated_note_execution_time: {self.repeated_note_execution_time}'


class Evaluation(ABC):

    @abstractmethod
    def evaluate(self, evaluation_context: EvaluationContext):
        pass

class SentimentalAnalysis(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        sentiment_pipeline = pipeline("sentiment-analysis")
        result = sentiment_pipeline([evaluation_context.data])[0]
        evaluation_context.sentimental_analysis_result = result['score']
        end_time = time.perf_counter()
        evaluation_context.sentimental_analysis_execution_time = end_time - start_time


class TriggerKeywords(Evaluation):

    def parse_config(self):
        with open('trigger_keywords.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get("language", {}).get("english", [])

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

        return occurrences_ratio * 100

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
        result = self.classifier(text, ["finance", "sports", "politics", "technology", "health", "entertainment"])
        sum_value = 0
        for topic in topics:
            position = result['labels'].index(topic)
            sum_value += result['scores'][position]
        return sum_value

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        evaluation_context.trigger_topics_result = self.resolve_topics(evaluation_context.data)
        end_time = time.perf_counter()
        evaluation_context.trigger_topics_execution_time = end_time - start_time


class ClickBait(Evaluation):
    classifier = pipeline("text-classification", model="distilbert-base-uncased")

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        evaluation_context.clickbait_result = self.classifier(evaluation_context.data)[0]['score'] * 100
        end_time = time.perf_counter()
        evaluation_context.clickbait_execution_time = end_time - start_time


class Subjective(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        blob = TextBlob(evaluation_context.data)
        evaluation_context.subjective_result = blob.sentiment.subjectivity
        end_time = time.perf_counter()
        evaluation_context.subjective_execution_time = end_time - start_time


class TextSimplicity(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        grade_level = textstat.flesch_reading_ease(evaluation_context.data)
        evaluation_context.text_simplicity_deviation = abs(config.average_news_simplicity - grade_level)
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
            evaluation_context.confidence_factor = 0
        end_time = time.perf_counter()
        evaluation_context.confidence_factor_execution_time = end_time - start_time


class CallToAction(Evaluation):

    def parse_config(self):
        with open('call_to_action_keywords.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get("keywords", [])

    def is_call_to_action(self, sentence: str) -> bool:
        doc = nlp(sentence)
        cta_keywords = self.parse_config()
        for token in doc:
            if token.lemma_.lower() in cta_keywords:
                return True
        return False

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()

        text = evaluation_context.data

        doc = nlp(text)
        sentences = list(doc.sents)

        if sentences:
            cta_counts = sum(1 for sentence in sentences if self.is_call_to_action(sentence.text))
            total_sentences = len(sentences)

            evaluation_context.call_to_action_result = cta_counts / total_sentences * 100
        else:
            evaluation_context.call_to_action_result = 0

        end_time = time.perf_counter()
        evaluation_context.evaluation_execution_time = end_time - start_time


class RepeatedNote(Evaluation):

    def get_embedding(self, text):
        """Generate an embedding for a single text."""
        doc = nlp(text)
        return doc.vector

    def check_similarity(self, reference_text, text_list):
        """Check if any text in the list is similar to the reference text based on the threshold."""
        ref_embedding = self.get_embedding(reference_text)
        results = []

        for text in text_list:
            text_embedding = self.get_embedding(text)
            sim = cosine_similarity([ref_embedding], [text_embedding])[0][0]
            if sim > config.similarity_threshold:
                results.append((text, sim))

        return results

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        notes_from_source = evaluation_context.note_dao.get_by_source_id(evaluation_context.source_id)
        repeated_notes = self.check_similarity(evaluation_context.data, [note.content for note in notes_from_source])
        evaluation_context.repeated_note_result = 100 if len(repeated_notes) > 0 else 0
        end_time = time.perf_counter()
        evaluation_context.confidence_factor_execution_time = end_time - start_time


class RepeatedTake(Evaluation):

    def get_sentence_embeddings(self, sentences):
        """Generate embeddings for a list of sentences."""
        embeddings = []
        for sentence in sentences:
            doc = nlp(sentence)
            embeddings.append(doc.vector)
        return np.array(embeddings)

    def find_repeated_sentences(self, sentences):
        """Check for repeated sentences based on similarity of embeddings."""
        embeddings = self.get_sentence_embeddings(sentences)
        num_sentences = len(sentences)
        similar_sentences = set()

        # Compare each sentence embedding with every other
        for i in range(num_sentences):
            for j in range(i + 1, num_sentences):
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                if sim > config.similarity_threshold:
                    similar_sentences.add((i, j))

        return similar_sentences

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()

        # Retrieve the text to analyze
        text = evaluation_context.data

        # Split text into sentences
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]

        # Check for repeated sentences
        repeated_sentence_indices = self.find_repeated_sentences(sentences)

        evaluation_context.repeated_take_result = len(repeated_sentence_indices) / len(sentences) * 100

        end_time = time.perf_counter()
        evaluation_context.repeated_take_execution_time = end_time - start_time


class EvaluationProcessor:

    def __init__(self, note_dao: NoteDao):
        self.note_dao = note_dao
        self.evaluations = [SentimentalAnalysis(), TriggerKeywords(),
                            TextSimplicity(), ConfidenceFactor(),
                            TriggerTopics(), ClickBait(),
                            Subjective(), CallToAction(),
                            RepeatedNote(), RepeatedTake()]

    def evaluate(self, data, source_id):
        context = EvaluationContext(data, source_id, self.note_dao)
        for i in self.evaluations:
            i.evaluate(context)
        return context


class CalculationUtils:

    def calculate_total_score(note: Note):
        total_score = note.sentimental_score * config.sentimental_score_coeff \
                      + note.triggered_keywords * config.triggered_keywords_coeff \
                      + note.triggered_topics * config.triggered_topics_coeff \
                      + note.text_simplicity_deviation * config.text_simplicity_deviation \
                      + note.clickbait * config.clickbait_coeff \
                      + note.subjective * config.subjective_coeff \
                      + note.call_to_action * config.call_to_action_coeff \
                      + note.repeated_take * config.repeated_take_coeff \
                      + note.repeated_note * config.repeated_note_coeff \
                      + float(note.confidence_factor) * config.confidence_factor_coeff

        print(
            f"sentimental score ({note.sentimental_score}) * sentimental score coeff ({config.sentimental_score_coeff}) = {note.sentimental_score * config.sentimental_score_coeff}\n"
            + f"triggered topics ({note.triggered_topics}) * triggered topics coeff ({config.triggered_topics_coeff}) = {note.triggered_topics * config.triggered_topics_coeff}\n"
            + f"text simplicity deviation ({note.text_simplicity_deviation}) * text simplicity deviation coeff ({config.text_simplicity_deviation}) = {note.text_simplicity_deviation * config.text_simplicity_deviation}\n"
            + f"clickbait ({note.clickbait}) * clickbait coeff ({config.clickbait_coeff}) = {note.clickbait * config.clickbait_coeff}\n"
            + f"subjective ({note.subjective}) * subjective coeff ({config.subjective_coeff}) = {note.subjective * config.subjective_coeff}\n"
            + f"confidence factor ({float(note.confidence_factor)}) * confidence factor coeff ({config.confidence_factor_coeff}) = {float(note.confidence_factor) * config.confidence_factor_coeff}\n"
            + f"triggered keywords ({note.triggered_keywords}) * triggered keywords coeff ({config.triggered_keywords_coeff}) = {note.triggered_keywords * config.triggered_keywords_coeff})\n"
            + f"сall to action ({note.call_to_action}) * сall to action coeff ({config.call_to_action_coeff}) = {note.call_to_action * config.call_to_action_coeff})\n"
            + f"repeated take ({note.repeated_take}) * repeated take ({config.repeated_take_coeff}) = {note.repeated_take * config.repeated_take_coeff})\n"
            + f"repeated note ({note.repeated_note}) * repated note ({config.repeated_note_coeff}) = {note.repeated_note * config.repeated_note_coeff})\n"
            + f"total score = {total_score}")

        calculation_object = {
            'sentimental_score': f"({round(note.sentimental_score, 3)}) * coeff ({round(config.sentimental_score_coeff, 3)}) = {round(note.sentimental_score * config.sentimental_score_coeff, 3)}",
            'triggered_topics': f"({round(note.triggered_topics, 3)}) * coeff ({round(config.triggered_topics_coeff, 3)}) = {round(note.triggered_topics * config.triggered_topics_coeff, 3)}",
            'text_simplicity_deviation': f"({round(note.text_simplicity_deviation, 3)}) * coeff ({round(config.text_simplicity_deviation, 3)}) = {round(note.text_simplicity_deviation * config.text_simplicity_deviation, 3)}",
            'clickbait': f"({round(note.clickbait, 3)}) * coeff ({round(config.clickbait_coeff, 3)}) = {round(note.clickbait * config.clickbait_coeff, 3)}",
            'subjective': f"({round(note.subjective, 3)}) * coeff ({round(config.subjective_coeff, 3)}) = {round(note.subjective * config.subjective_coeff, 3)}",
            'confidence_factor': f"({round(float(note.confidence_factor), 3)}) * coeff ({round(config.confidence_factor_coeff, 3)}) = {round(float(note.confidence_factor) * config.confidence_factor_coeff, 3)}",
            'triggered_keywords': f"({round(note.triggered_keywords, 3)}) * coeff ({round(config.triggered_keywords_coeff, 3)}) = {round(note.triggered_keywords * config.triggered_keywords_coeff, 3)}",
            'call_to_action': f"({round(note.call_to_action, 3)}) * coeff ({round(config.call_to_action_coeff, 3)}) = {round(note.call_to_action * config.call_to_action_coeff, 3)}",
            'repeated_take': f"({round(note.repeated_take, 3)}) * coeff ({round(config.repeated_take_coeff, 3)}) = {round(note.repeated_take * config.repeated_take_coeff, 3)}",
            'repeated_note': f"({round(note.repeated_note, 3)}) * coeff ({round(config.repeated_note_coeff, 3)}) = {round(note.repeated_note * config.repeated_note_coeff, 3)}",
            'total_score': f"{round(total_score, 3)}"
        }
        return total_score,calculation_object
