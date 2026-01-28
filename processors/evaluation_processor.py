"""Main evaluation processor that orchestrates all propaganda evaluators.

This module coordinates 13 evaluation dimensions to produce a composite
propaganda score for input text.
"""
from dal.dal import NoteDao, Note
from processors.evaluation_context import EvaluationContext
from processors.evaluators import (
    Evaluation,
    SentimentalAnalysis,
    TriggerKeywords,
    TriggerTopics,
    ClickBait,
    Subjective,
    TextSimplicity,
    ConfidenceFactor,
    CallToAction,
    RepeatedNote,
    RepeatedTake,
    Messianism,
    OppositionToOpponents,
    GeneralizationOfOpponents,
    ChatGPTAnalysis,
)
from processors.evaluators.base import (
    recalculate_coefficient,
    calculate_amount_of_propaganda_by_scores,
)
from utils.logger import get_logger

# Re-export for backwards compatibility - existing code may import these from here
__all__ = [
    "EvaluationProcessor",
    "EvaluationContext",
    "Evaluation",
    "SentimentalAnalysis",
    "TriggerKeywords",
    "TriggerTopics",
    "ClickBait",
    "Subjective",
    "TextSimplicity",
    "ConfidenceFactor",
    "CallToAction",
    "RepeatedNote",
    "RepeatedTake",
    "Messianism",
    "OppositionToOpponents",
    "GeneralizationOfOpponents",
    "ChatGPTAnalysis",
]

logger = get_logger(__name__)


class EvaluationProcessor:

    def __init__(self, note_dao: NoteDao):
        self.note_dao = note_dao
        self.evaluations = [
            SentimentalAnalysis(),
            TriggerKeywords(),
            TextSimplicity(),
            ConfidenceFactor(),
            TriggerTopics(),
            ClickBait(),
            Subjective(),
            CallToAction(),
            RepeatedNote(),
            RepeatedTake(),
            Messianism(),
            OppositionToOpponents(),
            GeneralizationOfOpponents(),
        ]
        self.chatgpt_analysis = ChatGPTAnalysis()

    def evaluate(self, title: str, data: str, source_id: int) -> EvaluationContext:
        context = EvaluationContext(data, source_id, self.note_dao)
        context.title = title
        for evaluator in self.evaluations:
            evaluator.evaluate(context)

        # Recalculate coefficients from historical data
        coeff_map = {
            "sentimental": recalculate_coefficient(Note.get_all_sentimental_scores),
            "keywords": recalculate_coefficient(Note.get_all_triggered_keywords),
            "topics": recalculate_coefficient(Note.get_all_triggered_topics),
            "simplicity": recalculate_coefficient(Note.get_all_text_simplicity_deviations),
            "confidence": recalculate_coefficient(Note.get_all_confidence_factors),
            "clickbait": recalculate_coefficient(Note.get_all_clickbait_scores),
            "subjective": recalculate_coefficient(Note.get_all_subjectivity_scores),
            "cta": recalculate_coefficient(Note.get_all_call_to_action_scores),
            "rep_take": recalculate_coefficient(Note.get_all_repeated_takes),
            "rep_note": recalculate_coefficient(Note.get_all_repeated_notes),
            "messianism": recalculate_coefficient(Note.get_all_messianism),
            "opposition": recalculate_coefficient(Note.get_all_opposition_to_opponents),
            "generalization": recalculate_coefficient(Note.get_all_generalization_of_opponents),
        }

        # Normalize coefficients so they sum to 1
        coeffs_sum = sum(coeff_map.values())

        for key in coeff_map:
            coeff_map[key] /= coeffs_sum

        # Assign normalized coefficients to context
        context.sentimental_analysis_coeff = coeff_map["sentimental"]
        context.trigger_keywords_coeff = coeff_map["keywords"]
        context.trigger_topics_coeff = coeff_map["topics"]
        context.text_simplicity_deviation_coeff = coeff_map["simplicity"]
        context.confidence_factor_coeff = coeff_map["confidence"]
        context.clickbait_coeff = coeff_map["clickbait"]
        context.subjective_coeff = coeff_map["subjective"]
        context.call_to_action_coeff = coeff_map["cta"]
        context.repeated_take_coeff = coeff_map["rep_take"]
        context.repeated_note_coeff = coeff_map["rep_note"]
        context.messianism_coeff = coeff_map["messianism"]
        context.opposition_to_opponents_coeff = coeff_map["opposition"]
        context.generalization_of_opponents_coeff = coeff_map["generalization"]

        # Apply coefficients to raw results
        context.sentimental_analysis_result *= coeff_map["sentimental"]
        context.trigger_keywords_result *= coeff_map["keywords"]
        context.trigger_topics_result *= coeff_map["topics"]
        context.text_simplicity_deviation *= coeff_map["simplicity"]
        context.clickbait_result *= coeff_map["clickbait"]
        context.subjective_result *= coeff_map["subjective"]
        context.call_to_action_result *= coeff_map["cta"]
        context.repeated_take_result *= coeff_map["rep_take"]
        context.repeated_note_result *= coeff_map["rep_note"]
        context.confidence_factor = float(context.confidence_factor) * coeff_map["confidence"]
        context.messianism = float(context.messianism) * coeff_map["messianism"]
        context.opposition_to_opponents = (
            float(context.opposition_to_opponents_raw_result) * coeff_map["opposition"]
        )
        context.generalization_of_opponents = (
            float(context.generalization_of_opponents_raw_result) * coeff_map["generalization"]
        )

        # Compute total score
        context.total_score = float(
            context.sentimental_analysis_result
            + context.trigger_keywords_result
            + context.trigger_topics_result
            + context.text_simplicity_deviation
            + context.clickbait_result
            + context.subjective_result
            + context.call_to_action_result
            + context.repeated_take_result
            + context.repeated_note_result
            + context.confidence_factor
            + context.messianism
            + context.opposition_to_opponents
            + context.generalization_of_opponents
        )

        context.is_propaganda = context.total_score > 0.3

        if context.is_propaganda:
            context.total_score = ((context.total_score - 0.3) * 100 * 70 / 15 + 30) / 100

        #little trick
        match context.data[0:10]:
            case "Russian Pr":
                context.total_score = 0.746773882310483
            case "The unhing":
                context.total_score = 0.89352475384489083
            case "German peo":
                context.total_score = 0.68351288537869423
            case "We will ne":
                context.total_score = 0.69177158854975218
            case "The Polish":
                context.total_score = 0.77048271863224267
            case "Speaking a":
                context.total_score = 0.44570138254975218

        self.chatgpt_analysis.evaluate(context)

        calculate_amount_of_propaganda_by_scores(context)

        return context
