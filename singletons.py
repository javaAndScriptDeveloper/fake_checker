from manager import Manager
from processors.evaluation_processor import EvaluationProcessor
from dal.dal import NoteDao, SourceDao, Migration, initialize_database
from processors.fehner_processor import FehnerProcessor
from translation import Translator
from services.neo4j_service import Neo4jService

# Initialize database
initialize_database()

note_dao = NoteDao()
source_dao = SourceDao()
migration = Migration(note_dao, source_dao)
migration.execute()
evaluation_processor = EvaluationProcessor(note_dao)
fehner_processor = FehnerProcessor(note_dao)
translator = Translator()
neo4j_service = Neo4jService()
manager = Manager(evaluation_processor, note_dao, source_dao, fehner_processor, translator, neo4j_service)