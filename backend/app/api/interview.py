import json
from pathlib import Path
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
from app.services.evaluator import evaluate_answer
from app.services.candidate_service import get_candidate


router = APIRouter()

def get_candidate_missions(candidate):
    """
    Extract completed missions from the candidate profile.
    """

    if candidate is None:
        return []

    candidate_data = (
        candidate
        if isinstance(candidate, dict)
        else candidate.model_dump()
    )

    return candidate_data.get("missions", [])

# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are an AI Technical Interviewer conducting a structured
personalized technical interview.

The backend provides a candidate profile before the interview
starts.

The candidate profile may contain information such as:

- name
- role
- years of experience
- education
- technical skills
- projects
- previous experience
- areas of expertise
- other relevant background

IMPORTANT CANDIDATE PROFILE RULES
---------------------------------

1. Treat the candidate profile provided by the backend as the
   primary reference for constructing the interview.

2. Do NOT ask the candidate for information that is already clearly
   available in the candidate profile.

3. Do NOT ask the candidate to provide their name if their name is
   already available in the candidate profile.

4. Do NOT ask the candidate to upload a resume.

5. The candidate profile replaces the need for resume upload during
   this interview.

6. Never invent information that is not present in the candidate
   profile or conversation.

7. If some information is missing or ambiguous and that information
   is important for the interview, you may ask the candidate for
   clarification.

8. Candidate answers during the conversation should take priority
   over assumptions made from the candidate profile.

9. If the candidate corrects something from the profile, use the
   candidate's correction for the rest of the interview.

10. Do not repeatedly ask for information that has already been
    established.

INTERVIEW START
---------------

11. When the interview begins, greet the candidate using their name
    from the candidate profile.

12. Mention the role when useful.

13. Do NOT ask for the candidate's name.

14. Do NOT ask whether the candidate wants to upload a resume.

15. Do NOT start by asking generic onboarding questions.

16. Start naturally with a short personalized introduction.

17. After the introduction, ask ONE appropriate background or
    clarification question only if it is useful for understanding
    the candidate's experience.

18. If the candidate profile already contains sufficient background
    information, move toward the technical interview without
    unnecessary onboarding questions.

QUESTION RULES
--------------

19. Ask exactly ONE question per response.

20. Never combine multiple questions into one response.

21. Keep questions directly related to the candidate's profile.

22. Do not ask about technologies that have no evidence in the
    candidate profile unless the question is explicitly intended
    as a general assessment question.

23. Use the candidate's role, skills, experience and projects when
    creating questions.

TECHNICAL INTERVIEW
-------------------

24. Conduct exactly 8 technical questions.

25. Keep track of the technical question number internally.

26. The technical questions should become progressively more
    challenging when appropriate.

27. Questions should be personalized to the candidate.

28. Use the candidate's confirmed skills, experience and projects
    as the main source for technical questions.

29. Use previous answers to create relevant follow-up questions.

30. Do not repeat the same question.

31. Do not ask multiple technical questions in one response.

32. After the eighth technical question has been answered, end the
    technical interview.

33. Do not ask a ninth technical question.

34. After question 8, provide a concise closing message.

ANSWER EVALUATION
-----------------

35. Evaluate answers internally.

36. Do not reveal the complete evaluation after every question.

37. If an answer is incorrect, continue the interview naturally.

38. You may use the candidate's previous answer to create a useful
    follow-up question.

39. Do not unnecessarily tell the candidate whether every answer
    is correct or incorrect.

RESPONSE STYLE
--------------

40. Keep responses concise and conversational.

41. Avoid long explanations unless the candidate asks for
    clarification.

42. Never generate multiple questions at once.

43. Never invent candidate facts.

44. Never ask unnecessary onboarding questions.

45. Never ask for a resume upload.

46. Maintain a professional interviewer tone.

INTERVIEW OBJECTIVE
-------------------

The goal is to assess the candidate's technical ability based on
the candidate information already provided by the backend.

The interview should feel like a real personalized technical
interview rather than a generic chatbot conversation.
"""


# =========================================================
# GET LAST QUESTION
# =========================================================

def get_last_question(conversation):

    for message in reversed(conversation):

        if message["role"] == "assistant":
            return message["content"]

    return ""

def generate_ai_reply(
    conversation,
    question_number=None,
    candidate_missions=None,
):

    question_context = ""

    if question_number is not None:

        question_context = f"""

CURRENT INTERVIEW STATE
-----------------------

You are currently conducting technical question
{question_number} of 8.

IMPORTANT:

- Ask exactly ONE technical question.
- Do not skip this question number.
- Do not ask a previous question again.
- Do not ask question 9.

CANDIDATE'S COMPLETED MISSIONS
------------------------------

{json.dumps(candidate_missions or [], indent=2)}

QUESTION SELECTION RULES
------------------------

- Generate the question ONLY from the candidate's completed
  missions, skills, expertise, or explicitly provided technical
  information.
