"""Repeated take (sentence) detection evaluator using cosine similarity."""
import time

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from config.config import config
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation, get_nlp


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

        for i in range(num_sentences):
            for j in range(i + 1, num_sentences):
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                if sim > config.similarity_threshold:
                    similar_sentences.add((i, j))

        return similar_sentences

    def evaluate(self, evaluation_context: EvaluationContext):
        start_time = time.perf_counter()

        text = evaluation_context.data
        doc = get_nlp()(text)
        sentences = [sent.text.strip() for sent in doc.sents]

        repeated_sentence_indices = self.find_repeated_sentences(sentences)

        evaluation_context.repeated_take_result = 1 if repeated_sentence_indices else 0
        evaluation_context.repeated_take_raw_result = evaluation_context.repeated_take_result

        end_time = time.perf_counter()
        evaluation_context.repeated_take_execution_time = end_time - start_time
