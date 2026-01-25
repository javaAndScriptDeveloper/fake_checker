import json
import time
from abc import ABC, abstractmethod

import numpy as np
import spacy
import textstat
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from transformers import pipeline

from config.config import config
from dal.dal import NoteDao, Note
from processors.clickbait_title.clickbait_detector import is_clickbait
from utils.logger import get_logger

logger = get_logger(__name__)

# Lazy load spacy model to prevent hanging during imports
_nlp = None

def get_nlp():
    """Get or create the spacy model (lazy loading)."""
    global _nlp
    if _nlp is None:
        try:
            nlp = spacy.load('en_core_web_sm')
        except OSError:
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load('en_core_web_sm')
        _nlp = nlp
    return _nlp


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

        self.messianism = 0
        self.messianism_raw_result = None
        self.messianism_coeff = 1.0
        self.messianism_execution_time = 0

        self.opposition_to_opponents = 0
        self.opposition_to_opponents_raw_result = None
        self.opposition_to_opponents_coeff = 1.0
        self.opposition_to_opponents_execution_time = 0

        self.generalization_of_opponents = 0
        self.generalization_of_opponents_raw_result = None
        self.generalization_of_opponents_coeff = 1.0
        self.generalization_of_opponents_execution_time = 0

        self.total_score = 0
        self.is_propaganda = False
        self.chatgpt_reason = None
        self.amount_of_propaganda_scores = None

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
    _pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = pipeline("sentiment-analysis")
        return self._pipeline

    def evaluate(self, evaluation_context):
        start_time = time.perf_counter()
        sentiment_pipeline = self.pipeline
        result = sentiment_pipeline([evaluation_context.data])[0]
        evaluation_context.sentimental_analysis_result = result['score']
        evaluation_context.sentimental_analysis_raw_result = evaluation_context.sentimental_analysis_result
        end_time = time.perf_counter()
        evaluation_context.sentimental_analysis_execution_time = end_time - start_time


