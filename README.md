# Personal AI Interview

Personal AI Interview is a full-stack application that runs structured, personalized technical interviews. A candidate is selected in the React interface, the backend uses the candidate's profile and completed learning missions to generate questions, evaluates answers, and stores the complete interview session and results.

## Features

- Candidate selection from local JSON data
- Personalized, eight-question technical interview flow
- One question per turn, with questions based on candidate missions and profile
- AI-generated answer evaluation with scores, strengths, weaknesses, and feedback
- Persistent interview sessions and final scores in SQLite
- Markdown rendering for AI responses in the chat interface

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | React 19, Vite, Axios, React Markdown |
| Backend | Python, FastAPI, Pydantic |
| Database | SQLite |
| AI provider | Google Gemini through the OpenAI-compatible SDK (`gemini-3.6-flash`) |
| Candidate data | JSON |

## Architecture

```text
React + Vite frontend
        |
        | HTTP requests via Axios
        v
FastAPI backend
  |-- Candidate service -> backend/data/candidates.json
  |-- Interview service -> Gemini API
  |-- Evaluator -> Gemini API
  `-- Session manager -> SQLite (backend/interview.db)
```

## Project structure

```text
.
|-- frontend/
|   |-- public/data/candidates.json  # Candidate data used by the UI
|   `-- src/
|       |-- App.jsx                  # Interview UI and API calls
|       `-- services/api.js          # Axios API client
`-- backend/
    |-- app/
    |   |-- api/                     # Interview and result endpoints
    |   |-- database/                # SQLite persistence
    |   |-- schemas/                 # Pydantic request/session models
    |   `-- services/                # Candidate, LLM, evaluator, session services
    |-- data/candidates.json         # Backend candidate source of truth
    `-- requirements.txt
```

## How the interview works

1. The frontend loads candidates from `frontend/public/data/candidates.json`.
2. Selecting a candidate creates a new UUID session ID.
3. The frontend starts an interview using the selected candidate's `member.id` as `candidateId`.
4. The backend loads the matching profile from `backend/data/candidates.json`, creates a session, and stores it in SQLite.
5. The LLM receives the candidate profile, completed missions, interview rules, and conversation history. It generates one technical question.
6. Each candidate answer is saved, evaluated by the LLM, and used as context for the next question.
7. After eight answers, the backend marks the session complete.
8. The result endpoint returns all evaluations plus total and average scores.

## Prerequisites

- Python 3.11 (configured in `backend/.python-version`)
- Node.js 18 or newer
- npm
- A Gemini API key

## Run locally

### 1. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create `backend/.env` before starting the backend:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The backend starts at `http://localhost:8000` and initializes `backend/interview.db` automatically. The `.env` file is ignored by Git and must not be committed.

### 2. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

The FastAPI CORS configuration permits the Vite development origin at `http://localhost:5173`.

## API

### Start or continue an interview

`POST /api/interview`

Request body:

```json
{
  "sessionId": "8ea2c7e5-8e6b-4c64-a9d0-83f85235c233",
  "candidateId": "CAND-001",
  "message": ""
}
```

- A new `sessionId` starts an interview and returns the first AI question.
- For later turns, send the same `sessionId` and `candidateId` with the candidate's answer in `message`.

Response:

```json
{
  "reply": "...",
  "done": false
}
```

### Read an interview session

`GET /api/interview/{session_id}`

Returns the current stage, conversation, question count, and stored evaluations.

### Read completed results

`GET /api/result/{session_id}`

Returns the final question count, total score, average score, and per-question evaluations after the interview is complete.

## Data model

Each candidate has a stable identifier at `candidate.member.id`, for example `CAND-001`. The frontend sends this ID only; it does not send the complete candidate object to the backend.

The backend stores a serialized session in SQLite, including the conversation, completed missions, current question number, and evaluations.

## Development commands

```powershell
# Frontend production build
cd frontend
npm run build

# Frontend lint
npm run lint

# Backend syntax check
cd backend
python -m compileall -q app
```

## Notes

- AI responses support Markdown in the frontend; candidate messages are shown as plain text.
- Sessions are stored locally in `backend/interview.db`.
- The current CORS configuration is intended for local Vite development.
- The backend uses only `fastapi`, `uvicorn`, `pydantic`, `openai`, and `python-dotenv` at runtime; it no longer requires PyTorch or Hugging Face Transformers.
