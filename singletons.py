from manager import Manager
from processors.evaluation_processor import EvaluationProcessor
from dal.dal import NoteDao, SourceDao, Migration
from processors.fehner_processor import FehnerProcessor

note_dao = NoteDao()
source_dao = SourceDao()
migration = Migration(note_dao, source_dao)
migration.execute()
evaluation_processor = EvaluationProcessor(note_dao)
fehner_processor = FehnerProcessor(note_dao)
manager = Manager(evaluation_processor, note_dao, source_dao, fehner_processor)