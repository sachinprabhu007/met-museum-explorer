import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


async def ask_llm(
    prompt: str,
    context: str,
) -> str:

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful museum guide. "
                    "Answer questions using the provided Met Museum "
                    "artwork data. Do not invent information that is "
                    "not supported by the provided data. "
                    "If the requested information is not available "
                    "in the data, say so."
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