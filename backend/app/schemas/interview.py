from pydantic import BaseModel
from app.schemas.candidate import Candidate


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Candidate


class InterviewResponse(BaseModel):
    reply: str
    done: bool