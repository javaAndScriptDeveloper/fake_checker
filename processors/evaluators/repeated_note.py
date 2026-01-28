"""Repeated note detection evaluator using cosine similarity."""
import time

from sklearn.metrics.pairwise import cosine_similarity

from config.config import config
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation, get_nlp


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

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()
        notes_from_source = evaluation_context.note_dao.get_by_source_id(evaluation_context.source_id)
        repeated_notes = self.check_similarity(evaluation_context.data, [note.content for note in notes_from_source])
        evaluation_context.repeated_note_result = 1 if len(repeated_notes) > 0 else 0
        evaluation_context.repeated_note_raw_result = evaluation_context.repeated_note_result
        end_time = time.perf_counter()
        evaluation_context.confidence_factor_execution_time = end_time - start_time
