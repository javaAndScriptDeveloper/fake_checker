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

def get_sources():
    return [Source(id=1, name='1', external_id="1", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=2, name='2', external_id="2", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=3, name='3', external_id="3", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=4, name='4', external_id="4", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=5, name='5', external_id="5", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=6, name='6', external_id="6", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=7, name='7', external_id="7", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=8, name='8', external_id="8", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=9, name='9', external_id="9", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=10, name='10', external_id="10", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=11, name='11', external_id="11", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=12, name='12', external_id="12", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=13, name='13', external_id="13", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=14, name='14', external_id="14", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=15, name='15', external_id="15", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=16, name='16', external_id="16", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=17, name='17', external_id="17", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=18, name='18', external_id="18", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=19, name='19', external_id="19", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=20, name='20', external_id="20", platform=PLATFORM_TYPE.TELEGRAM.name),
            Source(id=21, name='CNN NEWS', external_id="21", platform=PLATFORM_TYPE.TWITCH.name),
            Source(id=22, name='FOX NEWS', external_id="21", platform=PLATFORM_TYPE.TWITCH.name),
            Source(id=23, name='NY NEWS', external_id="21", platform=PLATFORM_TYPE.TWITCH.name),
            Source(id=24, name='THE GUARDIAN NEWS', external_id="21", platform=PLATFORM_TYPE.TWITCH.name),
            Source(id=25, name='SUN NEWS', external_id="21", platform=PLATFORM_TYPE.TWITCH.name)
            ]

sources = get_sources()
for i in sources:
    source_dao.save(i)

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
