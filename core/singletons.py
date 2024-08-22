from core.core import EvaluationProcessor
from dal.dal import NoteDao, SourceDao

source_dao = SourceDao()
note_dao = NoteDao()
evaluation_processor = EvaluationProcessor(note_dao)