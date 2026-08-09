from app.services.llm import generate_interview_response


conversation = [
    {
        "role": "system",
        "content": "You are a technical interviewer."
    },
    {
        "role": "user",
        "content": "What is Python?"
    }
]


response = generate_interview_response(
    conversation
)


print("\nAI RESPONSE:\n")
print(response)
