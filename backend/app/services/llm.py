import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

MODEL_NAME = "gemini-3.6-flash"


def generate_interview_response(conversation):
    try:
        print("Calling Gemini...")
        print("Model:", MODEL_NAME)
        print("Number of messages:", len(conversation))

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            max_tokens=500,
        )

        print("Gemini response received")

        return response.choices[0].message.content

    except Exception as e:
        print("====================================")
        print("GEMINI LLM ERROR:")
        print(repr(e))
        print("====================================")

        return "LLM_ERROR"