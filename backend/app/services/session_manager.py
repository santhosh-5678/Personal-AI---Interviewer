from app.schemas.session import InterviewSession
from app.database.database import (
    save_session_data,
    get_session_data,
    delete_session_data,
)


# =========================================================
# CREATE SESSION
# =========================================================

def create_session(session_id: str) -> InterviewSession:

    session = InterviewSession(
        sessionId=session_id
    )

    save_session_data(
        session_id,
        session.model_dump()
    )

    return session


# =========================================================
# GET SESSION
# =========================================================

def get_session(
    session_id: str
) -> InterviewSession | None:

    data = get_session_data(session_id)

    if data is None:
        return None

    return InterviewSession.model_validate(data)


# =========================================================
# SAVE SESSION
# =========================================================

def save_session(
    session: InterviewSession
) -> None:

    save_session_data(
        session.sessionId,
        session.model_dump()
    )


# =========================================================
# DELETE SESSION
# =========================================================

def delete_session(
    session_id: str
) -> None:

    delete_session_data(session_id)