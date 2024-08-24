from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit

from core.enums import PLATFORM_TYPE
from core.singletons import evaluation_processor, note_dao, source_dao
from databridge.data_producer import DataProducer
from mapper.mapper import NoteMapper
from model.model import DataMessage, ProduceDataMessagesCommand


def post_extract_func(data_message: DataMessage):
    if(data_message.text_content == ""):
        return
    source = source_dao.get_by_external_id(data_message.source_external_id)
    context = evaluation_processor.evaluate(data_message.text_content, source.id)
    note = NoteMapper.mapEvaluationContext(context)
    note_dao.save(note)
    print(note)
    print(f"source rating = {source_dao.calculate_rating(source.id)}")

    response = {
        'id': source.id,
        'external_id': source.external_id,
        'platform': source.platform,
        'name': source.name,
        'rating': float(source_dao.calculate_rating(source.id))
    }
    emit('source_details', response, broadcast=True)

data_producer = DataProducer()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sources')
def get_all_sources():
    sources = source_dao.get_all()
    source_list = [{'id': source.id, 'name': source.name} for source in sources]
    return jsonify(source_list)

@socketio.on('add_source')
def handle_message(msg):
    produce_data_messages_command = ProduceDataMessagesCommand()
    produce_data_messages_command.platform_type = PLATFORM_TYPE.TELEGRAM
    source = source_dao.get_by_id(msg)
    produce_data_messages_command.sources_to_fetch = [source.name]
    produce_data_messages_command.post_extract_func = post_extract_func
    data_producer.produce(produce_data_messages_command)
