import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def calculate_similarity_score(text):
    """
    Calculates the similarity score for a given text by splitting it into sentences.

    Args:
        text (str): The input text to be analyzed.

    Returns:
        float: The positive normalized similarity score (average similarity).
    """
    # Step 1: Split text into sentences using regex
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # Step 2: Preprocess text using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vectorizer.fit_transform(sentences)

    # Step 3: Compute cosine similarity matrix
    cosine_sim_matrix = cosine_similarity(X)

    # Step 4: Calculate total similarity score (excluding diagonal)
    n = cosine_sim_matrix.shape[0]
    total_similarity_score = np.sum(cosine_sim_matrix) - n  # Subtract diagonal (self-similarity)

    # Step 5: Normalize the score
    if n > 1:
        max_possible_score = n * (n - 1)  # Total number of off-diagonal pairs
        normalized_score = total_similarity_score / max_possible_score
    else:
        normalized_score = 0.0  # No meaningful similarity for a single sentence

    # Ensure the score is positive
    return max(0, normalized_score)

text_input = """
Mathematics is a field of study that discovers and organizes methods,
theories and theorems that are developed and proved for the needs of empirical sciences and mathematics itself.
There are many areas of mathematics,
which include number theory (the study of numbers), algebra (the study of formulas and related structures),
geometry (the study of shapes and spaces that contain them), analysis (the study of continuous changes),
and set theory (presently used as a foundation for all mathematics).
Mathematics is a field of study that discovers and organizes methods,
theories and theorems that are developed and proved for the needs of empirical sciences and mathematics itself.
There are many areas of mathematics,
"""

normalized_score = calculate_similarity_score(text_input)
print(f"Normalized Total Similarity Score (average similarity): {normalized_score:.4f}")
