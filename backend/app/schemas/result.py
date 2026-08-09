from typing import List, Dict, Any

from pydantic import BaseModel


class InterviewResult(BaseModel):
    sessionId: str

    totalQuestions: int
    answeredQuestions: int

    totalScore: int
    averageScore: float

    correctAnswers: int
    incorrectAnswers: int

    result: str

    evaluations: List[Dict[str, Any]]