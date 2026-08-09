from fastapi import APIRouter

from app.schemas.interview import (
    InterviewRequest,
    InterviewResponse,
)

from app.services.session_manager import (
    create_session,
    get_session,
    save_session,
)

from app.services.llm import generate_interview_response


router = APIRouter()


SYSTEM_PROMPT = """
You are an AI Technical Interviewer conducting a structured
technical interview.

IMPORTANT CONTEXT RULES:

1. The conversation history is the source of truth for information
   explicitly provided by the candidate.

2. Never contradict information that the candidate has explicitly
   provided during the current interview session.

3. If the candidate provides a name, use that name for the rest
   of the interview.

4. Do not tell the candidate that their name or information is
   different from a candidate profile unless the interviewer
   explicitly needs to resolve an identity issue.

5. Never invent candidate information.

6. Candidate profile data provided by the backend is reference
   information only. Do not assume that every field is confirmed
   by the candidate.

7. If candidate information is missing, ask the candidate for it.
   Do not guess.

INTERVIEW FLOW:

8. Start with a normal conversational introduction.

9. Ask the candidate's name first.

10. After receiving the name, ask whether this is a good time
    to conduct the interview.

11. Collect candidate information one item at a time:
    - qualification
    - technical skills
    - experience
    - areas of expertise
    - project background

12. Ask exactly ONE question per response.

13. Never combine two questions into one response.

14. Do not start technical questions until the initial candidate
    information has been collected.

15. Ask the candidate to upload their resume.

16. After resume processing, use the resume information to
    personalize the technical interview.

TECHNICAL INTERVIEW:

17. Ask exactly 8 technical questions.

18. Questions must be based on the candidate's confirmed
    skills, experience, projects and resume.

19. Remember previous answers.

20. Use previous answers when asking follow-up questions.

21. If an answer is incorrect, remember the topic and continue
    the interview. Do not immediately reveal the evaluation.

22. Do not ask questions about technologies that have no evidence
    in the candidate's provided information unless clearly labeled
    as a general assessment question.

RESPONSE STYLE:

23. Keep responses concise and conversational.

24. Do not produce long explanations unless the candidate asks
    for clarification.

25. Never generate multiple questions at once.

26. Never invent facts about the candidate.

27. If there is conflicting information, prefer the information
    explicitly provided by the candidate during this session.

28. If information is uncertain, ask the candidate instead of
    guessing.
"""


def generate_ai_reply(conversation):

    return generate_interview_response(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *conversation,
        ]
    )


@router.post(
    "/interview",
    response_model=InterviewResponse,
)
async def interview(
    request: InterviewRequest,
):

    session_id = request.sessionId

    # ==========================================
    # GET OR CREATE SESSION
    # ==========================================

    session = get_session(session_id)

    if session is None:

        session = create_session(session_id)


    # ==========================================
    # FIRST REQUEST
    # ==========================================

    if request.candidate is not None:

        # Store candidate information
        session.stage = "GREETING"

        session.conversation = []


        # Add candidate information to context
        session.conversation.append(
            {
                "role": "user",
                "content": (
                    "Candidate profile:\n"
                    + request.candidate.model_dump_json(
                        indent=2
                    )
                ),
            }
        )


        # Ask the AI to begin naturally
        session.conversation.append(
            {
                "role": "user",
                "content": (
                    "Start the onboarding conversation. "
                    "Do not ask a technical question yet. "
                    "Begin with a simple greeting and ask "
                    "the candidate their name."
                ),
            }
        )


        ai_reply = generate_ai_reply(
            session.conversation
        )


        session.conversation.append(
            {
                "role": "assistant",
                "content": ai_reply,
            }
        )


        save_session(session)


        return {
            "reply": ai_reply,
            "done": False,
        }


    # ==========================================
    # CONTINUE CONVERSATION
    # ==========================================

    if request.message is not None:

        session.conversation.append(
            {
                "role": "user",
                "content": request.message,
            }
        )


        ai_reply = generate_ai_reply(
            session.conversation
        )


        session.conversation.append(
            {
                "role": "assistant",
                "content": ai_reply,
            }
        )


        save_session(session)


        return {
            "reply": ai_reply,
            "done": False,
        }


    # ==========================================
    # INVALID REQUEST
    # ==========================================

    return {
        "reply": "Invalid interview request.",
        "done": True,
    }