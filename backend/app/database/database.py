import sqlite3
import json
from pathlib import Path


# =========================================================
# DATABASE LOCATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_PATH = BASE_DIR / "interview.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE TABLES
# =========================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interview_sessions (
            session_id TEXT PRIMARY KEY,
            session_data TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


# =========================================================
# SAVE SESSION
# =========================================================

def save_session_data(
    session_id: str,
    session_data: dict,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO interview_sessions
        (session_id, session_data)
        VALUES (?, ?)
        """,
        (
            session_id,
            json.dumps(session_data),
        ),
    )

    connection.commit()

    connection.close()


# =========================================================
# GET SESSION
# =========================================================

def get_session_data(
    session_id: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT session_data
        FROM interview_sessions
        WHERE session_id = ?
        """,
        (session_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return json.loads(
        row["session_data"]
    )

def get_all_session_data():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT session_id, session_data
        FROM interview_sessions
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows

# =========================================================
# DELETE SESSION
# =========================================================

def delete_session_data(
    session_id: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM interview_sessions
        WHERE session_id = ?
        """,
        (session_id,),
    )

    connection.commit()

    connection.close()