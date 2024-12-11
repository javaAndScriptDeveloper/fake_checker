from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit, send

from controller import app, socketio
from core.enums import PLATFORM_TYPE
from core.singletons import evaluation_processor, note_dao, source_dao
from dal.dal import Note, NoteDao, Source
from dal.migrations import clean_tables, save_initial_sources
from databridge.data_producer import DataProducer, ProduceDataMessagesCommand
from mapper.mapper import NoteMapper
from model.model import DataMessage

def read_file_to_variable(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()  # Read the entire file content
    return file_contents

#text = read_file_to_variable("data/putler.txt")

source = Source(id=1, name='1', external_id="1", platform=PLATFORM_TYPE.TELEGRAM.name)
source_dao.save(source)

source = Source(id=2, name='2', external_id="2", platform=PLATFORM_TYPE.TELEGRAM.name)
source_dao.save(source)

"""
context = evaluation_processor.evaluate(text, source.id)
note = NoteMapper.mapEvaluationContext(context)
note_dao.save(note)
"""
#print(note)
#print(f"source rating = {source_dao.calculate_rating(1)}")

def process(text, source_id):
    context = evaluation_processor.evaluate(text, source_id)
    note, calculation_object = NoteMapper.mapEvaluationContext(context)
    note_dao.save(note)
    calculation_object['is_propaganda'] = note.total_score > note_dao.get_average_rating()
    return note, calculation_object

def get_sources_with_ratings():
    sources = source_dao.get_all()
    source_ratings = {}
    for i in sources:
        notes = note_dao.get_by_source_id(i.id)
        if(notes):
            total_scores = [note.total_score for note in notes]
            rating = sum(total_scores) / len(total_scores)
            source_ratings[i] = rating
    return source_ratings
