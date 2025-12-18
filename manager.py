import csv
import hashlib
import json
import os
import time
from datetime import datetime

from dal.dal import Note, NoteDao, SourceDao
from processors.evaluation_processor import EvaluationContext, EvaluationProcessor
from processors.fehner_processor import FehnerProcessor
from translation import Translator
from utils.logger import get_logger

logger = get_logger(__name__)


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
                start_time = time.perf_counter()
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = data.get('content', '')
                    title = data.get('title', '')
                    word_count = self._count_words(content)
                    self.process(title, content, data.get('source_id'), data.get('language'), data.get('repostedFrom'))
                
                elapsed_time = time.perf_counter() - start_time
                time_str = self._format_processing_time(elapsed_time)
                speed = word_count / elapsed_time if elapsed_time > 0 else 0
                self._print_processing_metadata(filename, word_count, elapsed_time, speed)
                logger.info(f"Processed coldstart file: {filename} (took {time_str})")
            except Exception as e:
                logger.error(f"Error reading coldstart file {filename}: {e}", exc_info=True)

    def process_initial(self, path_to_pre_saved):
        for filename in os.listdir(path_to_pre_saved):
            file_path = os.path.join(path_to_pre_saved, filename)
            try:
                start_time = time.perf_counter()
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = data.get('content', '')
                    title = data.get('title', '')
                    word_count = self._count_words(content)
                    self.process(title, content, data.get('source_id'), data.get('language'), data.get('repostedFrom'))
                
                elapsed_time = time.perf_counter() - start_time
                time_str = self._format_processing_time(elapsed_time)
                speed = word_count / elapsed_time if elapsed_time > 0 else 0
                self._print_processing_metadata(filename, word_count, elapsed_time, speed)
                logger.info(f"Processed initial file: {filename} (took {time_str})")
            except Exception as e:
                logger.error(f"Error reading initial file {filename}: {e}", exc_info=True)

    def process(self, title,  text, source_id, language, reposted_from_source_id=None):
        hash = self._resolve_text_hash(text)
        text_by_hash = self.note_dao.get_by_hash(hash)
        if text_by_hash is not None:
            logger.debug(f"Skipped processing already processed text: {text[:16]}...")
            return text_by_hash
        if (language != "english"):
            title = self.translator.translate_to_english(title, language)
            text = self.translator.translate_to_english(text, language)
        evaluation_context = self.evaluation_processor.evaluate(title, text, source_id)
        note = Note()
        note = self._mapEvaluationContext(evaluation_context, note)
        self.fehner_processor.process(text, note)
        note.hash = hash
        
        # Handle repost relationship: link directly to source
        if reposted_from_source_id is not None:
            note.reposted_from_source_id = reposted_from_source_id
        
        self.note_dao.save(note)
        
        # Post-processing: Save to Neo4j
        if self.neo4j_service and note.id:
            try:
                source = self.source_dao.get_by_id(source_id)
                if source:
                    self.neo4j_service.save_note(note, source, title)
                    if note.reposted_from_source_id:
                        logger.info(f"Note {note.id} reposts from source {note.reposted_from_source_id}")
                else:
                    logger.warning(f"Source with ID {source_id} not found, skipping Neo4j save")
            except Exception as e:
                logger.error(f"Failed to save to Neo4j: {e}", exc_info=True)
        
        return note

    def _resolve_text_hash(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _count_words(self, content: str, title: str = '') -> int:
        """
        Count words in content only (excluding title/headline).
        
        Args:
            content: Main content text
            title: Optional title text (not counted)
            
        Returns:
            Word count in content only
        """
        if not content:
            return 0
        # Simple word count - split by whitespace (only content, not title)
        words = content.split()
        return len(words)
    
    def _format_processing_time(self, seconds: float) -> str:
        """
        Format processing time in a human-readable way.
        
        Args:
            seconds: Time in seconds (float)
            
        Returns:
            Human-readable time string (e.g., "2.5 seconds", "1 minute 23 seconds")
        """
        if seconds < 1:
            milliseconds = int(seconds * 1000)
            return f"{milliseconds} ms"
        elif seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            if secs < 1:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return f"{minutes} minute{'s' if minutes != 1 else ''} {secs:.1f} second{'s' if secs != 1 else ''}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            parts = [f"{hours} hour{'s' if hours != 1 else ''}"]
            if minutes > 0:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if secs > 0 and minutes == 0:  # Only show seconds if no minutes
                parts.append(f"{secs:.1f} second{'s' if secs != 1 else ''}")
            return " ".join(parts)
    
    def _print_processing_metadata(self, filename: str, word_count: int, elapsed_time: float, speed: float):
        """
        Print colored metadata block with processing information.
        
        Args:
            filename: Name of the processed file
            word_count: Number of words processed
            elapsed_time: Time taken in seconds
            speed: Words per second
        """
        # ANSI color codes
        RESET = '\033[0m'
        BOLD = '\033[1m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        
        time_str = self._format_processing_time(elapsed_time)
        speed_str = f"{speed:.1f} words/sec" if speed >= 1 else f"{speed * 1000:.0f} words/ms"
        
        # Create metadata block
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BOLD}{CYAN}📄 Processing Metadata{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{GREEN}File:{RESET}        {filename}")
        print(f"{YELLOW}Words:{RESET}        {word_count:,} words")
        print(f"{BLUE}Time:{RESET}         {time_str}")
        print(f"{MAGENTA}Speed:{RESET}       {speed_str}")
        print(f"{CYAN}{'='*60}{RESET}\n")

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
        logger.info(f"CSV exported to {file_path}")
