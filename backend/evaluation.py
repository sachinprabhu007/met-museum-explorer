import logging
import os

from pydantic import BaseModel
from groq import Groq

from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase


logger = logging.getLogger(__name__)


class GroqEvaluationModel(DeepEvalBaseLLM):

    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.model_name = "openai/gpt-oss-20b"

    def load_model(self):
        return self.client

    def generate(
        self,
        prompt: str,
        schema: BaseModel | None = None,
    ):

        if schema:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return your response as valid JSON only. "
                            "Do not include markdown or any text outside JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                response_format={
                    "type": "json_object"
                },
                max_completion_tokens=2048,
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_completion_tokens=2048,
            )

        return response.choices[0].message.content

    async def a_generate(
        self,
        prompt: str,
        schema: BaseModel | None = None,
    ):
        return self.generate(prompt, schema)

    def get_model_name(self):
        return self.model_name


evaluation_model = GroqEvaluationModel()


def evaluate_museum_response(
    question: str,
    answer: str,
    context: str,
) -> None:

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=[context],
    )

    metric = AnswerRelevancyMetric(
        threshold=0.5,
        include_reason=True,
        model=evaluation_model,
    )

    metric.measure(test_case)

    logger.info(
        "DeepEval | metric=Answer Relevancy | score=%.3f | reason=%s",
        metric.score,
        metric.reason,
    )

    faithfulness = FaithfulnessMetric(
        threshold=0.5,
        include_reason=True,
        model=evaluation_model,
    )

    faithfulness.measure(test_case)

    logger.info(
        "DeepEval | metric=Faithfulness | score=%.3f | reason=%s",
        faithfulness.score,
        faithfulness.reason,
    )