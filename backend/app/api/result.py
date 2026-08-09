from fastapi import APIRouter
from app.services.session_manager import get_session

router = APIRouter()


@router.get("/result/{session_id}")
async def get_interview_result(session_id: str):

    session = get_session(session_id)

    if session is None:
        return {
            "error": "Session not found"
        }

    if not session.completed:
        return {
            "error": "Interview is not completed yet."
        }

    evaluations = session.evaluations

    total_questions = len(evaluations)

    if total_questions == 0:
        return {
            "error": "No evaluations found."
        }

    total_score = 0

    for item in evaluations:

        evaluation = item.get("evaluation", {})

        score = evaluation.get("score", 0)

        try:
            total_score += float(score)
        except (TypeError, ValueError):
            pass

    average_score = total_score / total_questions

    return {
        "sessionId": session.sessionId,
        "completed": session.completed,
        "totalQuestions": total_questions,
        "totalScore": total_score,
        "averageScore": round(average_score, 2),
        "evaluations": evaluations,
    }