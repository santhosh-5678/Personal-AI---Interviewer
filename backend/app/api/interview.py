from fastapi import APIRouter
from app.schemas.interview import InterviewRequest, InterviewResponse

router = APIRouter()


@router.post("/interview", response_model=InterviewResponse)
def start_interview(request: InterviewRequest):
    return InterviewResponse(
        reply="Welcome. Let's begin your interview.",
        done=False
    )