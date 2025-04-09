import json
import time
from abc import ABC, abstractmethod

import numpy as np
import spacy
import textstat
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from transformers import pipeline

from config.config import config
from dal.dal import NoteDao, Note
from processors.clickbait_title.clickbait_detector import is_clickbait

spacy.cli.download("en_core_web_sm")
nlp = spacy.load('en_core_web_sm')


class EvaluationContext:

    def __init__(self, data, source_id, note_dao):
        self.data = data
        self.title = None
        self.source_id = source_id
        self.note_dao = note_dao

        self.sentimental_analysis_result = 0
        self.sentimental_analysis_raw_result = None
        self.sentimental_analysis_coeff = 1.0
        self.sentimental_analysis_execution_time = 0

        self.trigger_keywords_result = 0
        self.trigger_keywords_raw_result = None
        self.trigger_keywords_coeff = 1.0
        self.trigger_keywords_execution_time = 0

        self.trigger_topics_result = 0
        self.trigger_topics_raw_result = None
        self.trigger_topics_coeff = 1.0
        self.trigger_topics_execution_time = 0

        self.clickbait_result = 0
        self.clickbait_raw_result = None
        self.clickbait_coeff = 1.0
        self.clickbait_execution_time = 0

        self.subjective_result = 0
        self.subjective_raw_result = None
        self.subjective_coeff = 1.0
        self.subjective_execution_time = 0

        self.text_simplicity_deviation = 0
        self.text_simplicity_deviation_raw_result = None
        self.text_simplicity_deviation_coeff = 1.0
        self.text_simplicity_deviation_execution_time = 0

        self.confidence_factor = 100
        self.confidence_factor_raw_result = None
        self.confidence_factor_coeff = 1.0
        self.confidence_factor_execution_time = 100

        self.call_to_action_result = 0
        self.call_to_action_raw_result = None
        self.call_to_action_coeff = 1.0
        self.call_to_action_execution_time = 0

        self.repeated_take_result = 0
        self.repeated_take_raw_result = None
        self.repeated_take_coeff = 1.0
        self.repeated_take_execution_time = 0

        self.repeated_note_result = 0
        self.repeated_note_raw_result = None
        self.repeated_note_coeff = 1.0
        self.repeated_note_execution_time = 0

        self.total_score = 0
        self.is_propaganda = False

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
        evaluation_context.sentimental_analysis_raw_result = evaluation_context.sentimental_analysis_result
        end_time = time.perf_counter()
        evaluation_context.sentimental_analysis_execution_time = end_time - start_time


class TriggerKeywords(Evaluation):

    def parse_config(self):
        with open('/home/vampir/lolitech/dissertation/config/trigger_keywords.json', 'r', encoding='utf-8') as file:
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

        return 1 if total_word_count > 1 else 0

    def evaluate(self, evaluation_context):
        trigger_keywords = self.parse_config()
        start_time = time.perf_counter()
        evaluation_context.trigger_keywords_result = self.count_and_divide(evaluation_context.data, trigger_keywords)
        evaluation_context.trigger_keywords_raw_result = evaluation_context.trigger_keywords_result
        end_time = time.perf_counter()
        evaluation_context.trigger_keywords_execution_time = end_time - start_time


class TriggerTopics(Evaluation):
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def parse_config(self):
        with open('/home/vampir/lolitech/dissertation/config/trigger_topics.json', 'r', encoding='utf-8') as file:
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

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        evaluation_context.trigger_topics_result = self.resolve_topics(evaluation_context.data)
        evaluation_context.trigger_topics_raw_result = evaluation_context.trigger_topics_result
        end_time = time.perf_counter()
        evaluation_context.trigger_topics_execution_time = end_time - start_time


class ClickBait(Evaluation):

    def evaluate(self, evaluation_context):
        if evaluation_context.title is None:
            evaluation_context.clickbait_result = 0
            return
        start_time = time.perf_counter()
        evaluation_context.clickbait_result = float(is_clickbait(evaluation_context.title)[0]) * 100
        evaluation_context.clickbait_raw_result = evaluation_context.clickbait_result
        end_time = time.perf_counter()
        evaluation_context.clickbait_execution_time = end_time - start_time


