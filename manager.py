import json
import os

from dal.dal import Note, NoteDao, SourceDao
from processors.evaluation_processor import EvaluationContext, EvaluationProcessor
from processors.fehner_processor import FehnerProcessor

class Manager:

    def __init__(self,
                 evaluation_processor: EvaluationProcessor,
                 note_dao: NoteDao,
                 source_dao: SourceDao,
                 fehner_processor: FehnerProcessor):
        self.evaluation_processor = evaluation_processor
        self.note_dao = note_dao
        self.source_dao = source_dao
        self.fehner_processor = fehner_processor

        self.coldstart("/home/vampir/lolitech/dissertation/data/coldstart")

    def coldstart(self, path_to_coldstart_files):
        for filename in os.listdir(path_to_coldstart_files):
            file_path = os.path.join(path_to_coldstart_files, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.process(data.get('content'), data.get('source_id'))

                    print(f"Processed coldstart file: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    def process(self, text, source_id):
        evaluation_context = self.evaluation_processor.evaluate(text, source_id)
        note = Note()
        note = self._mapEvaluationContext(evaluation_context, note)
        self.fehner_processor.process(text, note)
        self.note_dao.save(note)
        return note

    def _mapEvaluationContext(self, evaluationContext: EvaluationContext, note: Note):
        note.content = evaluationContext.data
        note.source_id = evaluationContext.source_id
        note.sentimental_score = evaluationContext.sentimental_analysis_result
        note.triggered_keywords = evaluationContext.trigger_keywords_result
        note.text_simplicity_deviation = evaluationContext.text_simplicity_deviation
        note.confidence_factor = evaluationContext.confidence_factor
        note.triggered_topics = evaluationContext.trigger_topics_result
        note.clickbait = evaluationContext.clickbait_result
        note.subjective = evaluationContext.subjective_result
        note.call_to_action = evaluationContext.call_to_action_result
        note.repeated_take = evaluationContext.repeated_take_result
        note.repeated_note = evaluationContext.repeated_note_result
        note.total_score = evaluationContext.total_score
        note.is_propaganda = evaluationContext.is_propaganda
        return note

    def get_visible_sources(self):
        sources = self.source_dao.get_all()
        return [source for source in sources if not source.is_hidden]

    def get_sources_with_ratings(self):
        sources = self.source_dao.get_all()
        source_ratings = {}
        for i in sources:
            if not i.is_hidden:
                notes = self.note_dao.get_by_source_id(i.id)
                if notes:
                    total_scores = [note.total_score for note in notes]
                    rating = sum(total_scores) / len(total_scores)
                    source_ratings[i] = rating
        return source_ratings

    def calculate_fehner_score(self):
        return self.fehner_processor.calculate_fehner_score()
