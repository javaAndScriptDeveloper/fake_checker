"""ChatGPT-based propaganda analysis evaluator."""
import time

from config.config import config
from processors.evaluation_context import EvaluationContext
from processors.evaluators.base import Evaluation
from utils.logger import get_logger

logger = get_logger(__name__)


class ChatGPTAnalysis(Evaluation):

    def __init__(self):
        self.client = None
        self.is_enabled = config.is_chatgpt_processor_enabled

        if self.is_enabled and config.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=config.openai_api_key)
                logger.info("ChatGPT processor initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ChatGPT processor: {e}", exc_info=True)
                self.is_enabled = False
        else:
            logger.info("ChatGPT processor disabled or API key not provided")

    def should_process(self, evaluation_context: EvaluationContext) -> bool:
        """Determine if the content should be processed by ChatGPT.
        Only process if total_score > 0.3 and processor is enabled.
        """
        return (self.is_enabled and
                self.client is not None and
                evaluation_context.total_score > 0.3)

    def analyze_propaganda(self, evaluation_context: EvaluationContext) -> str:
        """Analyze the content using ChatGPT to explain why it might be propaganda.
        Returns the explanation or empty string if analysis fails.
        """
        if self.client is None:
            return ""

        try:
            start_time = time.perf_counter()

            prompt = self._create_analysis_prompt(evaluation_context.data)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in media analysis and propaganda detection. Provide clear, objective explanations of why content might be considered propaganda."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )

            explanation = response.choices[0].message.content.strip()

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            logger.info(f"ChatGPT analysis completed in {execution_time:.2f}s")

            return explanation

        except Exception as e:
            logger.error(f"ChatGPT analysis failed: {e}", exc_info=True)
            return ""

    def _create_analysis_prompt(self, content: str) -> str:
        """Create a focused prompt for ChatGPT to analyze propaganda content."""
        return f"""
Analyze the following text content whether it is propaganda.
Focus on identifying specific propaganda techniques, biased language, emotional manipulation,
or misleading information. Provide a clear, concise explanation (2-3 sentences) in the Ukrainian language.

Text to analyze:
"{content}"
"""

    def evaluate(self, evaluation_context: EvaluationContext):
        """Evaluate the content using ChatGPT analysis if conditions are met."""
        if self.should_process(evaluation_context):
            evaluation_context.chatgpt_reason = self.analyze_propaganda(evaluation_context)
        else:
            evaluation_context.chatgpt_reason = None
