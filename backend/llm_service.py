import logging
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

logger = logging.getLogger(__name__)


client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    default_headers={
        "Groq-Model-Version": "latest",
    },
)


GROQ_MODEL = "openai/gpt-oss-20b"
FALLBACK_MODEL = "groq/compound-mini"


def generate_groq_answer(
    prompt: str,
    context: str,
) -> str:

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful museum guide. "
                    "Answer questions using the provided Met Museum "
                    "artwork data. "
                    "Do not invent information that is not supported "
                    "by the provided data. "
                    "If the requested information is not available "
                    "in the provided data, say so."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"MET MUSEUM ARTWORK DATA:\n\n"
                    f"{context}\n\n"
                    f"QUESTION:\n{prompt}"
                ),
            },
        ],
    )

    return response.choices[0].message.content


def generate_compound_fallback(
    prompt: str,
    context: str,
) -> str:

    logger.info(
        "Groq Compound Mini fallback triggered"
    )

    response = client.chat.completions.create(
        model=FALLBACK_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a museum research assistant. "
                    "The primary Met Museum artwork data does not "
                    "contain enough information to answer the question. "
                    "\n\n"
                    "Use web search to find reliable information. "
                    "Prefer authoritative sources such as museum "
                    "websites, universities, museum foundations, "
                    "and reputable cultural institutions. "
                    "\n\n"
                    "If the user is asking a follow-up question about "
                    "an artwork in the provided Met Museum data, identify "
                    "the relevant artwork from that context before "
                    "searching. "
                    "\n\n"
                    "Do not invent information. "
                    "Clearly distinguish information from the provided "
                    "Met Museum data from information obtained through "
                    "web search."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"MET MUSEUM ARTWORK DATA:\n\n"
                    f"{context}\n\n"
                    f"QUESTION:\n{prompt}"
                ),
            },
        ],
        compound_custom={
            "tools": {
                "enabled_tools": [
                    "web_search",
                ]
            }
        },
    )

    answer = response.choices[0].message.content

    logger.info(
        "Compound fallback answer: %s",
        answer,
    )

    logger.info(
        "Groq Compound Mini fallback completed"
    )

    return answer


async def ask_llm(
    prompt: str,
    context: str,
) -> dict:

    answer = generate_groq_answer(
        prompt,
        context,
    )

    logger.info(
        "Groq answer: %s",
        answer,
    )

    normalized_answer = (
        answer.lower()
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )

    logger.info(
        "Normalized answer: %s",
        normalized_answer,
    )

    unknown = any(
        phrase in normalized_answer
        for phrase in [
            "not available",
            "isn't available",
            "don't have",
            "do not have",
            "does not include",
            "doesn't include",
            "isn't included",
            "is not included",
            "doesn't contain",
            "does not contain",
            "no information",
            "cannot answer",
            "can't answer",
        ]
    )

    logger.info(
        "Fallback trigger: unknown=%s",
        unknown,
    )

    if not unknown:

        return {
            "answer": answer,
            "context": context,
            "fallback_used": False,
        }

    logger.info(
        "Groq could not answer from Met context"
    )

    try:

        fallback_answer = generate_compound_fallback(
            prompt,
            context,
        )

        fallback_context = (
            f"{context}\n\n"
            "FALLBACK SOURCE:\n"
            "Groq Compound Mini web search"
        )

        return {
            "answer": fallback_answer,
            "context": fallback_context,
            "fallback_used": True,
        }

    except Exception:

        logger.exception(
            "Groq Compound Mini fallback failed"
        )

        return {
            "answer": answer,
            "context": context,
            "fallback_used": False,
        }