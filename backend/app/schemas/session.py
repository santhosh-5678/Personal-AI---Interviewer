from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class CandidateDetails(BaseModel):
    name: Optional[str] = None
    qualification: Optional[str] = None
    skills: List[str] = []
    background: Optional[str] = None
    expertise: Optional[str] = None


class InterviewSession(BaseModel):
    sessionId: str

    stage: str = "GREETING"

    candidateDetails: CandidateDetails = CandidateDetails()

    resumeUploaded: bool = False
    resumeAnalyzed: bool = False

    resumeProfile: Dict[str, Any] = {}

    currentQuestion: int = 0
    totalQuestions: int = 8

    conversation: List[Dict[str, str]] = []

    evaluations: List[Dict[str, Any]] = []

    completed: bool = False