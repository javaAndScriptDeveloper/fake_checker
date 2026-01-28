"""Evaluator modules for propaganda detection.

Each evaluator implements a specific dimension of propaganda analysis.
"""
from processors.evaluators.base import Evaluation
from processors.evaluators.sentiment import SentimentalAnalysis
from processors.evaluators.trigger_keywords import TriggerKeywords
from processors.evaluators.trigger_topics import TriggerTopics
from processors.evaluators.clickbait import ClickBait
from processors.evaluators.subjective import Subjective
from processors.evaluators.text_simplicity import TextSimplicity
from processors.evaluators.confidence_factor import ConfidenceFactor
from processors.evaluators.call_to_action import CallToAction
from processors.evaluators.repeated_note import RepeatedNote
from processors.evaluators.repeated_take import RepeatedTake
from processors.evaluators.messianism import Messianism
from processors.evaluators.opposition import OppositionToOpponents
from processors.evaluators.generalization import GeneralizationOfOpponents
from processors.evaluators.chatgpt import ChatGPTAnalysis

__all__ = [
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
