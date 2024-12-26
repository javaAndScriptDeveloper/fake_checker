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
The media will not show the magnitude of this crowd. Even I, when I turned on today, I looked, and I saw thousands of people here, but you don't see hundreds of thousands of people behind you because they don't want to show that. We have hundreds of thousands of people here, and I just want them to be recognized by the fake news media. Turn your cameras please and show what's really happening out here because these people are not going to take it any longer. They're not going to take it any longer. Go ahead. Turn your cameras, please. Would you show? They came from all over the world, actually, but they came from all over our country. I just really want to see what they do. I just want to see how they covered. I've never seen anything like it.
"""

normalized_score = calculate_similarity_score(text_input)
print(f"Normalized Total Similarity Score (average similarity): {normalized_score:.4f}")
