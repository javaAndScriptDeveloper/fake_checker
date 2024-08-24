from telegram import Message

from core.core import CalculationUtils, EvaluationContext
from core.enums import PLATFORM_TYPE
from dal.dal import Note
from model.model import DataMessage


class NoteMapper:

    def mapEvaluationContext(evaluationContext: EvaluationContext):
        note = Note()
        note.content = evaluationContext.data
        note.source_id = evaluationContext.source_id
        note.sentimental_score = evaluationContext.sentimental_analysis_result
        note.triggered_keywords = evaluationContext.trigger_keywords_result
        note.text_simplicity_deviation = evaluationContext.text_simplicity_deviation
        note.confidence_factor = evaluationContext.confidence_factor
        note.triggered_topics = evaluationContext.trigger_topics_result
        note.clickbait = evaluationContext.clickbait_result
        note.subjective = evaluationContext.subjective_result
        note.call_to_action = evaluationContext.call_to_action_result
        note.repeated_take = evaluationContext.repeated_take_result
        note.repeated_note = evaluationContext.repeated_note_result
        note.total_score = CalculationUtils.calculate_total_score(note)
        return note


class ParserMapper:

    def mapTelegramMessage(message: Message):
        data_message = DataMessage()
        data_message.platform_type = PLATFORM_TYPE.TELEGRAM
        data_message.source_external_id = message.sender.id
        data_message.text_content = message.text if message.text is not None else ""
        return data_message
