from app.schemas.session import InterviewSession


# Temporary in-memory session storage
sessions = {}


def create_session(session_id: str) -> InterviewSession:
    session = InterviewSession(
        sessionId=session_id
    )

    sessions[session_id] = session

    return session


def get_session(session_id: str) -> InterviewSession | None:
    return sessions.get(session_id)


def save_session(session: InterviewSession) -> None:
    sessions[session.sessionId] = session


def delete_session(session_id: str) -> None:
    sessions.pop(session_id, None)