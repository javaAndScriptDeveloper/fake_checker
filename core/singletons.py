from core.core import EvaluationProcessor
from dal.dal import NoteDao, SourceDao
from fehner_processor import FehnerProcessor

source_dao = SourceDao()
note_dao = NoteDao()
evaluation_processor = EvaluationProcessor(note_dao)
fehner_processor = FehnerProcessor(note_dao)