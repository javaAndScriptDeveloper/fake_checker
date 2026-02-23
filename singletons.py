from manager import Manager
from processors.evaluation_processor import EvaluationProcessor
from dal.dal import NoteDao, SourceDao, AudioMetadataDao, Migration, initialize_database
from processors.fehner_processor import FehnerProcessor
from translation import Translator
from services.neo4j_service import Neo4jService
from services.audio_service import AudioService
from config.config import config

# Initialize database
initialize_database()

note_dao = NoteDao()
source_dao = SourceDao()
audio_metadata_dao = AudioMetadataDao()
migration = Migration(note_dao, source_dao)
migration.execute()
evaluation_processor = EvaluationProcessor(note_dao)
fehner_processor = FehnerProcessor(note_dao)
translator = Translator()
neo4j_service = Neo4jService()

# Initialize audio service (lazy loading of Whisper model)
audio_service = AudioService(
    model_size=config.audio_config['whisper_model_size'],
    max_file_size_mb=config.audio_config['max_file_size_mb'],
    max_duration_minutes=config.audio_config['max_duration_minutes'],
    device=config.audio_config['device']
)

manager = Manager(
    evaluation_processor,
    note_dao,
    source_dao,
    fehner_processor,
    translator,
    neo4j_service,
    audio_metadata_dao
)