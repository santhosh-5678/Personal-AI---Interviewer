from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.interview import router as interview_router
from app.api.result import router as result_router
from app.database.database import init_database

app = FastAPI()
init_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router, prefix="/api")
app.include_router(result_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "AI Interview Agent Backend Running"}