from clusterization_sample import calculate_similarity_score
from core.enums import FEHNER_TYPE


class FehnerProcessor:

   def __init__(self, note_dao):
       self.note_dao = note_dao

   def process(self, note, text):

       cosine_similarity = calculate_similarity_score(text)
       note.cosine_similarity = cosine_similarity
       last_note = self.note_dao.get_last_note()

       if not last_note:
           note.cosine_similarity_sum = note.cosine_similarity
           note.cosine_similarity_size = 1
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
