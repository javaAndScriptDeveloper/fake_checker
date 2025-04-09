from enums import FEHNER_TYPE
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


class FehnerProcessor:

   def __init__(self, note_dao):
       self.note_dao = note_dao

   def calculate_similarity_score(self, text):

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

   def process(self, text, note):

       cosine_similarity = self.calculate_similarity_score(text)
       note.cosine_similarity = float(cosine_similarity)
       last_note = self.note_dao.get_last_note()

       if not last_note:
           note.cosine_similarity_sum = note.cosine_similarity
           note.cosine_similarity_size = int(1)
           note.total_score_sum = note.total_score
           note.total_score_size = 1
           return

       note.cosine_similarity_sum = float(last_note.cosine_similarity_sum) + float(note.cosine_similarity)
       note.cosine_similarity_size = last_note.cosine_similarity_size + 1
       note.total_score_sum = float(last_note.total_score_sum) + float(note.total_score)
       note.total_score_size = last_note.total_score_size + 1

       average_cosine_similarity = float(note.cosine_similarity_sum) / float(note.cosine_similarity_size)
       cosine_similarity_deviation = float(note.cosine_similarity) - float(average_cosine_similarity)
       is_cosine_similarity_deviation_positive = cosine_similarity_deviation >= 0

       average_total_score_sum = float(note.total_score_sum) / float(note.total_score_size)
       total_score_deviation = float(note.total_score) - float(average_total_score_sum)
       is_total_score_deviation_positive = total_score_deviation >= 0

       if (is_cosine_similarity_deviation_positive and is_total_score_deviation_positive) or (not is_cosine_similarity_deviation_positive and is_total_score_deviation_positive):
           note.fehner_type = FEHNER_TYPE.A.name
       else:
           note.fehner_type = FEHNER_TYPE.B.name

   def calculate_fehner_score(self):

        notes = self.note_dao.get_notes()
        if not notes:
            return 0  # Avoid division by zero if no notes exist

            # Initialize the score counter
        score = 0

        # Iterate through all notes
        for note in notes:
            if note.fehner_type == 'A':  # Check the fehner_type
                score += 1

        # Calculate the Fechner Score
        fehner_score = score / len(notes)

        return fehner_score