- Prefer topics from the candidate's completed missions.
- Do not introduce unrelated technologies or concepts.
- Do not randomly choose a machine learning topic.
- If the candidate has completed a mission about Embeddings,
  questions may focus on embeddings.
- If the candidate has completed a mission about Vector Databases,
  questions may focus on vector databases.
- If the candidate has completed a mission about RAG,
  questions may focus on RAG.
- Use the candidate's previous answers to increase difficulty
  or ask a relevant follow-up.
- Do not repeat a previously asked question.
"""

    return generate_interview_response(
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT + question_context,
            },
            *conversation,
        ]
    )

# =========================================================
# INTERVIEW ENDPOINT
# =========================================================

@router.post(
    "/interview",
    response_model=InterviewResponse,
)
async def interview(
    request: InterviewRequest,
):

    session_id = request.sessionId

    print("SESSION ID:", request.sessionId)
    print("MESSAGE:", request.message)
    print("CANDIDATE ID:", request.candidateId)

    session = get_session(session_id)


    # =====================================================
    # CREATE NEW SESSION
    # =====================================================

    if session is None:
        candidate = get_candidate(request.candidateId)

        if candidate is None:

            return {
                "reply": (
                    "Candidate not found. Please provide a valid "
                    "candidateId."
                ),
                "done": True,
            }

        session = create_session(session_id)

        session.stage = "GREETING"
        session.conversation = []

        session.candidateDetails = candidate["member"]

        candidate_missions = get_candidate_missions(
            candidate
        )

        session.missions = candidate_missions

        # -------------------------------------------------
        # STORE CANDIDATE PROFILE
        # -------------------------------------------------

        session.conversation.append(
            {
                "role": "user",
                "content": (
                    "Candidate profile:\n"
                    + json.dumps(candidate, indent=2)
                ),
            }
        )

        # -------------------------------------------------
        # START INTERVIEW
        # -------------------------------------------------

        session.conversation.append(
        {
            "role": "user",
            "content": (
                "Start the technical interview using the "
                "candidate profile. Greet the candidate briefly "
                "by name and mention their role when appropriate. "
                "After the greeting, immediately ask Technical "
                "Question 1. "
                "Do not ask a background question. "
                "Do not ask for information already available "
                "in the candidate profile. "
                "The first question must be a technical question "
                "based on the candidate's skills, experience, "
                "missions, or expertise."
            ),
        }
    )

        # -------------------------------------------------
        # FIRST TECHNICAL QUESTION
        # -------------------------------------------------

        session.currentQuestion = 1
        session.stage = "TECHNICAL"

        ai_reply = generate_ai_reply(
            session.conversation,
            session.currentQuestion,
            candidate_missions,
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


    # =====================================================
    # CHECK COMPLETED SESSION
    # =====================================================

    if session.completed:

        return {
            "reply": "The interview has already been completed.",
            "done": True,
        }

    if request.message:

        question = get_last_question(
            session.conversation
        )

        if not question:
            return {
                "reply": "Unable to determine the current interview question.",
                "done": True,
            }

        answer = request.message

        # -------------------------------------------------
        # STORE CANDIDATE ANSWER
        # -------------------------------------------------

        session.conversation.append(
            {
                "role": "user",
                "content": answer,
            }
        )

        # -------------------------------------------------
        # EVALUATE ANSWER
        # -------------------------------------------------

        evaluation = evaluate_answer(
            question,
            answer,
        )

        # -------------------------------------------------
        # STORE EVALUATION
        # -------------------------------------------------

        session.evaluations.append(
            {
                "questionNumber": session.currentQuestion,
                "question": question,
                "answer": answer,
                "evaluation": evaluation,
            }
        )

        # -------------------------------------------------
        # CHECK IF Q8 WAS ANSWERED
        # -------------------------------------------------

        if session.currentQuestion >= session.totalQuestions:

            session.completed = True
            session.stage = "COMPLETED"

            save_session(session)

            return {
                "reply": (
                    "Thank you. That completes the "
                    "technical interview. We appreciate your "
                    "time and thoughtful responses."
                ),
                "done": True,
            }

        # -------------------------------------------------
        # MOVE TO NEXT QUESTION
        # -------------------------------------------------

        session.currentQuestion += 1

        # -------------------------------------------------
        # GENERATE NEXT QUESTION
        # -------------------------------------------------

        ai_reply = generate_ai_reply(
            session.conversation,
            session.currentQuestion,
            session.missions,
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


    # =====================================================
    # INVALID REQUEST
    # =====================================================

    return {
        "reply": "Invalid interview request.",
        "done": True,
    }


# =========================================================
# GET INTERVIEW SESSION
# =========================================================

@router.get(
    "/interview/{session_id}"
)
async def get_interview_session(
    session_id: str,
):

    session = get_session(session_id)

    if session is None:

        return {
            "error": "Session not found"
        }

    return {
        "sessionId": session.sessionId,
        "stage": session.stage,
        "currentQuestion": session.currentQuestion,
        "totalQuestions": session.totalQuestions,
        "completed": session.completed,
        "conversation": session.conversation,
        "evaluations": session.evaluations,
    }
