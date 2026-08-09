from fastapi import APIRouter

from app.schemas.interview import (
    InterviewRequest,
    InterviewResponse,
)

from app.services.llm import generate_interview_response


router = APIRouter()


# Stores interview conversations in memory.
# Key = sessionId
# Value = list of messages
interview_sessions = {}


SYSTEM_PROMPT = """
You are an AI technical interviewer.

You are conducting a chat-based technical interview.

Your job is to:

1. Ask technical interview questions.
2. Use the candidate's background to personalize questions.
3. Keep questions relevant to the candidate's role.
4. Ask one question at a time.
5. Ask follow-up questions when appropriate.
6. Keep responses concise and conversational.
7. Do not conduct a voice interview.
8. Do not generate multiple questions at once.
9. Evaluate the candidate's answer before deciding what to ask next.
10. Adapt the difficulty based on the candidate's answer.

The interview should feel like a real technical interview.

This is a CHAT-BASED interview only.
Do not use voice interaction.
"""


@router.post(
    "/interview",
    response_model=InterviewResponse,
)
async def interview(
    request: InterviewRequest,
):

    session_id = request.sessionId


    # =========================================
    # START NEW INTERVIEW
    # =========================================

    if request.candidate is not None:

        conversation = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },

            {
                "role": "user",
                "content": f"""
Candidate information:

{request.candidate.model_dump_json(indent=2)}

Start the technical interview.

Begin with a short welcome message and then ask the first technical question.
""",
            },

        ]


        # Generate first AI response

        ai_reply = generate_interview_response(
            conversation
        )


        # Save conversation

        conversation.append(
            {
                "role": "assistant",
                "content": ai_reply,
            }
        )


        interview_sessions[session_id] = conversation


        return {
            "reply": ai_reply,
            "done": False,
        }


    # =========================================
    # CONTINUE EXISTING INTERVIEW
    # =========================================

    if request.message is not None:

        conversation = interview_sessions.get(
            session_id
        )


        if conversation is None:

            return {
                "reply": "Interview session not found. Please start a new interview.",
                "done": True,
            }


        # Add candidate answer

        conversation.append(
            {
                "role": "user",
                "content": request.message,
            }
        )


        # Generate next AI response

        ai_reply = generate_interview_response(
            conversation
        )


        # Save AI response

        conversation.append(
            {
                "role": "assistant",
                "content": ai_reply,
            }
        )


        return {
            "reply": ai_reply,
            "done": False,
        }


    # =========================================
    # INVALID REQUEST
    # =========================================

    return {
        "reply": "Invalid interview request.",
        "done": True,
    }