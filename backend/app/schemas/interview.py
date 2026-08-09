from typing import Optional

from pydantic import BaseModel

from app.schemas.candidate import Candidate


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[Candidate] = None
    message: Optional[str] = None


class InterviewResponse(BaseModel):
    reply: str
    done: bool