"""Evaluation context that accumulates results from all evaluators."""


class EvaluationContext:

    def __init__(self, data, source_id, note_dao):
        self.data = data
        self.title = None
        self.source_id = source_id
        self.note_dao = note_dao

        self.sentimental_analysis_result = 0
        self.sentimental_analysis_raw_result = None
        self.sentimental_analysis_coeff = 1.0
        self.sentimental_analysis_execution_time = 0

        self.trigger_keywords_result = 0
        self.trigger_keywords_raw_result = None
        self.trigger_keywords_coeff = 1.0
        self.trigger_keywords_execution_time = 0

        self.trigger_topics_result = 0
        self.trigger_topics_raw_result = None
        self.trigger_topics_coeff = 1.0
        self.trigger_topics_execution_time = 0

        self.clickbait_result = 0
        self.clickbait_raw_result = None
        self.clickbait_coeff = 1.0
        self.clickbait_execution_time = 0

        self.subjective_result = 0
        self.subjective_raw_result = None
        self.subjective_coeff = 1.0
        self.subjective_execution_time = 0

        self.text_simplicity_deviation = 0
        self.text_simplicity_deviation_raw_result = None
        self.text_simplicity_deviation_coeff = 1.0
        self.text_simplicity_deviation_execution_time = 0

        self.confidence_factor = 100
        self.confidence_factor_raw_result = None
        self.confidence_factor_coeff = 1.0
        self.confidence_factor_execution_time = 100

        self.call_to_action_result = 0
        self.call_to_action_raw_result = None
        self.call_to_action_coeff = 1.0
        self.call_to_action_execution_time = 0

        self.repeated_take_result = 0
        self.repeated_take_raw_result = None
        self.repeated_take_coeff = 1.0
        self.repeated_take_execution_time = 0

        self.repeated_note_result = 0
        self.repeated_note_raw_result = None
        self.repeated_note_coeff = 1.0
        self.repeated_note_execution_time = 0

        self.messianism = 0
        self.messianism_raw_result = None
        self.messianism_coeff = 1.0
        self.messianism_execution_time = 0

        self.opposition_to_opponents = 0
        self.opposition_to_opponents_raw_result = None
        self.opposition_to_opponents_coeff = 1.0
        self.opposition_to_opponents_execution_time = 0

        self.generalization_of_opponents = 0
        self.generalization_of_opponents_raw_result = None
        self.generalization_of_opponents_coeff = 1.0
        self.generalization_of_opponents_execution_time = 0

        self.total_score = 0
        self.is_propaganda = False
        self.chatgpt_reason = None
        self.amount_of_propaganda_scores = None

    def __str__(self) -> str:
        return f'sentimental_analysis_result: {self.sentimental_analysis_result},\n' \
            + f'sentimental_analysis_execution_time: {self.sentimental_analysis_execution_time},\n' \
            + f'trigger_keywords_result: {self.trigger_keywords_result},\n' \
            + f'trigger_keywords_execution_time: {self.trigger_keywords_execution_time},\n' \
            + f'trigger_topics_result: {self.trigger_topics_result},\n' \
            + f'trigger_topics_execution_time: {self.trigger_topics_execution_time},\n' \
            + f'text_simplicity_deviation: {self.text_simplicity_deviation},\n' \
            + f'text_simplicity_deviation_execution_time: {self.text_simplicity_deviation_execution_time},\n' \
            + f'clickbait: {self.clickbait_result},\n' \
            + f'clickbait_execution_time: {self.clickbait_execution_time},\n' \
            + f'subjective: {self.subjective_result},\n' \
            + f'subjective_execution_time: {self.subjective_execution_time},\n' \
            + f'confidence_factor: {self.confidence_factor}' \
            + f'confidence_factor_execution_time: {self.confidence_factor_execution_time}' \
            + f'call_to_action: {self.call_to_action_result}' \
            + f'call_to_action_execution_time: {self.call_to_action_execution_time}' \
            + f'repeated_take: {self.repeated_take_result}' \
            + f'repeated_take_execution_time: {self.repeated_take_execution_time}' \
            + f'repeated_note: {self.repeated_note_result}' \
            + f'repeated_note_execution_time: {self.repeated_note_execution_time}'
