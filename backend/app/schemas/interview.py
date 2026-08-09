from typing import Optional
from pydantic import BaseModel

class InterviewRequest(BaseModel):
    sessionId: str
    candidateId: str
    message: Optional[str] = ""


class InterviewResponse(BaseModel):
    reply: str
    done: bool
