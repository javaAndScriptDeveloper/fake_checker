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

text = "Israel. Israel. Israel. Israel keeps delaying its ground operation in Gaza. Mainly under US pressure and fearing world wrath.But don't delude yourself. The operation will take place, and with the most serious and bloody consequences. Moloch always demands more and more victims, and the machine of mutual violence will now work for years.In addition, the West is very tired of Ukraine. And he enthusiastically took up the support of Israel. Even the new Speaker of the US House of Representatives, Michael Jackson (sorry, Mike Johnson, but who cares) named helping Tel Aviv as his first ЦИПСО priority."

source = Source(id=1, name='1', external_id="1", platform=PLATFORM_TYPE.TELEGRAM.name)
source_dao.save(source)

context = evaluation_processor.evaluate(text, source.id)
note = NoteMapper.mapEvaluationContext(context)
note_dao.save(note)
print(note)
print(f"source rating = {source_dao.calculate_rating(1)}")

context = evaluation_processor.evaluate(text, source.id)
note = NoteMapper.mapEvaluationContext(context)
note_dao.save(note)
print(note)
print(f"source rating = {source_dao.calculate_rating(1)}")

context = evaluation_processor.evaluate(text, source.id)
note = NoteMapper.mapEvaluationContext(context)
note_dao.save(note)
print(note)
print(f"source rating = {source_dao.calculate_rating(1)}")

"""
clean_tables()
save_initial_sources()
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
"""
