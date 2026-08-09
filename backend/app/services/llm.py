import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not configured in .env"
    )


client = Groq(
    api_key=GROQ_API_KEY
)


MODEL_NAME = "llama-3.3-70b-versatile"


def generate_interview_response(
    conversation
):

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=conversation,

        temperature=0.7,

        max_tokens=500,
    )

    return response.choices[0].message.content