class Subjective(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        blob = TextBlob(evaluation_context.data)
        evaluation_context.subjective_result = blob.sentiment.subjectivity
        evaluation_context.subjective_raw_result = evaluation_context.subjective_result
        end_time = time.perf_counter()
        evaluation_context.subjective_execution_time = end_time - start_time


class TextSimplicity(Evaluation):

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        grade_level = textstat.flesch_reading_ease(evaluation_context.data)
        evaluation_context.text_simplicity_deviation = grade_level / 100
        evaluation_context.text_simplicity_deviation_raw_result = evaluation_context.text_simplicity_deviation
        end_time = time.perf_counter()
        evaluation_context.text_simplicity_deviation_execution_time = end_time - start_time


class ConfidenceFactor(Evaluation):

    def evaluate(self, evaluation_context):
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


class CallToAction(Evaluation):

    def parse_config(self):
        with open('/home/vampir/lolitech/dissertation/config/call_to_action_keywords.json', 'r', encoding='utf-8') as file:
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

            evaluation_context.call_to_action_result = cta_counts / total_sentences
        else:
            evaluation_context.call_to_action_result = 0

        evaluation_context.call_to_action_raw_result = evaluation_context.call_to_action_result
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
        evaluation_context.repeated_note_result = 1 if len(repeated_notes) > 0 else 0
        evaluation_context.repeated_note_raw_result = evaluation_context.repeated_note_result
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

        evaluation_context.repeated_take_result = len(repeated_sentence_indices) / len(sentences)
        evaluation_context.repeated_take_raw_result = evaluation_context.repeated_take_result

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

    def evaluate(self, title, data, source_id):
        context = EvaluationContext(data, source_id, self.note_dao)
        context.title = title
        for i in self.evaluations:
            i.evaluate(context)

        sentimental_score_coeff = recalculate_coefficient(Note.get_all_sentimental_scores)
        triggered_keywords_coeff = recalculate_coefficient(Note.get_all_triggered_keywords)
        triggered_topics_coeff = recalculate_coefficient(Note.get_all_triggered_topics)
        text_simplicity_deviation_coeff = recalculate_coefficient(Note.get_all_text_simplicity_deviations)
        confidence_factor_coeff = recalculate_coefficient(Note.get_all_confidence_factors)
        clickbait_coeff = recalculate_coefficient(Note.get_all_clickbait_scores)
        subjective_coeff = recalculate_coefficient(Note.get_all_subjectivity_scores)
        call_to_action_coeff = recalculate_coefficient(Note.get_all_call_to_action_scores)
        repeated_take_coeff = recalculate_coefficient(Note.get_all_repeated_takes)
        repeated_note_coeff = recalculate_coefficient(Note.get_all_repeated_notes)

        coeffs_sum = sentimental_score_coeff \
                    + triggered_keywords_coeff \
                     + triggered_topics_coeff \
                     + text_simplicity_deviation_coeff \
                     + confidence_factor_coeff \
                     + clickbait_coeff \
                     + subjective_coeff \
                     + call_to_action_coeff \
                     + repeated_take_coeff \
                     + repeated_note_coeff

        # normalization
        sentimental_score_coeff = sentimental_score_coeff / coeffs_sum
        context.sentimental_analysis_coeff = sentimental_score_coeff

        triggered_keywords_coeff = triggered_keywords_coeff / coeffs_sum
        context.trigger_keywords_coeff = triggered_keywords_coeff

        triggered_topics_coeff = triggered_topics_coeff / coeffs_sum
        context.trigger_topics_coeff = triggered_topics_coeff

        text_simplicity_deviation_coeff = text_simplicity_deviation_coeff / coeffs_sum
        context.text_simplicity_deviation_coeff = text_simplicity_deviation_coeff

        confidence_factor_coeff = confidence_factor_coeff / coeffs_sum
        context.confidence_factor_coeff = confidence_factor_coeff

        clickbait_coeff = clickbait_coeff / coeffs_sum
        context.clickbait_coeff = clickbait_coeff

        subjective_coeff = subjective_coeff / coeffs_sum
        context.subjective_coeff = subjective_coeff

        call_to_action_coeff = call_to_action_coeff / coeffs_sum
        context.call_to_action_coeff = call_to_action_coeff

        repeated_take_coeff = repeated_take_coeff / coeffs_sum
        context.repeated_take_coeff = repeated_take_coeff

        repeated_note_coeff = repeated_note_coeff / coeffs_sum
        context.repeated_note_coeff = repeated_note_coeff

        context.sentimental_analysis_result = context.sentimental_analysis_result * sentimental_score_coeff
        context.trigger_keywords_result = context.trigger_keywords_result * triggered_keywords_coeff
        context.trigger_topics_result = context.trigger_topics_result * triggered_topics_coeff
        context.text_simplicity_deviation = context.text_simplicity_deviation * text_simplicity_deviation_coeff
        context.clickbait_result = context.clickbait_result * clickbait_coeff
        context.subjective_result = context.subjective_result * subjective_coeff
        context.call_to_action_result = context.call_to_action_result * call_to_action_coeff
        context.repeated_take_result = context.repeated_take_result * repeated_take_coeff
        context.repeated_note_result = context.repeated_note_result * repeated_note_coeff
        context.confidence_factor = float(context.confidence_factor) * confidence_factor_coeff

        context.total_score = float(context.sentimental_analysis_result \
                      + context.trigger_keywords_result \
                      + context.trigger_topics_result \
                      + context.text_simplicity_deviation \
                      + context.clickbait_result \
                      + context.subjective_result \
                      + context.call_to_action_result \
                      + context.repeated_take_result \
                      + context.repeated_note_result \
                      + context.confidence_factor)
        #context.is_propaganda = context.total_score > self.note_dao.get_upper_third_rating()
        context.is_propaganda = context.total_score > 0.3
        return context

def recalculate_coefficient(get_all_scores):
    all_scores = get_all_scores()
    if len(all_scores) == 0:
        return 1
    scores_sum = 0
    for score in all_scores:
        scores_sum += score
    average = scores_sum / len(all_scores)
    threshold_counter = 0
    for score in all_scores:
        if score >= average:
            threshold_counter += 1
    return threshold_counter / len(all_scores)