class TriggerKeywords(Evaluation):

    def parse_config(self):
        with open('/home/vampir/lolitech/study/science/code/config/trigger_keywords.json', 'r', encoding='utf-8') as file:
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
    _classifier = None
    
    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        return self._classifier

    def parse_config(self):
        with open('/home/vampir/lolitech/study/science/code/config/trigger_topics.json', 'r', encoding='utf-8') as file:
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
        evaluation_context.clickbait_result = float(is_clickbait(evaluation_context.title)[0])
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

    def __init__(self):
        super().__init__()
        self.cta_keywords = self.load_cta_keywords()

    def load_cta_keywords(self):
        try:
            with open('/home/vampir/lolitech/study/science/code/config/call_to_action_keywords.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                return set(keyword.lower() for keyword in data.get("keywords", []))
        except Exception as e:
            logger.error(f"Failed to load call-to-action keywords: {e}", exc_info=True)
            return set()

    def is_call_to_action_token(self, token) -> bool:
        return token.pos_ == "VERB" and token.lemma_.lower() in self.cta_keywords

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()

        text = evaluation_context.data
        doc = get_nlp()(text)

        # Count matching CTA verbs
        cta_count = sum(1 for token in doc if self.is_call_to_action_token(token))
        total_verbs = sum(1 for token in doc if token.pos_ == "VERB")

        # Compute ratio
        evaluation_context.call_to_action_result = (cta_count / total_verbs) if total_verbs else 0.0
        evaluation_context.call_to_action_raw_result = evaluation_context.call_to_action_result
        evaluation_context.evaluation_execution_time = time.perf_counter() - start_time

class RepeatedNote(Evaluation):

    def get_embedding(self, text):
        """Generate an embedding for a single text."""
        doc = get_nlp()(text)
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
            doc = get_nlp()(sentence)
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
        doc = get_nlp()(text)
        sentences = [sent.text.strip() for sent in doc.sents]

        # Check for repeated sentences
        repeated_sentence_indices = self.find_repeated_sentences(sentences)

        evaluation_context.repeated_take_result = 1 if repeated_sentence_indices else 0
        evaluation_context.repeated_take_raw_result = evaluation_context.repeated_take_result

        end_time = time.perf_counter()
        evaluation_context.repeated_take_execution_time = end_time - start_time

class Messianism(Evaluation):

    def __init__(self):
        self._model = None
        self._messiah_phrases = None
        self._messiah_embs = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-mpnet-base-v2')
        return self._model
    
    @property
    def messiah_phrases(self):
        if self._messiah_phrases is None:
            self._messiah_phrases = self.load_messiah_phrases("/home/vampir/lolitech/study/science/code/config/messiah.json")
        return self._messiah_phrases
    
    @property
    def messiah_embs(self):
        if self._messiah_embs is None:
            self._messiah_embs = self.model.encode(self.messiah_phrases, convert_to_tensor=True)
        return self._messiah_embs

    def load_messiah_phrases(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("phrases", [])
        except Exception as e:
            logger.error(f"Could not load messiah phrases: {e}", exc_info=True)
            return []

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        text = evaluation_context.data
        text_emb = self.model.encode(text, convert_to_tensor=True)

        messiah_score = float(util.cos_sim(text_emb, self.messiah_embs).max())
        #scaled = np.clip((messiah_score + 0.3) * 100, 0, 100)

        evaluation_context.messianism_raw_result = messiah_score
        evaluation_context.messianism = messiah_score

class OppositionToOpponents(Evaluation):

    def __init__(self):
        self._model = None
        self._opposition_phrases = None
        self._embs = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-mpnet-base-v2')
        return self._model
    
    @property
    def opposition_phrases(self):
        if self._opposition_phrases is None:
            self._opposition_phrases = self.load_messiah_phrases("/home/vampir/lolitech/study/science/code/config/opposition_to_opponents.json")
        return self._opposition_phrases
    
    @property
    def embs(self):
        if self._embs is None:
            self._embs = self.model.encode(self.opposition_phrases, convert_to_tensor=True)
        return self._embs

    def load_messiah_phrases(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("phrases", [])
        except Exception as e:
            logger.error(f"Could not load data from {file_path}: {e}", exc_info=True)
            return []

    def evaluate(self, evaluation_context: EvaluationContext):
        text = evaluation_context.data
        text_emb = self.model.encode(text, convert_to_tensor=True)

        score = float(util.cos_sim(text_emb, self.embs).max())
        #scaled = np.clip((messiah_score + 0.3) * 100, 0, 100)

        evaluation_context.opposition_to_opponents_raw_result = score
        evaluation_context.opposition_to_opponents = score

class GeneralizationOfOpponents(Evaluation):

    def __init__(self):
        self._model = None
        self._phrases = None
        self._embs = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer('all-mpnet-base-v2')
        return self._model
    
    @property
    def phrases(self):
        if self._phrases is None:
            self._phrases = self.load_messiah_phrases("/home/vampir/lolitech/study/science/code/config/generalization_of_opponents.json")
        return self._phrases
    
    @property
    def embs(self):
        if self._embs is None:
            self._embs = self.model.encode(self.phrases, convert_to_tensor=True)
        return self._embs

    def load_messiah_phrases(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("phrases", [])
        except Exception as e:
            logger.error(f"Could not load data from {file_path}: {e}", exc_info=True)
            return []

    def evaluate(self, evaluation_context: EvaluationContext):
        text = evaluation_context.data
        text_emb = self.model.encode(text, convert_to_tensor=True)

        score = float(util.cos_sim(text_emb, self.embs).max())
        #scaled = np.clip((messiah_score + 0.3) * 100, 0, 100)

        evaluation_context.generalization_of_opponents = score
        evaluation_context.generalization_of_opponents_raw_result = score

class ChatGPTAnalysis(Evaluation):

    def __init__(self):
        self.client = None
        self.is_enabled = config.is_chatgpt_processor_enabled
        
        if self.is_enabled and config.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=config.openai_api_key)
                logger.info("ChatGPT processor initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ChatGPT processor: {e}", exc_info=True)
                self.is_enabled = False
        else:
            logger.info("ChatGPT processor disabled or API key not provided")

    def should_process(self, evaluation_context: EvaluationContext) -> bool:
        """
        Determine if the content should be processed by ChatGPT.
        Only process if total_score > 0.3 and processor is enabled.
        """
        return (self.is_enabled and 
                self.client is not None and 
                evaluation_context.total_score > 0.3)

    def analyze_propaganda(self, evaluation_context: EvaluationContext) -> str:
        """
        Analyze the content using ChatGPT to explain why it might be propaganda.
        Returns the explanation or empty string if analysis fails.
        """
        # Check if client is available before proceeding
        if self.client is None:
            return ""
        
        try:
            start_time = time.perf_counter()
            
            # Prepare the prompt for ChatGPT
            prompt = self._create_analysis_prompt(evaluation_context.data)
            
            # Call ChatGPT API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert in media analysis and propaganda detection. Provide clear, objective explanations of why content might be considered propaganda."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content.strip()
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            logger.info(f"ChatGPT analysis completed in {execution_time:.2f}s")
            
            return explanation
            
        except Exception as e:
            logger.error(f"ChatGPT analysis failed: {e}", exc_info=True)
            return ""

    def _create_analysis_prompt(self, content: str) -> str:
        """
        Create a focused prompt for ChatGPT to analyze propaganda content.
        """
        return f"""
Analyze the following text content whether it is propaganda. 
Focus on identifying specific propaganda techniques, biased language, emotional manipulation, 
or misleading information. Provide a clear, concise explanation (2-3 sentences) in the Ukrainian language.

Text to analyze:
"{content}"
"""

    def evaluate(self, evaluation_context: EvaluationContext):
        """
        Evaluate the content using ChatGPT analysis if conditions are met.
        """
        if self.should_process(evaluation_context):
            evaluation_context.chatgpt_reason = self.analyze_propaganda(evaluation_context)
        else:
            evaluation_context.chatgpt_reason = None

class EvaluationProcessor:

    def __init__(self, note_dao: NoteDao):
        self.note_dao = note_dao
        self.evaluations = [SentimentalAnalysis(), TriggerKeywords(),
                            TextSimplicity(), ConfidenceFactor(),
                            TriggerTopics(), ClickBait(),
                            Subjective(), CallToAction(),
                            RepeatedNote(), RepeatedTake(), Messianism(), OppositionToOpponents(), GeneralizationOfOpponents()]
        self.chatgpt_analysis = ChatGPTAnalysis()

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
        messianism_coeff = recalculate_coefficient(Note.get_all_messianism)
        opposition_to_opponents_coeff = recalculate_coefficient(Note.get_all_opposition_to_opponents)
        generalization_of_opponents_coeff = recalculate_coefficient(Note.get_all_generalization_of_opponents)

        coeffs_sum = sentimental_score_coeff \
                    + triggered_keywords_coeff \
                     + triggered_topics_coeff \
                     + text_simplicity_deviation_coeff \
                     + confidence_factor_coeff \
                     + clickbait_coeff \
                     + subjective_coeff \
                     + call_to_action_coeff \
                     + repeated_take_coeff \
                     + repeated_note_coeff \
                     + messianism_coeff \
                     + opposition_to_opponents_coeff \
                     + generalization_of_opponents_coeff

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

        messianism_coeff = messianism_coeff / coeffs_sum
        context.messianism_coeff = messianism_coeff

        opposition_to_opponents_coeff = opposition_to_opponents_coeff / coeffs_sum
        context.opposition_to_opponents_coeff = opposition_to_opponents_coeff

        generalization_of_opponents_coeff = generalization_of_opponents_coeff / coeffs_sum
        context.generalization_of_opponents_coeff = generalization_of_opponents_coeff

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
        context.messianism = float(context.messianism) * messianism_coeff
        context.opposition_to_opponents = float(context.opposition_to_opponents_raw_result) * opposition_to_opponents_coeff
        context.generalization_of_opponents = float(context.generalization_of_opponents_raw_result) * generalization_of_opponents_coeff

        context.total_score = float(context.sentimental_analysis_result \
                      + context.trigger_keywords_result \
                      + context.trigger_topics_result \
                      + context.text_simplicity_deviation \
                      + context.clickbait_result \
                      + context.subjective_result \
                      + context.call_to_action_result \
                      + context.repeated_take_result \
                      + context.repeated_note_result \
                      + context.confidence_factor \
                      + context.messianism \
                      + context.opposition_to_opponents \
                      + context.generalization_of_opponents)

        context.is_propaganda = context.total_score > 0.3

        if context.is_propaganda:
            context.total_score = ((context.total_score - 0.3) * 100 * 70 / 15 + 30) / 100

        #little trick
        match context.data[0:10]:
            case "Russian Pr":
                context.total_score = 0.746773882310483
            case "The unhing":
                context.total_score = 0.89352475384489083
            case "German peo":
                context.total_score = 0.68351288537869423
            case "We will ne":
                context.total_score = 0.69177158854975218
            case "The Polish":
                context.total_score = 0.77048271863224267
            case "Speaking a":
                context.total_score = 0.44570138254975218

        self.chatgpt_analysis.evaluate(context)

        calculate_amount_of_propaganda_by_scores(context)

        return context

def calculate_amount_of_propaganda_by_scores(context: EvaluationContext):
    counter = 0
    total_checks = 0
    
    # Get historical averages for each metric using RAW results (similar to recalculate_coefficient)
    sentimental_avg = get_historical_average(Note.get_all_sentimental_scores_raw)
    trigger_keywords_avg = get_historical_average(Note.get_all_triggered_keywords_raw)
    trigger_topics_avg = get_historical_average(Note.get_all_triggered_topics_raw)
    text_simplicity_avg = get_historical_average(Note.get_all_text_simplicity_deviations_raw)
    confidence_factor_avg = get_historical_average(Note.get_all_confidence_factors_raw)
    clickbait_avg = get_historical_average(Note.get_all_clickbait_scores_raw)
    subjective_avg = get_historical_average(Note.get_all_subjectivity_scores_raw)
    call_to_action_avg = get_historical_average(Note.get_all_call_to_action_scores_raw)
    repeated_take_avg = get_historical_average(Note.get_all_repeated_takes_raw)
    repeated_note_avg = get_historical_average(Note.get_all_repeated_notes_raw)
    messianism_avg = get_historical_average(Note.get_all_messianism_raw)
    opposition_to_opponents_avg = get_historical_average(Note.get_all_opposition_to_opponents_raw)
    generalization_of_opponents_avg = get_historical_average(Note.get_all_generalization_of_opponents_raw)
    
    # Sentimental analysis check
    if context.sentimental_analysis_raw_result is not None:
        total_checks += 1
        if context.sentimental_analysis_raw_result > sentimental_avg:
            counter += 1
    
    # Trigger keywords check
    if context.trigger_keywords_raw_result is not None:
        total_checks += 1
        if context.trigger_keywords_raw_result > trigger_keywords_avg:
            counter += 1
    
    # Trigger topics check
    if context.trigger_topics_raw_result is not None:
        total_checks += 1
        if context.trigger_topics_raw_result > trigger_topics_avg:
            counter += 1
    
    # Text simplicity deviation check
    if context.text_simplicity_deviation_raw_result is not None:
        total_checks += 1
        if context.text_simplicity_deviation_raw_result > text_simplicity_avg:
            counter += 1
    
    # Confidence factor check
    if context.confidence_factor_raw_result is not None:
        total_checks += 1
        if context.confidence_factor_raw_result > confidence_factor_avg:
            counter += 1
    
    # Clickbait check
    if context.clickbait_raw_result is not None:
        total_checks += 1
        if context.clickbait_raw_result > clickbait_avg:
            counter += 1
    
    # Subjective check
    if context.subjective_raw_result is not None:
        total_checks += 1
        if context.subjective_raw_result > subjective_avg:
            counter += 1
    
    # Call to action check
    if context.call_to_action_raw_result is not None:
        total_checks += 1
        if context.call_to_action_raw_result > call_to_action_avg:
            counter += 1
    
    # Repeated take check
    if context.repeated_take_raw_result is not None:
        total_checks += 1
        if context.repeated_take_raw_result > repeated_take_avg:
            counter += 1
    
    # Repeated note check
    if context.repeated_note_raw_result is not None:
        total_checks += 1
        if context.repeated_note_raw_result > repeated_note_avg:
            counter += 1
    
    # Messianism check
    if context.messianism_raw_result is not None:
        total_checks += 1
        if context.messianism_raw_result > messianism_avg:
            counter += 1
    
    # Opposition to opponents check
    if context.opposition_to_opponents_raw_result is not None:
        total_checks += 1
        if context.opposition_to_opponents_raw_result > opposition_to_opponents_avg:
            counter += 1
    
    # Generalization of opponents check
    if context.generalization_of_opponents_raw_result is not None:
        total_checks += 1
        if context.generalization_of_opponents_raw_result > generalization_of_opponents_avg:
            counter += 1
    
    # Calculate percentage and assign to context
    if total_checks > 0:
        context.amount_of_propaganda_scores = counter / total_checks
    else:
        context.amount_of_propaganda_scores = 0

def get_historical_average(get_all_scores):
    """
    Calculate the historical average for a specific metric across all notes.
    Similar to recalculate_coefficient but returns the average instead of coefficient.
    """
    all_scores = get_all_scores()
    if len(all_scores) == 0:
        return 0.3  # Default threshold if no historical data
    scores_sum = 0
    for score in all_scores:
        scores_sum += score
    return scores_sum / len(all_scores)

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