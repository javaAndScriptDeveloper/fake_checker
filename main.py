from controller import app, socketio
from core.singletons import source_dao, note_dao, evaluation_processor
from dal.dal import Source, Note, NoteDao
from core.enums import PLATFORM_TYPE
from dal.migrations import save_initial_sources, clean_tables
from databridge.data_producer import DataProducer, ProduceDataMessagesCommand
from mapper.mapper import NoteMapper
from model.model import DataMessage
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, send, emit

from core.singletons import source_dao

text = "Israel keeps delaying its ground operation in Gaza. Mainly under US pressure and fearing world wrath.But don't delude yourself. The operation will take place, and with the most serious and bloody consequences. Moloch always demands more and more victims, and the machine of mutual violence will now work for years.In addition, the West is very tired of Ukraine. And he enthusiastically took up the support of Israel. Even the new Speaker of the US House of Representatives, Michael Jackson (sorry, Mike Johnson, but who cares) named helping Tel Aviv as his first ЦИПСО priority."

source = Source(id = 1, name='1', external_id = "1", platform=PLATFORM_TYPE.TELEGRAM.name)
source_dao.save(source)

context = evaluation_processor.evaluate(text, source.id)
note = NoteMapper.mapEvaluationContext(context)
note_dao.save(note)
print(note)
print(f"source rating = {source_dao.calculate_rating(1)}")

context = evaluation_processor.evaluate(text, source)
note = NoteMapper.mapEvaluationContext(context)
note_dao.save(note)
print(note)
print(f"source rating = {source_dao.calculate_rating(1)}")

context = evaluation_processor.evaluate(text, source)
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
