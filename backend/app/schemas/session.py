from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class CandidateDetails(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    jobRole: Optional[str] = None
    yearsExperience: Optional[int] = None
    education: Optional[str] = None
    status: Optional[str] = None


class InterviewSession(BaseModel):
    sessionId: str

    stage: str = "GREETING"

    candidateDetails: CandidateDetails = Field(
        default_factory=CandidateDetails
    )

    resumeUploaded: bool = False
    resumeAnalyzed: bool = False

    resumeProfile: Dict[str, Any] = Field(
        default_factory=dict
    )

    missions: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    currentQuestion: int = 0
    totalQuestions: int = 8

    conversation: List[Dict[str, str]] = Field(
        default_factory=list
    )

    evaluations: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    completed: bool = False