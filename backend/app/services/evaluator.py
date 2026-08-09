import json

from app.services.llm import generate_interview_response


EVALUATION_PROMPT = """
You are an AI technical interview evaluator.

Evaluate the candidate's answer to a technical interview question.

Return ONLY valid JSON.

Do NOT use markdown.
Do NOT use ```json.
Do NOT add any explanation outside the JSON.

Use exactly this structure:

{
    "score": 0,
    "correct": true,
    "strengths": [],
    "weaknesses": [],
    "feedback": ""
}

Rules:

1. score must be an integer from 0 to 10.
2. correct must be true or false.
3. strengths must contain short points.
4. weaknesses must contain short points.
5. feedback must be concise.
6. Evaluate the candidate's answer against the interview question.
7. Do not invent information.
8. Do not judge grammar unless it affects technical clarity.
9. Focus on technical correctness, understanding, relevance, and depth.
10. If the candidate's answer does not answer the question, reflect that in the score and weaknesses.
"""


def evaluate_answer(question, answer):

    conversation = [
        {
            "role": "system",
            "content": EVALUATION_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"Interview Question:\n{question}\n\n"
                f"Candidate Answer:\n{answer}"
            ),
        },
    ]

    result = generate_interview_response(conversation)

    # Remove markdown code fences if the model still returns them
    result = result.strip()

    if result.startswith("```json"):
        result = result[7:]

    elif result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    # Convert JSON string into Python dictionary
    try:
        evaluation = json.loads(result)

        return evaluation

    except json.JSONDecodeError:

        return {
            "score": 0,
            "correct": False,
            "strengths": [],
            "weaknesses": [
                "Unable to parse evaluator response."
            ],
            "feedback": "Evaluation could not be processed.",
        }