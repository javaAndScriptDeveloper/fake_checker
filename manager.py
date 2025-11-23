import csv
import hashlib
import json
import os
from datetime import datetime

from dal.dal import Note, NoteDao, SourceDao
from processors.evaluation_processor import EvaluationContext, EvaluationProcessor
from processors.fehner_processor import FehnerProcessor
from translation import Translator


class Manager:

    def __init__(self,
                 evaluation_processor: EvaluationProcessor,
                 note_dao: NoteDao,
                 source_dao: SourceDao,
                 fehner_processor: FehnerProcessor,
                 translator: Translator,
                 neo4j_service=None):
        self.evaluation_processor = evaluation_processor
        self.note_dao = note_dao
        self.source_dao = source_dao
        self.fehner_processor = fehner_processor
        self.translator = translator
        self.neo4j_service = neo4j_service

        self.coldstart("/home/vampir/lolitech/study/science/code/data/coldstart")
        #self.process_initial("/home/vampir/lolitech/dissertation/data/initial")

    def coldstart(self, path_to_coldstart_files):
        for filename in os.listdir(path_to_coldstart_files):
            file_path = os.path.join(path_to_coldstart_files, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.process(data.get('title'), data.get('content'), data.get('source_id'), data.get('language'))

                    print(f"Processed coldstart file: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    def process_initial(self, path_to_pre_saved):
        for filename in os.listdir(path_to_pre_saved):
            file_path = os.path.join(path_to_pre_saved, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.process(data.get('title'), data.get('content'), data.get('source_id'), data.get('language'))

                    print(f"Processed initial file: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    def process(self, title,  text, source_id, language):
        hash = self._resolve_text_hash(text)
        text_by_hash = self.note_dao.get_by_hash(hash)
        if text_by_hash is not None:
            print(f"Skipped processing already processed text: {text[:16]}...")
            return text_by_hash
        if (language != "english"):
            title = self.translator.translate_to_english(title, language)
            text = self.translator.translate_to_english(text, language)
        evaluation_context = self.evaluation_processor.evaluate(title, text, source_id)
        note = Note()
        note = self._mapEvaluationContext(evaluation_context, note)
        self.fehner_processor.process(text, note)
        note.hash = hash
        self.note_dao.save(note)
        
        # Post-processing: Save to Neo4j
        if self.neo4j_service and note.id:
            try:
                source = self.source_dao.get_by_id(source_id)
                if source:
                    self.neo4j_service.save_note(note, source, title)
                else:
                    print(f"⚠️ Warning: Source with ID {source_id} not found, skipping Neo4j save")
            except Exception as e:
                print(f"⚠️ Warning: Failed to save to Neo4j: {e}")
        
        return note

    def _resolve_text_hash(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _mapEvaluationContext(self, evaluationContext: EvaluationContext, note: Note):
        note.content = evaluationContext.data
        note.source_id = evaluationContext.source_id

        note.sentimental_score = evaluationContext.sentimental_analysis_result
        note.sentimental_score_raw = evaluationContext.sentimental_analysis_raw_result
        note.sentimental_score_coeff = evaluationContext.sentimental_analysis_coeff

        note.triggered_keywords = evaluationContext.trigger_keywords_result
        note.triggered_keywords_raw = evaluationContext.trigger_keywords_raw_result
        note.triggered_keywords_coeff = evaluationContext.trigger_keywords_coeff

        note.text_simplicity_deviation = evaluationContext.text_simplicity_deviation
        note.text_simplicity_deviation_raw = evaluationContext.text_simplicity_deviation_raw_result
        note.text_simplicity_deviation_coeff = evaluationContext.text_simplicity_deviation_coeff

        note.confidence_factor = evaluationContext.confidence_factor
        note.confidence_factor_raw = evaluationContext.confidence_factor_raw_result
        note.confidence_factor_coeff = evaluationContext.confidence_factor_coeff

        note.triggered_topics = evaluationContext.trigger_topics_result
        note.triggered_topics_raw = evaluationContext.trigger_topics_raw_result
        note.triggered_topics_coeff = evaluationContext.trigger_topics_coeff

        note.clickbait = evaluationContext.clickbait_result
        note.clickbait_raw = evaluationContext.clickbait_raw_result
        note.clickbait_coeff = evaluationContext.clickbait_coeff

        note.subjective = evaluationContext.subjective_result
        note.subjective_raw = evaluationContext.subjective_raw_result
        note.subjective_coeff = evaluationContext.subjective_coeff

        note.call_to_action = evaluationContext.call_to_action_result
        note.call_to_action_raw = evaluationContext.call_to_action_raw_result
        note.call_to_action_coeff = evaluationContext.call_to_action_coeff

        note.repeated_take = evaluationContext.repeated_take_result
        note.repeated_take_raw = evaluationContext.repeated_take_raw_result
        note.repeated_take_coeff = evaluationContext.repeated_take_coeff

        note.repeated_note = evaluationContext.repeated_note_result
        note.repeated_note_raw = evaluationContext.repeated_note_raw_result
        note.repeated_note_coeff = evaluationContext.repeated_note_coeff

        note.messianism = evaluationContext.messianism
        note.messianism_raw = evaluationContext.messianism_raw_result
        note.messianism_coeff = evaluationContext.messianism_coeff

        note.generalization_of_opponents = evaluationContext.generalization_of_opponents
        note.generalization_of_opponents_raw = evaluationContext.generalization_of_opponents_raw_result
        note.generalization_of_opponents_coeff = evaluationContext.generalization_of_opponents_coeff

        note.opposition_to_opponents = evaluationContext.opposition_to_opponents
        note.opposition_to_opponents_raw = evaluationContext.opposition_to_opponents_raw_result
        note.opposition_to_opponents_coeff = evaluationContext.opposition_to_opponents_coeff

        note.total_score = evaluationContext.total_score
        note.is_propaganda = evaluationContext.is_propaganda
        note.reason = evaluationContext.chatgpt_reason
        note.amount_of_propaganda_scores = evaluationContext.amount_of_propaganda_scores
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

    def get_available_translations(self):
        return self.translator.supported_translations_list

    def export_results_to_csv(self, data, file_path=None):
        if not file_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f"propaganda_results_{timestamp}.csv"

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow(row)
        print(f"CSV exported to {file_path}")
